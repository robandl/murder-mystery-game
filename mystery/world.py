from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import yaml
from animation import Animation
from door import Door
from llm import Bot
from npc import NPC, LlmNPC
from officer import Officer
from params import Params
from player import Player
from room import Room
from utils import BLACK, BLUE, Point2D, RoomName


class World:
    def __init__(self, config_path: Path):
        with open(config_path, 'r') as file:
            world_config = yaml.safe_load(file)["world"]
        self.config_path = config_path
        self.world_config = world_config

    def _get_abs_path(self, path: Optional[Path]) -> Optional[Path]:
        return self.config_path.parent / path if path is not None else None

    def get_starting_room(self):
        room_str = self.world_config["start_room"]
        return RoomName[room_str.upper()]

    def create_player(self, params: Params, rooms: list[Room], current_room: Room) -> Player:
        player_config = self.world_config["player"]
        animation_kwargs = {k: self._get_abs_path(v) for k, v in player_config.pop("animation").items()}
        animation = Animation(**animation_kwargs)
        return Player(
            params=params,
            pos=Point2D(*player_config["start_pos"]),
            animation=animation,
            rooms=rooms,
            current_room=current_room,
        )

    def create_officer(self, npcs: list[NPC], rooms: list[Room]) -> Officer:
        officer_config = self.world_config["officer"]
        npc_name = officer_config["name"]
        npc = [npc for npc in npcs if npc.name == npc_name]
        assert len(npc) == 1, npc

        return Officer(npc=npc[0], exam_path=officer_config["exam"], rooms=rooms)

    def create_rooms(self, params: Params) -> Dict[RoomName, Room]:
        rooms = {}
        for room_str, room_config in self.world_config["rooms"].items():
            room_name = RoomName[room_str.upper()]
            doors = self._create_doors(room_config.get("doors", []), in_room=room_name)
            background = self._get_background(room_config["background"])
            terrain = self._create_terrain(params=params)
            image = self._get_abs_path(room_config["image"]) if "image" in room_config else None

            rooms[room_name] = Room(name=room_name, doors=doors, terrain=terrain, background=background, image=image)
        return rooms

    def create_npcs(self, rooms: list[Room], bot: Bot, user: str) -> List[NPC]:
        npcs = []
        for room_str, room_config in self.world_config["rooms"].items():
            room_name = RoomName[room_str.upper()]
            for npc_config in room_config["npcs"]:
                name = npc_config["name"]
                pos = Point2D(*npc_config["start_pos"])

                if npc_config.get("use_llm", False):
                    prompt_path = self._get_abs_path(npc_config.get("prompt"))
                    chat_img = self._get_abs_path(npc_config.get("chat_img"))
                    figure_img = self._get_abs_path(npc_config.get("figure_img"))
                    assert prompt_path.is_file(), f"Could not find prompt path for npc `{name}` in: {str(prompt_path)}"
                    npc = LlmNPC(
                        name=name,
                        room=rooms[room_name],
                        pos=pos,
                        bot=bot,
                        prompt_path=prompt_path,
                        user=user,
                        chat_img=chat_img,
                        figure_img=figure_img,
                    )
                else:
                    npc = NPC(name=name, pos=pos, room=room_name)
                npcs.append(npc)
        return npcs

    def _create_doors(self, door_configs, in_room: RoomName) -> List[Door]:
        doors = []
        for door_config in door_configs:
            pos = Point2D(*door_config["start_pos"])
            out_room = RoomName[door_config["out_room"].upper()]
            img_path = self._get_abs_path(door_config.get("img"))
            assert out_room != in_room
            door = Door(pos=pos, in_room=in_room, out_room=out_room, img_path=img_path)
            doors.append(door)
        return doors

    def _get_background(self, background: str):
        if background == "black":
            return BLACK
        elif background == "blue":
            return BLUE
        else:
            raise NotImplementedError(background)

    def _create_terrain(self, params: Params):
        terrain_mask = np.zeros((params.HEIGHT, params.WIDTH), dtype=bool)
        # Set frame values to True
        terrain_mask[:5, :] = True  # Top frame
        terrain_mask[-5:, :] = True  # Bottom frame
        terrain_mask[:, :5] = True  # Left frame
        terrain_mask[:, -5:] = True  # Right frame
        return terrain_mask
