from enum import Enum, auto


class State(Enum):
    MENU = auto()
    GAME = auto()
    TUTORIAL = auto()
    START_MENU = auto()
    EXAM = auto()
    END = auto()
    QUIT = auto()
