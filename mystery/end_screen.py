import random
from dataclasses import dataclass

import pygame
import pygame_gui
from params import Params
from pygame.constants import KEYDOWN, QUIT, K_m
from pygame_gui.elements import UIButton
from state import State
from utils import BLACK


@dataclass
class Particle:
    x: int
    y: int
    color: tuple


class EndScreen:
    def __init__(self, params: Params):
        self.screen_width = params.WIDTH
        self.screen_height = params.HEIGHT + params.CHAT_HEIGHT
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        num_particles = 100
        self.confetti = []
        for i in range(num_particles):
            x = random.randrange(0, self.screen_width)
            y = random.randrange(0, self.screen_height)
            self.confetti.append(
                Particle(x=x, y=y, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            )

        self.menu_button = UIButton(pygame.Rect(1, 1, 100, 40), '[M] Menu', manager=self.ui_manager)

    def handle_events(self, state: State) -> bool:
        for event in pygame.event.get():
            if event.type == QUIT:
                return State.QUIT

            # handle menu keys
            if event.type == KEYDOWN and event.key == K_m:
                return State.MENU

            self.ui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.menu_button:
                    print(213)
                    return State.MENU

        return state

    def draw(self, screen, num_attempts):
        screen.fill(BLACK)

        for i, particle in enumerate(self.confetti):
            pygame.draw.circle(screen, particle.color, [particle.x, particle.y], 5)
            self.confetti[i].y += 0.2
            if self.confetti[i].y > self.screen_height:
                self.confetti[i].y = random.randrange(-50, -10)
                self.confetti[i].x = random.randrange(0, self.screen_width)

        self.font = pygame.font.Font(None, 74)
        text = self.font.render('You\'ve Won!', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 1 / 3)))
        screen.blit(text, text_rect)

        self.font = pygame.font.Font(None, 40)
        text = self.font.render(f'Failed Exams: {num_attempts-1}', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 2 / 5)))
        screen.blit(text, text_rect)

        self.ui_manager.draw_ui(window_surface=screen)
        self.ui_manager.update(0.01)
