from dataclasses import dataclass
from pathlib import Path

from utils import Point2D


@dataclass
class Character:
    prompt_path: Path
    pos: Point2D


CHARACTERS = {
    "tim": Character(Path(__file__).parent.parent / "plot/business_of_murder/prompts/tim.txt", Point2D(100, 100))
}
