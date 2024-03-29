from pathlib import Path
from typing import Tuple

import numpy as np
import pygame
from door import Door
from utils import RoomName


class Room:
    def __init__(
        self,
        name: RoomName,
        doors: list[Door],
        terrain: np.array,
        background: Tuple,
        image: Path | None,
    ):
        self.name = name
        self.doors = doors
        self.terrain = terrain
        self.background = background

        self.image = None
        if image is not None:
            img = pygame.image.load(image)
            # TODO: Remove hard coded room size
            self.image = pygame.transform.scale(img, (800, 600))

    def draw(self, screen):
        screen.fill(self.background)
        if self.image is not None:
            screen.blit(self.image, (0, 0))
