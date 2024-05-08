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

    # TODO: this is chatgpt's fault. Should just use numpy here
    def __add__(self, other):
        if isinstance(other, Point2D):
            return Point2D(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Point2D(self.x + other, self.y + other)
        raise ValueError("Unsupported type for addition")

    def __sub__(self, other):
        if isinstance(other, Point2D):
            return Point2D(self.x - other.x, self.y - other.y)
        elif isinstance(other, (int, float)):
            return Point2D(self.x - other, self.y - other)
        raise ValueError("Unsupported type for subtraction")

    def __mul__(self, other):
        if isinstance(other, (int, float)):  # scalar multiplication
            return Point2D(self.x * other, self.y * other)
        elif isinstance(other, Point2D):  # pointwise multiplication
            return Point2D(self.x * other.x, self.y * other.y)
        raise ValueError("Unsupported type for multiplication")

    def __truediv__(self, other):
        if isinstance(other, (int, float)):  # scalar division
            return Point2D(self.x / other, self.y / other)
        elif isinstance(other, Point2D):  # pointwise division
            return Point2D(self.x / other.x, self.y / other.y)
        raise ValueError("Unsupported type for division")


@dataclass
class Rectangle:
    top_left: Point2D
    width: float
    height: float


class RoomName(Enum):
    # TODO: remove hardcoded room names
    RICK_SALOON = "RICK_SALOON"
    RICK_HALL = "RICK_HALL"
    RICK_BATHROOM = "RICK_BATHROOM"
    RICK_OVERVIEW = "RICK_OVERVIEW"
    OFFICE_BATHROOM = "OFFICE_BATHROOM"
    OFFICE_HALL = "OFFICE_HALL"
    OFFICE_OVERVIEW = "OFFICE_OVERVIEW"
    OFFICE_PARTY = "OFFICE_PARTY"
    OFFICE_RICKS_BUREAU = "OFFICE_RICKS_BUREAU"
