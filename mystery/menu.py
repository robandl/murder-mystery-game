import pygame
import pygame_gui
from params import Params
from pygame.constants import K_1, K_2, K_3, KEYDOWN, QUIT
from pygame_gui.elements import UIButton
from state import State
from utils import BLACK


class Menu:
    def __init__(self, params: Params):
        self.ui_manager = pygame_gui.UIManager((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
        self.start_game_button = UIButton(pygame.Rect(300, 200, 200, 50), '[1] Start Game', manager=self.ui_manager)

        self.credit_button = UIButton(pygame.Rect(300, 258, 200, 50), '[2] Credits', manager=self.ui_manager)

        self.quit_button = UIButton(pygame.Rect(300, 316, 200, 50), '[3] Quit', manager=self.ui_manager)

    def handle_events(self, state: State) -> bool:
        for event in pygame.event.get():
            if event.type == QUIT:
                return State.QUIT
            state = self._handle_event(event=event)
            if state != State.MENU:
                return state

        return state

    def _handle_event(self, event: pygame.Event) -> bool:
        # handle keys
        if event.type == KEYDOWN and event.key == K_1:
            return State.GAME
        elif event.type == KEYDOWN and event.key == K_2:
            print("Credits not implemented")
        elif event.type == KEYDOWN and event.key == K_3:
            return State.QUIT

        # handle button pressed
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_game_button:
                return State.GAME
            elif event.ui_element == self.credit_button:
                print("Credits not implemented")
            elif event.ui_element == self.quit_button:
                return State.QUIT

        return State.MENU

    def draw(self, screen):
        screen.fill(BLACK)
        self.ui_manager.draw_ui(window_surface=screen)
        self.ui_manager.update(0.01)
