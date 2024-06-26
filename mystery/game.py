from pathlib import Path

import pygame
import pygame_gui
from chat_box import ChatBox
from end_screen import EndScreen
from llm import get_llm
from menu import Menu
from params import Params
from pygame.constants import K_DOWN, K_ESCAPE, K_LEFT, K_RETURN, K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT, K_m
from pygame.event import Event
from pygame_gui.elements import UIButton
from state import State
from utils import Point2D
from world import World

# Initialize Pygame
pygame.init()
config_path = Path(__file__).resolve().parent.parent / "plot" / "business_of_murder" / "game_config.yaml"
params = Params.from_config(config_path)

# Set up the display
screen = pygame.display.set_mode((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
pygame.display.set_caption("Mystery Dinner")


# bot = get_llm("chat_gpt")
bot = get_llm("local")
user = "R.A."


class Game:
    def __init__(
        self,
        config_path: Path,
        params: Params,
    ):
        self.params = params

        self.ui_manager = pygame_gui.UIManager((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
        self.chat_box = ChatBox(
            params=params,
            text_rect=pygame.Rect(
                int(params.WIDTH / 4), params.HEIGHT, int(params.WIDTH / 2), int(params.CHAT_HEIGHT * 2 / 3)
            ),
            input_rect=pygame.Rect(
                int(params.WIDTH / 4),
                params.HEIGHT + int(params.CHAT_HEIGHT * 2 / 3),
                int(params.WIDTH / 2),
                int(params.CHAT_HEIGHT / 3),
            ),
            button_pos=Point2D(650, 750),
        )

        self.world = World(config_path=config_path)
        self.current_room = self.world.get_starting_room()

        self.rooms = self.world.create_rooms(params=params)
        self.player = self.world.create_player(params, rooms=self.rooms, current_room=self.rooms[self.current_room])
        self.npcs = self.world.create_npcs(rooms=self.rooms, bot=bot, user=user)

        self.officer = self.world.create_officer(npcs=self.npcs, rooms=self.rooms)
        self.judge = self.officer.judge
        #        self.active_npc = None

        # buttons
        self.menu_button = UIButton(pygame.Rect(1, 1, 100, 40), '[M] Menu', manager=self.ui_manager)
        self.exam_button_text = '[ENTER] "I\'ve found the murderer"'
        self.exam_button = UIButton(pygame.Rect(102, 1, 320, 40), self.exam_button_text, manager=self.ui_manager)

    def _on_enter(self, current_state):

        new_state = State.GAME if current_state == State.EXAM else State.EXAM
        return new_state

    def _update_buttons(self, current_state):
        if current_state == State.EXAM:
            self.exam_button.set_text('[ENTER] "I need to investigate more"')
        else:
            self.exam_button.set_text(self.exam_button_text)

    def get_visible_npcs(self):
        visibile_npcs = [npc for npc in self.npcs if npc.room.name == self.current_room]
        return visibile_npcs

    def draw(self, screen):
        self.rooms[self.current_room].draw(screen)

        # Draw player character
        self.player.draw(screen)

        # Draw NPCs
        visibile_npcs = self.get_visible_npcs()
        for npc in visibile_npcs:
            npc.draw(screen)

        # Draw doors
        for door in self.room.doors:
            door.draw(screen)

        # Draw the chat frame
        for npc in self.npcs:
            if npc.chat_open:
                self.chat_box.draw(screen=screen, npc=npc)

        if self.judge.chat_open:
            self.chat_box.draw(screen=screen, npc=self.judge)

        if not self.chat_box.is_on:
            self.ui_manager.draw_ui(window_surface=screen)
        self.ui_manager.update(0.005)
        self.chat_box.ui_manager.update(0.005)

    def handle_player_movement(self, event: Event):
        if event.key == K_UP:
            self.player.dy = -1
        elif event.key == K_DOWN:
            self.player.dy = 1
        elif event.key == K_LEFT:
            self.player.dx = -1
        elif event.key == K_RIGHT:
            self.player.dx = 1
        elif event.key == K_SPACE:
            visibile_npcs = self.get_visible_npcs()
            distances = [
                ((self.player.pos.x - npc.pos.x) ** 2 + (self.player.pos.y - npc.pos.y) ** 2) ** 0.5
                for npc in visibile_npcs
            ]
            if not distances:
                return
            closest_npc, distance = min(zip(visibile_npcs, distances), key=lambda x: x[1])
            if distance <= 2 * self.params.NPC_RADIUS:
                # TODO: Proper hitbox
                print(f"Chatting with npc {closest_npc.name}")
                self.chat_box.open_chat(closest_npc)

    def handle_events(self, state: State) -> State:
        for event in pygame.event.get():
            if event.type == QUIT:
                return State.QUIT

            if self.chat_box.is_on:
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.chat_box.close_chat()
                else:
                    self.chat_box.handle_event(event)
                    continue

            # handle menu keys
            if event.type == KEYDOWN and event.key == K_m:
                return State.MENU
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return self._on_enter(state)

            # handle menu buttons
            self.ui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.menu_button:
                    return State.MENU
                elif event.ui_element == self.exam_button:
                    return self._on_enter(state)

            # handle player movement
            if event.type == KEYDOWN:
                self.handle_player_movement(event=event)

            if event.type == KEYUP:
                if event.key == K_UP and self.player.dy == -1:
                    self.player.dy = 0
                elif event.key == K_DOWN and self.player.dy == 1:
                    self.player.dy = 0
                elif event.key == K_LEFT and self.player.dx == -1:
                    self.player.dx = 0
                elif event.key == K_RIGHT and self.player.dx == 1:
                    self.player.dx = 0

        self._update_buttons(current_state=state)

        return state


def game_loop():
    current_state = State.MENU
    # current_state = State.END
    game = Game(config_path=config_path, params=params)
    menu = Menu(params=params)
    end_screen = EndScreen(params=params)

    while True:
        if current_state == State.MENU:
            menu.draw(screen=screen)
            current_state = menu.handle_events(state=current_state)

        elif current_state in [State.GAME, State.EXAM]:
            game.room = game.rooms[game.current_room]
            current_state = game.handle_events(state=current_state)
            game.current_room = game.player.move(game.room, npcs=game.get_visible_npcs())
            current_state = game.officer.update(
                state=current_state, player_room=game.room, player=game.player, chat_box=game.chat_box
            )
            game.draw(screen=screen)

        elif current_state == State.END:
            end_screen.draw(screen=screen, num_attempts=game.judge.num_attempts)
            current_state = end_screen.handle_events(state=current_state)

        pygame.display.flip()

        if current_state == State.QUIT:
            break


# Game loop
game_loop()

# Quit the game
pygame.quit()
