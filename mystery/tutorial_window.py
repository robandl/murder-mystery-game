from pathlib import Path

import pygame
import pygame.constants as pyconstants
import pygame_gui
import pygame_gui.data
from mystery.params import Params
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui._constants import UI_WINDOW_CLOSE
from pygame_gui.elements import UIButton, UITextBox, UIWindow


class CustomUiWindow(UIWindow):
    def on_close_window_button_pressed(self):
        # hack. Overwrite method to prevent closing the window.
        # As in the parent method, we still need to post the close event to catch it in self.handle_tutorial_events
        window_close_event = pygame.event.Event(
            UI_WINDOW_CLOSE, {'ui_element': self, 'ui_object_id': self.most_specific_combined_id}
        )
        pygame.event.post(window_close_event)


class TutorialWindow:
    def __init__(
        self,
        params: Params,
        prompt_path: Path | str,
    ):
        prompt_path = Path(prompt_path)
        page_paths = sorted(list(prompt_path.glob("*.txt")))
        assert len(page_paths) > 0, f"No pages found in {prompt_path}"
        pages = [page_path.read_text() for page_path in page_paths]

        self.ui_manager = pygame_gui.UIManager((params.WIDTH, params.HEIGHT))
        self.window = CustomUiWindow(
            pygame.Rect(
                int(params.WIDTH * 3 / 12),
                int(params.HEIGHT * 3 / 12),
                int(params.WIDTH / 2),
                int(params.HEIGHT / 2 - 8),
            ),
            self.ui_manager,
            window_display_title="Tutorial",
        )
        text_height, text_width = (int(params.HEIGHT / 3), int(params.WIDTH / 2 - 32))
        text_rect = pygame.Rect(0, 0, text_width, text_height)
        text_box = UITextBox(
            html_text=pages[0], relative_rect=text_rect, manager=self.ui_manager, container=self.window
        )
        text_box.update(5.0)
        self.text_box = text_box

        self.prev_button = UIButton((17, text_height), 'previous page', manager=self.ui_manager, container=self.window)
        self.next_button = UIButton(
            (text_width * 4 / 10, text_height), 'next page', manager=self.ui_manager, container=self.window
        )
        self.close_button = UIButton(
            (text_width * 5 / 8 + 20, text_height), 'close [ESC]', manager=self.ui_manager, container=self.window
        )

        # tutorial request text
        font = pygame.font.SysFont("Arial", 25)
        text = "Press 'h' to open the tutorial"
        color = (255, 255, 255)  # White color
        self.text_surface = font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect()
        self._game_center_y = params.HEIGHT / 2

        self._is_open = False
        self._tutorial_has_been_opened = False
        self._page_count = 0
        self._pages = pages
        self.update()

    def handle_tutorial_events(self, event: pygame.Event) -> bool:
        # TODO: Returning boolean is outdated
        if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.window:
            self._is_open = False
            self.update()
            return False

        if event.type == pyconstants.KEYDOWN:
            if event.key == pyconstants.K_ESCAPE:
                self._is_open = False
                return False
            elif event.key == pyconstants.K_h:
                self._is_open = False
                return False

        if event.type == UI_BUTTON_PRESSED:
            match event.ui_element:
                case self.prev_button:
                    self._page_count = max(0, self._page_count - 1)
                    self.update()
                case self.next_button:
                    self._page_count = min(len(self._pages) - 1, self._page_count + 1)
                    self.update()
                case self.close_button:
                    self._is_open = False
                    return False

        self.ui_manager.process_events(event)
        return True

    def update(self):
        self.text_box.set_text(self._pages[self._page_count])
        if self.text_box.scroll_bar is not None:
            self.text_box.scroll_bar.set_scroll_from_start_percentage(0.0)
        if self._page_count == 0:
            self.prev_button.disable()
            self.next_button.enable()

        elif self._page_count == len(self._pages) - 1:
            self.next_button.disable()
            self.prev_button.enable()
        else:
            self.prev_button.enable()
            self.next_button.enable()

    def draw(self, screen):
        self.ui_manager.update(0.01)
        self.ui_manager.draw_ui(window_surface=screen)

    def draw_tutorial_request_text(self, screen):

        # Get the center of the screen
        screen_rect = screen.get_rect()

        # Position the text in the center of the screen
        self.text_rect.midtop = (screen_rect.centerx, self._game_center_y)

        # Blit the text onto the screen
        screen.blit(self.text_surface, self.text_rect)

    @property
    def is_open(self):
        return self._is_open

    def open(self):
        self._is_open = True
        self._tutorial_has_been_opened = True

    @property
    def tutorial_has_been_opened(self):
        return self._tutorial_has_been_opened
