from pathlib import Path
from typing import Optional, Tuple, Union

import pygame
from utils import RED, Point2D, Rectangle, RoomName


def draw_glowing_polygon(
    screen: pygame.Surface,
    points: list[Point2D],
    color: tuple[int, int, int],
    glow_color: tuple[int, int, int],
    thickness: int = 2,
    glow_radius: int = 10,
):
    abs_points = [p.to_tuple() for p in points]
    pygame.draw.polygon(screen, color, abs_points, thickness)


class Door:
    def __init__(
        self,
        in_room: RoomName,
        out_room: RoomName,
        pos: Optional[Point2D] = None,
        img_path: Optional[Union[str, Path]] = None,
        color: Tuple = RED,
        polygon: Optional[list[Point2D]] = None,
    ):
        assert pos is not None or (polygon is not None and pos is None)

        self.pos = pos
        self.in_room = in_room
        self.out_room = out_room

        # assert can only choose img_path, color or polygon
        assert img_path is None or polygon is None

        self.color = color
        # TODO: Remove hardcoded sizes
        self.img_size = Point2D(40, 10) if img_path is None else Point2D(40, 100)
        self.game_center = Point2D(400, 300)

        self.img = None
        self.img_pos = pos
        if img_path is not None:
            img = pygame.image.load(img_path)
            # TODO: Remove hard code
            self.img = pygame.transform.scale(img, (self.img_size.x, self.img_size.y))

        if polygon is None:
            self.rectangle = Rectangle(
                self.img_pos,
                self.img_size.x,
                self.img_size.y,
            )
        self.polygon = polygon

    def get_door_pos(self):
        if self.polygon is not None:
            x = sum([p.x for p in self.polygon]) / len(self.polygon)
            y = sum([p.y for p in self.polygon]) / len(self.polygon)
            return Point2D(x, y)
        return Point2D(
            self.rectangle.top_left.x + self.rectangle.width / 2, self.rectangle.top_left.y + self.rectangle.height / 2
        )

    def _get_polygon_max_width(self):
        return max([p.x for p in self.polygon])

    def get_safe_exit_pos(self):
        """Get a safe position to position the player when exiting the door"""

        if self.polygon is not None:
            min_x = min([p.x - self.game_center.x for p in self.polygon], key=abs)
            min_y = min([p.y - self.game_center.y for p in self.polygon], key=abs)
        else:
            min_x = min(
                self.rectangle.top_left.x - self.game_center.x,
                self.rectangle.top_left.x + self.rectangle.width - self.game_center.x,
            )
            min_y = min(
                self.rectangle.top_left.y - self.game_center.y,
                self.rectangle.height + self.rectangle.top_left.y - self.game_center.y,
            )
        pos = Point2D(
            self.game_center.x + (min_x + 20 if min_x < 0 else min_x - 20),
            self.game_center.y + (min_y + 20 if min_y < 0 else min_y - 20),
        )
        return pos

    def draw(self, screen):

        if self.polygon is not None:
            draw_glowing_polygon(screen, self.polygon, self.color, (255, 0, 0))
        else:
            img_pos = Point2D(
                int(self.pos.x - self.img_size.x / 2),
                int(self.pos.y - self.img_size.y / 2),
            )
            if self.img is not None:
                screen.blit(self.img, (self.img_pos.x, self.img_pos.y))
                return

            self.rectangle = Rectangle(
                img_pos,
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
