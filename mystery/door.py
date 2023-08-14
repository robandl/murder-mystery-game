from dataclasses import dataclass
from typing import Tuple

import pygame
from utils import Rectangle, RoomName


@dataclass
class Door:
    rectangle: Rectangle
    in_room: RoomName
    out_room: RoomName

    color: Tuple

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (
                int(self.rectangle.top_left.x),
                int(self.rectangle.top_left.y),
                int(self.rectangle.width),
                int(self.rectangle.height),
            ),
        )
