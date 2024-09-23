from pathlib import Path
from typing import Tuple

import numpy as np
import pygame
from door import Door
from utils import WHITE, RoomName

# TODO: Remove hard coded room size
ROOM_SIZE = (800, 600)


class Room:
    def __init__(
        self,
        name: RoomName,
        doors: list[Door],
        terrain: np.array,
        background: Tuple,
        image: Path | None,
        pretty_name: str | None = None,
    ):
        self.name = name
        self.doors = doors
        self.terrain = terrain
        self.background = background
        if pretty_name is None:
            pretty_name = str(name)

        self.image = None
        if image is not None:
            img = pygame.image.load(image)
            # TODO: Remove hard coded room size
            self.image = pygame.transform.scale(img, ROOM_SIZE)
        font = pygame.font.SysFont('Arial', 25)
        self.caption = font.render(pretty_name, True, WHITE)
        self.text_rect = self.caption.get_rect(center=(ROOM_SIZE[0] // 2, ROOM_SIZE[1] + 15))

    def draw(self, screen):
        screen.fill(self.background)
        if self.image is not None:
            screen.blit(self.image, (0, 0))
        screen.blit(self.caption, self.text_rect)
