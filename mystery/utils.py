from dataclasses import dataclass
from enum import Enum

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)


@dataclass
class Point2D:
    x: float
    y: float


@dataclass
class Rectangle:
    top_left: Point2D
    width: float
    height: float


class RoomName(Enum):
    HALL = "HALL"
    BATHROOM = "BATHROOM"
