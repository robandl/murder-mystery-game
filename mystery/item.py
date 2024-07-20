from pathlib import Path

import pygame
from npc import NPC, load_contour_image
from room import Room
from utils import Point2D


class Item(NPC):
    def __init__(
        self,
        name: str,
        pos: Point2D,
        room: Room,
        description: str,
        img_path: Path,
        img_size: list[int, int] = [50, 50],
    ):
        super().__init__(name=name, pos=pos, room=room, chat_history=self._get_chat_history(description))

        self._img = load_contour_image(img_path)
        self._chat_img = pygame.image.load(str(img_path))
        self._img_size = img_size

    def _get_chat_history(self, description: str) -> str:
        return f"<font color=#E0C834>{description}</font>"

    def chat(self, new_message) -> str:
        return self.chat_history

    def get_figure_image(self) -> pygame.Surface:
        return self._img

    def get_chat_image(self) -> pygame.Surface:
        return self._chat_img

    def get_image_size(self) -> list[int, int]:
        return self._img_size
