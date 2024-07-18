from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


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

    def to_tuple(self):
        return self.x, self.y


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


def draw_contour(img: np.ndarray, color: tuple[int, int, int] = (255, 0, 0), thickness: int = 3):
    # Extract the alpha channel
    alpha_channel = img[:, :, 3]

    # Threshold the alpha channel to get a binary mask
    _, binary_mask = cv2.threshold(alpha_channel, 0, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Assuming the largest contour is the object
    contour = max(contours, key=cv2.contourArea)

    # Optionally visualize the result
    #    img_with_contour = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
    img_with_contour = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
    img_with_contour = cv2.drawContours(img_with_contour, [contour], -1, color, thickness)
    img_with_contour = cv2.cvtColor(img_with_contour, cv2.COLOR_RGB2BGR)
    img_with_contour = np.concatenate([img_with_contour, img[:, :, 3:]], axis=-1)
    return img_with_contour
