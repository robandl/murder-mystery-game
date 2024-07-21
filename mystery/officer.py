import math
from collections import deque
from enum import Enum, auto
from pathlib import Path

from chat_box import ChatBox
from judge import Judge
from npc import NPC, LlmNPC
from player import Player
from room import Room
from state import State
from utils import Point2D, RoomName
from walker import Walker


def bfs_shortest_path(graph, start, target):
    """breadth-first search to find the shortest path from start to target by ChatGPT"""
    # A queue to store the paths
    queue = deque([[start]])
    # A set to store visited nodes
    visited = set()
    while queue:
        # Get the first path from the queue
        path = queue.popleft()
        # Get the last node from the path
        node = path[-1]
        # If the node is the target, return the path
        if node == target:
            return path
        # If the node has not been visited
        if node not in visited:
            # Mark the node as visited
            visited.add(node)

            # Enumerate all adjacent nodes, construct a new path, and push it into the queue
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    # If there's no path from start to target
    return None


class OfficerState(Enum):
    MOVE_TO = auto()
    EXAM = auto()
    EVAL = auto()
    MOVE_BACK = auto()
    IDLE = auto()


# TODO: move to numpy
def get_norm(a: Point2D):
    return math.sqrt(a.x**2 + a.y**2 + 1e-8)


class Officer(Walker):
    def __init__(
        self,
        npc: NPC | LlmNPC,
        judge_path: Path,
        rooms: list[Room],
        room_graph: dict[RoomName, list[RoomName]],
    ):

        super().__init__(
            pos=npc.pos,
            rooms=rooms,
            current_room=npc.room,
            terrain_collision=False,
            npc_collision=False,
            door_collision=True,
        )
        self.room_graph = room_graph

        self.npc = npc
        self.npc_history_backup = None

        self.game_state = State.GAME
        self.officer_state = OfficerState.IDLE
        self.target_pos: Point2D | None = None
        self.origin_pos: Point2D = npc.pos
        self.origin_room: Room = npc.room
        self.judge = Judge(bot=npc.bot, judge_path=judge_path, user=npc.user)
        self.npc_backup = None

    def _find_next_target_room(self, current_room: Room, target_room_name: RoomName) -> RoomName:
        path = bfs_shortest_path(self.room_graph, current_room.name, target_room_name)
        assert path is not None, f"Could not find path from {current_room.name} to {target_room_name}"
        return path[1]

    def _find_next_target_door(self, current_room: Room, target_room_name: RoomName) -> Point2D:
        door = next((door for door in current_room.doors if door.out_room == target_room_name), None)
        assert door is not None, f"Could not find door in room {current_room.name} to {target_room_name}"
        door_pos = door.get_door_pos()
        return door_pos

    def _walk(self, player_room: Room, player: Player, target_pos: Point2D):

        if self.officer_state == OfficerState.MOVE_TO:
            if player_room.name != self.npc.room.name:
                target_room = self._find_next_target_room(self.npc.room, player_room.name)
                target_pos = self._find_next_target_door(self.npc.room, target_room)
        elif self.officer_state == OfficerState.MOVE_BACK:
            if self.npc.room.name != self.origin_room.name:
                target_room = self._find_next_target_room(self.npc.room, self.origin_room.name)
                target_pos = self._find_next_target_door(self.npc.room, target_room)
        else:
            raise NotImplementedError(self.officer_state)

        # walk towards target
        d_pos = target_pos - self.npc.pos
        d_pos = d_pos / get_norm(d_pos)
        self.dx = d_pos.x
        self.dy = d_pos.y

        self.npc.room = self.rooms[self.move(room=self.npc.room)]
        self.npc.pos = self.pos

    def _is_target_reached(self, current_pos: Point2D, target_pos: Point2D, min_distance: float = 30.0):
        distance = get_norm(target_pos - current_pos)
        return distance <= min_distance

    def _call_officer(self, chat_box: ChatBox):
        msg = f"<font color=#E0C834>Calling {self.npc.name}...\n</font>"
        msg += f"{self.npc.name}: Hello?\n"
        msg += f"Detective {self.npc.user}: Good news, I know now who the murderer is!\n"
        msg += f"{self.npc.name}: About time! OK, stay where you are, I'm coming to you!\n"
        self.npc.chat_history += msg
        chat_box.update_chat()

    def _load_history_backup(self):
        if self.npc_history_backup is not None:
            self.npc.chat_history = self.npc_history_backup
            self.npc_history_backup = None

    def update(self, state: State, player: Player, player_room: Room, chat_box: ChatBox):

        if self.game_state == State.EXAM and not chat_box.is_on:
            state = State.GAME

        # react to new game state
        if self.game_state == State.GAME and state == State.EXAM:
            # TODO: copy npc backup and init new
            self.npc_history_backup = self.npc.chat_history
            self.npc.chat_history = ""

            chat_box.open_chat(self.npc)
            self._call_officer(chat_box=chat_box)
            self.officer_state = OfficerState.MOVE_TO
        elif self.game_state == State.EXAM and state == State.GAME:
            self.officer_state = OfficerState.MOVE_BACK

        self.game_state = state

        if self.officer_state == OfficerState.MOVE_TO:
            target_pos = player.pos
            # TODO: remove hardcoded min_distance
            if self.current_room == player.current_room and self._is_target_reached(
                self.pos, target_pos, min_distance=50.0
            ):
                chat_box.close_chat()
                chat_box.open_chat(self.judge)
                self.officer_state = OfficerState.EXAM
            else:
                self._walk(player_room=player_room, player=player, target_pos=target_pos)

        elif self.officer_state == OfficerState.MOVE_BACK:
            target_pos = self.origin_pos
            if self._is_target_reached(self.pos, target_pos, min_distance=5.0):
                self.officer_state == OfficerState.IDLE
                self._load_history_backup()
            else:
                self._walk(player_room=player_room, player=player, target_pos=target_pos)

        if self.officer_state == OfficerState.MOVE_BACK:
            if self.judge.is_game_won:
                self.game_state = State.END

        return self.game_state
