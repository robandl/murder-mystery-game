import re

import pygame
import pygame_gui
import pygame_gui.data
from params import Params
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton, UITextBox, UITextEntryBox
from utils import Point2D


class ChatBox:
    def __init__(self, params: Params, text_rect: pygame.Rect, input_rect: pygame.Rect, button_pos: Point2D):
        self.ui_manager = pygame_gui.UIManager((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
        text_box = UITextBox(html_text="", relative_rect=text_rect, manager=self.ui_manager)

        entry_box = UITextEntryBox(relative_rect=input_rect, manager=self.ui_manager)
        entry_box.blink_cursor_time = 5.0
        leave_button = UIButton((button_pos.x, button_pos.y), '[ESC] Leave chat', manager=self.ui_manager)

        entry_box.update(5.0)
        text_box.update(5.0)

        self.text_box = text_box
        self.entry_box = entry_box
        self.leave_button = leave_button
        self._active_npc = None

        self.img_size = (int(params.WIDTH / 4 * 0.96), int(params.CHAT_HEIGHT * 0.96))
        self.img_pos = (int(0.02 * params.WIDTH / 4), int(params.HEIGHT + 0.02 * params.CHAT_HEIGHT))

    def handle_event(self, event: pygame.Event) -> bool:
        self.ui_manager.process_events(event)
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.leave_button:
                self.close_chat()
        # Hack: there can be a buffer of ENTER keys if llm inference takes too long
        # This here resets the input box if there is no text
        player_text = self.entry_box.get_text()
        # remove beginning and trailing '\n's and ' 's
        player_text = re.sub(r'^[\n\s]+|[\n\s]+$', '', player_text)
        if not player_text:
            # remove spaces and breaks if there is no valid text e.g. due to ENTER buffer
            self.clear_chat_box()
            return True

        # process input text
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] and not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            assert self._active_npc is not None
            chat_history = self._active_npc.chat(player_text)
            self.text_box.set_text(chat_history)
            # reset input box
            self.clear_chat_box()
            self.scroll_down()
        return True

    def draw(self, screen, npc):
        self.ui_manager.draw_ui(window_surface=screen)
        if (chat_image := npc.get_chat_image()) is not None:
            chat_image = pygame.transform.scale(chat_image, self.img_size)
            screen.blit(chat_image, self.img_pos)

    def open_chat(self, npc):
        npc.open_chat()
        self._active_npc = npc
        self.update_chat()

    def update_chat(self):
        chat_history = self._active_npc.load_chat_history()
        self.text_box.set_text(chat_history)
        self.entry_box.focus()
        self.clear_chat_box()
        self.scroll_down()

    def clear_chat_box(self):
        """Resets input box to prepare for next input"""
        self.entry_box.set_text("")

    def scroll_down(self):
        """Scolls down output box"""
        if self.text_box.scroll_bar is not None:
            self.text_box.scroll_bar.set_scroll_from_start_percentage(1.0)

    def close_chat(self):
        self._active_npc.close_chat()
        self._active_npc = None
        self.clear_chat_box()

    @property
    def is_on(self) -> bool:
        return self._active_npc is not None
