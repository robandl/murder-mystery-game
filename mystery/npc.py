from dataclasses import dataclass

import pygame
from utils import GREEN, WHITE, Point2D


@dataclass
class NPC:
    name: str
    pos: Point2D
    chat_history: str = ""
    chat_open: bool = False

    def draw(self, screen):
        color = GREEN if self.chat_open else WHITE
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), 20)

    def open_chat(self):
        self.chat_open = True

    def close_chat(self):
        self.chat_open = False

    def load_chat_history(self) -> str:
        return self.chat_history

    def chat(self, new_message):
        if self.chat_open:
            self.chat_history += f"Player: {new_message}\n"

            # TODO: Add NPC message
            answer = f"{self.name}: Answer\n"
            self.chat_history += answer

        return self.chat_history
