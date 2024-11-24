from enum import Enum, auto


class State(Enum):
    INTRO = auto()
    MENU = auto()
    GAME = auto()
    TUTORIAL = auto()
    START_MENU = auto()
    EXAM = auto()
    END = auto()
    QUIT = auto()
