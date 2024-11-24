from pathlib import Path

import pygame
import pygame_gui
from chat_box import ChatBox
from end_screen import EndScreen
from llm import Bot, get_llm
from menu import Menu
from params import Params
from pygame.constants import K_DOWN, K_ESCAPE, K_LEFT, K_RETURN, K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT, K_h, K_m
from pygame.event import Event
from pygame_gui.elements import UIButton
from state import State
from utils import WHITE, Point2D
from world import World

DRAW_GRID = False
# LLM_MODE = "local"
LLM_MODE = "chat_gpt"

# Initialize Pygame
pygame.init()
config_path = Path(__file__).resolve().parent.parent / "plot" / "business_of_murder" / "game_config.yaml"
params = Params.from_config(config_path)

# Set up the display
screen = pygame.display.set_mode((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
pygame.display.set_caption("Mystery Dinner")


def draw_distance_grid(screen: pygame.Surface):
    # Draw grid lines
    grid_size = 50
    for x in range(0, screen.get_width(), grid_size):
        pygame.draw.line(screen, WHITE, (x, 0), (x, screen.get_height()))
        # Draw the pixel number
        font = pygame.font.Font(None, 20)
        text = font.render(str(x), True, WHITE)
        screen.blit(text, (x, 0))

    for y in range(0, screen.get_height(), grid_size):
        pygame.draw.line(screen, WHITE, (0, y), (screen.get_width(), y))
        # Draw the pixel number
        font = pygame.font.Font(None, 20)
        text = font.render(str(y), True, WHITE)
        screen.blit(text, (0, y))


class Game:
    def __init__(
        self,
        world: World,
        params: Params,
        bot: Bot,
        user: str,
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

        self.current_room = world.get_starting_room()
        self.rooms = world.create_rooms(params=params)
        self.room_graph = world.create_room_graph(rooms=self.rooms)
        self.player = world.create_player(params, rooms=self.rooms, current_room=self.rooms[self.current_room])
        self.npcs = world.create_npcs(rooms=self.rooms, bot=bot, user=user)

        # add items to npcs for now
        self.npcs += world.create_items(rooms=self.rooms)

        self.officer = world.create_officer(npcs=self.npcs, rooms=self.rooms, room_graph=self.room_graph)
        self.judge = self.officer.judge
        #        self.active_npc = None

        # buttons
        self.menu_button = UIButton(pygame.Rect(1, 1, 100, 40), '[M] Menu', manager=self.ui_manager)
        self.exam_button_text = '[ENTER] "I\'ve found the murderer"'
        self.exam_button = UIButton(pygame.Rect(102, 1, 320, 40), self.exam_button_text, manager=self.ui_manager)

        _tutorial_button_text = '[H] Help'
        self.tutorial_botton = UIButton(pygame.Rect(422, 1, 100, 40), _tutorial_button_text, manager=self.ui_manager)

        # create tutorial window
        self.tutorial_window = world.create_tutorial_window(params=params, user=user)

    def _on_enter(self, current_state, mode: str):
        if mode == "exam":
            return State.GAME if current_state == State.EXAM else State.EXAM
        elif mode == "tutorial":
            if current_state == State.GAME:
                self.tutorial_window.open()
                return State.TUTORIAL
        else:
            raise ValueError(mode)

    def _update_buttons(self, current_state):
        if current_state == State.EXAM:
            self.exam_button.set_text('[ENTER] "I need to investigate more"')
        else:
            self.exam_button.set_text(self.exam_button_text)

        if current_state != State.GAME:
            self.tutorial_botton.disable()
        else:
            self.tutorial_botton.enable()

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

        if not self.tutorial_window.tutorial_has_been_opened:
            self.tutorial_window.draw_tutorial_request_text(screen)

        if self.tutorial_window.is_open:
            self.tutorial_window.draw(screen)

        if not self.chat_box.is_on:
            self.ui_manager.draw_ui(window_surface=screen)
        self.ui_manager.update(0.005)
        self.chat_box.ui_manager.update(0.005)

        if DRAW_GRID:
            draw_distance_grid(screen)

    def _handle_player_movement(self, event: Event):
        if event.type == KEYUP:
            if event.key == K_UP and self.player.dy == -1:
                self.player.dy = 0
            elif event.key == K_DOWN and self.player.dy == 1:
                self.player.dy = 0
            elif event.key == K_LEFT and self.player.dx == -1:
                self.player.dx = 0
            elif event.key == K_RIGHT and self.player.dx == 1:
                self.player.dx = 0

        if not event.type == KEYDOWN:
            return

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

            if self.tutorial_window.is_open:
                assert state == State.TUTORIAL
                self.tutorial_window.handle_tutorial_events(event)
            if not self.tutorial_window.is_open and state == State.TUTORIAL:
                return State.GAME

            # handle menu keys
            self.ui_manager.process_events(event)

            if self.chat_box.is_on:
                continue

            if event.type == KEYDOWN and event.key == K_m:
                return State.MENU
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return self._on_enter(state, mode="exam")
            elif event.type == KEYDOWN and event.key == K_h:
                return self._on_enter(state, mode="tutorial")

            # handle menu buttons
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.menu_button:
                    return State.MENU
                elif event.ui_element == self.exam_button:
                    return self._on_enter(state, mode="exam")
                elif event.ui_element == self.tutorial_botton:
                    return self._on_enter(state, mode="tutorial")

            self._handle_player_movement(event=event)

        self._update_buttons(current_state=state)

        return state


def game_loop():
    current_state = State.INTRO
    # current_state = State.MENU
    # current_state = State.END

    world = World(config_path=config_path)

    intro = world.create_info_screen(params=params)
    user = intro.get_default_user()
    if current_state == State.INTRO:
        user = intro.run_intro_and_user_name_entry(screen=screen)
        current_state = State.MENU

    bot = get_llm(LLM_MODE, user=user)

    game = Game(world=world, params=params, bot=bot, user=user)
    menu = Menu(params=params)
    end_screen = EndScreen(params=params)

    while True:
        if current_state == State.MENU:
            menu.draw(screen=screen)
            current_state = menu.handle_events(state=current_state)

        elif current_state in [State.GAME, State.EXAM, State.TUTORIAL]:
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
