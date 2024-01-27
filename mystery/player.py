from animation import Animation, Direction
from params import Params
from room import Room
from utils import Point2D
from walker import Walker


class Player(Walker):
    def __init__(self, params: Params, pos: Point2D, rooms: list[Room], current_room: Room, animation: Animation):

        super().__init__(
            pos=pos,
            rooms=rooms,
            current_room=current_room,
            terrain_collision=True,
            npc_collision=True,
            door_collision=True,
        )

        self.params = params
        self.animation = animation

    def draw(self, screen):
        if self.dx < 0:
            direction = Direction.LEFT
        elif self.dx > 0:
            direction = Direction.RIGHT
        else:
            direction = None
        self.animation.draw(screen=screen, pos=self.pos, direction=direction)
