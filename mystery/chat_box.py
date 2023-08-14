import re

import pygame
import pygame_gui
import pygame_gui.data
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton, UITextBox, UITextEntryBox
from utils import Point2D


class ChatBox:
    def __init__(
        self, ui_manager: pygame_gui.UIManager, text_rect: pygame.Rect, input_rect: pygame.Rect, button_pos: Point2D
    ):
        text_box = UITextBox(html_text="", relative_rect=text_rect, manager=ui_manager)

        entry_box = UITextEntryBox(relative_rect=input_rect, manager=ui_manager)
        entry_box.blink_cursor_time = 5.0
        leave_button = UIButton((button_pos.x, button_pos.y), '[ESC] Leave chat', manager=ui_manager)

        entry_box.update(5.0)
        text_box.update(5.0)

        self.text_box = text_box
        self.entry_box = entry_box
        self.leave_button = leave_button
        self._active_npc = None

    def handle_event(self, event: pygame.Event) -> bool:
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
            # reset inpuy box
            self.clear_chat_box()
            self.scroll_down()
        return True

    def open_chat(self, npc):
        npc.open_chat()
        self._active_npc = npc
        chat_history = npc.load_chat_history()
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
