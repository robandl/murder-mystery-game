from pathlib import Path
from typing import Optional, Tuple, Union

import pygame
from utils import WHITE, Point2D, Rectangle, RoomName


class Door:
    def __init__(
        self,
        pos: Point2D,
        in_room: RoomName,
        out_room: RoomName,
        img_path: Optional[Union[str, Path]] = None,
        color: Tuple = WHITE,
    ):
        self.pos = pos
        self.in_room = in_room
        self.out_room = out_room
        self.color = color
        # TODO: Remove hardcoded sizes
        self.img_size = Point2D(40, 10) if img_path is None else Point2D(40, 100)

        self.img = None
        self.img_pos = pos
        if img_path is not None:
            img = pygame.image.load(img_path)
            # TODO: Remove hard code
            self.img = pygame.transform.scale(img, (self.img_size.x, self.img_size.y))

        self.rectangle = Rectangle(
            self.img_pos,
            self.img_size.x,
            self.img_size.y,
        )

    def draw(self, screen):
        self.img_pos = Point2D(
            int(self.pos.x - self.img_size.x / 2),
            int(self.pos.y - self.img_size.y / 2),
        )
        self.rectangle = Rectangle(
            self.img_pos,
            self.img_size.x,
            self.img_size.y,
        )

        if self.img is None:
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
        else:
            # TODO: remove hardcode
            screen.blit(self.img, (self.img_pos.x, self.img_pos.y))
