from dataclasses import dataclass
from pathlib import Path

import pygame
import pygame_gui
from chat_box import ChatBox
from llm import get_llm

# from mystery.characters import CHARACTERS
from mystery.utils import Point2D
from npc import NPC
from params import Params
from pygame.locals import K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT
from world import World

# Initialize Pygame
pygame.init()
config_path = Path(__file__).resolve().parent.parent / "plot" / "business_of_murder" / "game_config.yaml"
params = Params.from_config(config_path)

# Set up the display

screen = pygame.display.set_mode((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT))
pygame.display.set_caption("Mystery Dinner")

ui_manager = pygame_gui.UIManager((params.WIDTH, params.HEIGHT + params.CHAT_HEIGHT), 'data/themes/theme_1.json')


# Define game states
MENU = 0
GAME = 1


bot = get_llm("local")
user = "Robin"


@dataclass
class Game:
    active_npc: NPC | None
    chat_box: ChatBox


def draw_menu():
    # TODO: Draw the menu screen, including buttons for starting the game and closing the application
    pass


def handle_menu_events():
    # TODO: Handle menu interactions, such as button clicks, to transition to the GAME state
    return True


def draw_game(player, room):
    screen.fill(room.background)
    # Draw player character
    player.draw(screen)

    # Draw NPCs
    for npc in room.npcs:
        npc.draw(screen)

    # Draw doors
    for door in room.doors:
        door.draw(screen)

    # Draw the chat frame
    for npc in room.npcs:
        if npc.chat_open:
            draw_chat_frame(screen, npc)


def draw_chat_frame(screen, npc: NPC | None = None):
    # TODO: Fix hack
    ui_manager.draw_ui(window_surface=screen)
    if (chat_image := npc.get_chat_image()) is not None:
        img_size = (int(params.WIDTH / 4 * 0.96), int(params.CHAT_HEIGHT * 0.96))
        img_pos = (int(0.02 * params.WIDTH / 4), int(params.HEIGHT + 0.02 * params.CHAT_HEIGHT))
        chat_image = pygame.transform.scale(chat_image, img_size)
        screen.blit(chat_image, img_pos)


def handle_game_events(game, player, room):
    for event in pygame.event.get():
        if event.type == QUIT:
            return False

        ui_manager.process_events(event)
        if game.chat_box.is_on:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                game.chat_box.close_chat()
            else:
                game.chat_box.handle_event(event)
                continue

        if event.type == KEYDOWN:
            if event.key == K_UP:
                player.dy = -1
            elif event.key == K_DOWN:
                player.dy = 1
            elif event.key == K_LEFT:
                player.dx = -1
            elif event.key == K_RIGHT:
                player.dx = 1
            elif event.key == K_SPACE:
                distances = [
                    ((player.pos.x - npc.pos.x) ** 2 + (player.pos.y - npc.pos.y) ** 2) ** 0.5 for npc in room.npcs
                ]
                if not distances:
                    continue
                closest_npc, distance = min(zip(room.npcs, distances), key=lambda x: x[1])
                if distance <= 2 * params.NPC_RADIUS:  # Adjust the distance as needed
                    print(f"Chatting with npc {closest_npc.name}")
                    game.chat_box.open_chat(closest_npc)

        if event.type == KEYUP:
            if event.key == K_UP and player.dy == -1:
                player.dy = 0
            elif event.key == K_DOWN and player.dy == 1:
                player.dy = 0
            elif event.key == K_LEFT and player.dx == -1:
                player.dx = 0
            elif event.key == K_RIGHT and player.dx == 1:
                player.dx = 0

    return True


def game_loop():
    world = World(config_path=config_path)
    player = world.create_player(params)
    rooms = world.create_rooms(params=params, bot=bot, user=user)
    current_room = world.get_starting_room()

    chat_box = ChatBox(
        ui_manager=ui_manager,
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
    game = Game(active_npc=None, chat_box=chat_box)

    state = GAME
    while True:
        if state == MENU:
            draw_menu()
            if not handle_menu_events():
                break

        elif state == GAME:
            room = rooms[current_room]
            if not handle_game_events(game, player, room):
                break
            current_room = player.move(room)
            draw_game(player, room)
        ui_manager.update(0.01)
        pygame.display.flip()


# Game loop
state = GAME
game_loop()

# Quit the game
pygame.quit()
