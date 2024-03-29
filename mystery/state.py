from enum import Enum, auto


class State(Enum):
    MENU = auto()
    GAME = auto()
    START_MENU = auto()
    EXAM = auto()
    END = auto()
    QUIT = auto()
