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

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] and not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            player_text = self.entry_box.get_text()
            # remove beginning and trailing '\n's and ' 's
            player_text = re.sub(r'^[\n\s]+|[\n\s]+$', '', player_text)
            self.entry_box.set_text("")
            if player_text:
                assert self._active_npc is not None
                chat_history = self._active_npc.chat(player_text)
                self.text_box.set_text(chat_history)
        return True

    def open_chat(self, npc):
        npc.open_chat()
        self._active_npc = npc
        chat_history = npc.load_chat_history()
        self.text_box.set_text(chat_history)

    def close_chat(self):
        self._active_npc.close_chat()
        self._active_npc = None

    @property
    def is_on(self) -> bool:
        return self._active_npc is not None
