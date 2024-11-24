import re
from enum import Enum, auto
from pathlib import Path

import pygame
import pygame_gui
from params import Params
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton, UITextBox, UITextEntryLine, UIWindow

POPUP_WIDTH, POPUP_HEIGHT = 600, 300  # TODO: Move to config


class IntroState(Enum):
    LOADING_SCREEN = auto()
    GET_USER_NAME = auto()
    INTRO_COMPLETED = auto()


class IntroScreen:
    def __init__(self, params: Params, image_path: Path, officer_path: Path, officer_name: str, default_user: str):

        width, height = params.WIDTH, params.HEIGHT
        self.manager = pygame_gui.UIManager((width, height))

        self._init_loading_screen(manager=self.manager, params=params, image_path=image_path)
        self._init_user_name_popup(manager=self.manager, officer_path=officer_path, officer_name=officer_name)
        self.popup_window_active = False

        self.default_user_name = default_user
        self.custom_user_name = default_user

        self.current_state = IntroState.LOADING_SCREEN

    def _init_loading_screen(self, manager: pygame_gui.UIManager, params: Params, image_path: Path):

        # Loading screen items
        background_image = pygame.image.load(image_path)
        self.background_image = pygame.transform.scale(background_image, (params.WIDTH, params.HEIGHT))
        text_string = "Press ENTER or RETURN to start"

        width, height = params.WIDTH, params.HEIGHT

        center_x, center_y = width // 2, int(height / 3 * 2)
        font = pygame.font.SysFont("Arial", 20)
        color = (255, 255, 255)
        self.text_surface = font.render(text_string, True, color)
        self.text_rect = self.text_surface.get_rect(center=(center_x, center_y))
        self.blink_interval = 1000  # Blink every 500 milliseconds (0.5 seconds)
        self.last_blink_time = pygame.time.get_ticks()
        self.text_visible = True

    def _init_user_name_popup(self, manager: pygame_gui.UIManager, officer_path: Path, officer_name: str):
        # user name popup items
        popup_rect = pygame.Rect((100, 150), (POPUP_WIDTH, POPUP_HEIGHT))
        popup_window = UIWindow(
            rect=popup_rect, manager=manager, window_display_title=officer_name, object_id="#popup_window"
        )
        self.popup_window = popup_window
        self.popup_window.hide()

        raw_text = (
            "Hello Detective,\nWelcome to this murder mystery game. "
            "We're taking you to the crime scene right away... \n\n"
            "...ehhm, what was your name again?"
        )
        text_rect = pygame.Rect((10, 10), (POPUP_WIDTH - 210, 150))
        self.text_box = UITextBox(html_text=raw_text, relative_rect=text_rect, manager=manager, container=popup_window)

        self.name_entry = UITextEntryLine(
            relative_rect=pygame.Rect((10, 170), (POPUP_WIDTH - 360, 30)), manager=manager, container=popup_window
        )
        self.name_entry.blink_cursor_time = 5.0
        self.confirm_button = UIButton(
            (10 + POPUP_WIDTH - 360, 170), '[ENTER] Confirm', manager=manager, container=popup_window
        )

        image_surface = pygame.image.load(officer_path)  # Replace with your image path
        scaled_image = pygame.transform.scale(image_surface, (200, POPUP_HEIGHT - 40))
        self.image_element = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((POPUP_WIDTH - 210, 10), (200, POPUP_HEIGHT - 40)),
            image_surface=scaled_image,
            manager=manager,
            container=popup_window,
        )

    def _read_user_name(self) -> str:
        name = self.name_entry.get_text()
        name = re.sub(r'^[\n\s]+|[\n\s]+$', '', name)
        return name if len(name) > 0 else self.default_user_name

    def draw(self, screen, state: IntroState):
        if state == IntroState.LOADING_SCREEN:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time > self.blink_interval:
                self.text_visible = not self.text_visible
                self.last_blink_time = current_time

            screen.blit(self.background_image, (0, 0))
            if self.text_visible:
                screen.blit(self.text_surface, self.text_rect)

        elif state == IntroState.GET_USER_NAME:
            if not self.popup_window_active:
                self.popup_window_active = True
                self.popup_window.show()
                self.name_entry.focus()

        self.manager.draw_ui(window_surface=screen)
        self.manager.update(0.005)

    def handle_events(self, state: IntroState):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if state == IntroState.LOADING_SCREEN:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        return IntroState.GET_USER_NAME
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return IntroState.GET_USER_NAME

            elif state == IntroState.GET_USER_NAME:
                if event.type == UI_BUTTON_PRESSED:
                    if event.ui_element == self.confirm_button:
                        self.custom_user_name = self._read_user_name()
                        return IntroState.INTRO_COMPLETED if self.custom_user_name != self.default_user_name else state

                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    self.custom_user_name = self._read_user_name()
                    if self.custom_user_name != self.default_user_name:
                        return IntroState.INTRO_COMPLETED if self.custom_user_name != self.default_user_name else state
            else:
                return state

            self.manager.process_events(event)

        return state

    def run_intro_and_user_name_entry(self, screen) -> str:
        while True:
            if self.current_state == IntroState.INTRO_COMPLETED:
                return self.custom_user_name

            self.current_state = self.handle_events(state=self.current_state)
            self.draw(screen=screen, state=self.current_state)

            pygame.display.flip()

    def get_default_user(self) -> str:
        return self.default_user_name
