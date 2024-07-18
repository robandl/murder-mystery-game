from pathlib import Path
from typing import Optional, Tuple, Union

import pygame
from utils import RED, Point2D, Rectangle, RoomName


def draw_glowing_polygon(
    screen: pygame.Surface,
    pos: Point2D,
    points: list[Point2D],
    color: tuple[int, int, int],
    glow_color: tuple[int, int, int],
    thickness: int = 2,
    glow_radius: int = 10,
):
    abs_points = [(pos + p).to_tuple() for p in points]
    pygame.draw.polygon(screen, color, abs_points, thickness)


class Door:
    def __init__(
        self,
        pos: Point2D,
        in_room: RoomName,
        out_room: RoomName,
        img_path: Optional[Union[str, Path]] = None,
        color: Tuple = RED,
        polygon: Optional[list[Point2D]] = None,
    ):

        self.pos = pos
        self.in_room = in_room
        self.out_room = out_room

        # assert can only choose img_path, color or polygon
        assert img_path is None or polygon is None

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

        self.polygon = polygon

    def draw(self, screen):
        self.img_pos = Point2D(
            int(self.pos.x - self.img_size.x / 2),
            int(self.pos.y - self.img_size.y / 2),
        )

        if self.img is not None:
            # TODO: remove hardcode
            screen.blit(self.img, (self.img_pos.x, self.img_pos.y))
        elif self.polygon is not None:
            draw_glowing_polygon(screen, self.pos, self.polygon, self.color, (255, 0, 0))
        else:
            self.rectangle = Rectangle(
                self.img_pos,
                self.img_size.x,
                self.img_size.y,
            )
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
