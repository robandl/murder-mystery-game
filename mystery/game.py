from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

import numpy as np
import pygame
import pygame_gui
from chat_box import ChatBox
from llm import get_llm
from mystery.characters import CHARACTERS
from mystery.utils import BLACK, BLUE, WHITE, Point2D
from npc import NPC, LlmNPC
from pygame.locals import K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
CHAT_HEIGHT = int(HEIGHT * 0.5)

screen = pygame.display.set_mode((WIDTH, HEIGHT + CHAT_HEIGHT))
pygame.display.set_caption("Mystery Dinner")

ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT + CHAT_HEIGHT), 'data/themes/theme_1.json')


# Define game states
MENU = 0
GAME = 1

terrain_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
# Set frame values to True
terrain_mask[:5, :] = True  # Top frame
terrain_mask[-5:, :] = True  # Bottom frame
terrain_mask[:, :5] = True  # Left frame
terrain_mask[:, -5:] = True  # Right frame

NPC_RADIUS = 40

bot = get_llm("local")
user = "Robin"


class RoomName(Enum):
    HALL = "HALL"
    BATHROOM = "BATHROOM"


@dataclass
class Rectangle:
    top_left: Point2D
    width: float
    height: float


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.speed = 0.25
        self.dx = 0
        self.dy = 0

    def move(self, room):
        new_pos = Point2D(self.pos.x + self.dx * self.speed, self.pos.y + self.dy * self.speed)

        if not (self.collides_with_terrain(new_pos, room.terrain_mask) or self.collides_with_npcs(new_pos, room.npcs)):
            self.pos = new_pos

        for door in room.doors:
            if self.collides_with_door(new_pos, door):
                return door.out_room

        return room.name

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), 20)

    def collides_with_terrain(self, pos, terrain_mask):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < terrain_mask.shape[1] and 0 <= y < terrain_mask.shape[0]:
            return terrain_mask[y, x]
        return False

    def collides_with_npcs(self, pos, npcs):
        for npc in npcs:
            if self.collides_with_single_npc(pos, npc):
                return True
        return False

    def collides_with_single_npc(self, pos, npc):
        distance = ((pos.x - npc.pos.x) ** 2 + (pos.y - npc.pos.y) ** 2) ** 0.5
        return distance <= NPC_RADIUS

    def collides_with_door(self, pos, door):
        return (
            door.rectangle.top_left.x <= pos.x <= door.rectangle.top_left.x + door.rectangle.width
            and door.rectangle.top_left.y <= pos.y <= door.rectangle.top_left.y + door.rectangle.height
        )


@dataclass
class Game:
    active_npc: NPC | None
    chat_box: ChatBox


@dataclass
class Door:
    rectangle: Rectangle
    in_room: RoomName
    out_room: RoomName

    color: Tuple

    def draw(self):
        pygame.draw.rect(
            screen,
            self.color,
            (
                int(self.rectangle.top_left.x),
                int(self.rectangle.top_left.y),
                int(self.rectangle.width),
                int(self.rectangle.height),
            ),
        )


def draw_menu():
    # TODO: Draw the menu screen, including buttons for starting the game and closing the application
    pass


def handle_menu_events():
    # TODO: Handle menu interactions, such as button clicks, to transition to the GAME state
    return True


def draw_game(player, room):
    screen.fill(room.background_color)
    # Draw player character
    player.draw()

    # Draw NPCs
    for npc in room.npcs:
        npc.draw(screen)

    # Draw doors
    for door in room.doors:
        door.draw()

    # Draw the chat frame
    for npc in room.npcs:
        if npc.chat_open:
            draw_chat_frame(npc)


def draw_chat_frame(npc: NPC | None = None):
    # TODO: Fix hack
    ui_manager.draw_ui(window_surface=screen)


@dataclass
class Room:
    name: RoomName
    npcs: List[NPC]
    doors: List[Door]
    terrain_mask: np.array
    background_color: Tuple


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
                for npc in room.npcs:
                    distance = ((player.pos.x - npc.pos.x) ** 2 + (player.pos.y - npc.pos.y) ** 2) ** 0.5
                    if distance > 2 * NPC_RADIUS:  # Adjust the distance as needed
                        continue
                    print(f"Chatting with npc {npc.name}")
                    game.chat_box.open_chat(npc)

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
    # Create player character
    player = Player(Point2D(WIDTH / 2, HEIGHT / 2))

    for name, char in CHARACTERS.items():
        char = LlmNPC(name=name, pos=char.pos, bot=bot, prompt_path=char.prompt_path, user=user)

    room_1 = Room(
        name=RoomName.HALL,
        npcs=[char, NPC("b", Point2D(200, 200))],
        doors=[
            Door(Rectangle(Point2D(350, 250), 40, 10), in_room=RoomName.HALL, out_room=RoomName.BATHROOM, color=WHITE)
        ],
        terrain_mask=terrain_mask,
        background_color=BLACK,
    )
    room_2 = Room(
        name=RoomName.BATHROOM,
        npcs=[NPC("a", Point2D(400, 500)), NPC("b", Point2D(500, 100))],
        doors=[
            Door(Rectangle(Point2D(150, 150), 40, 10), in_room=RoomName.BATHROOM, out_room=RoomName.HALL, color=WHITE)
        ],
        terrain_mask=terrain_mask,
        background_color=BLUE,
    )
    rooms = {RoomName.HALL: room_1, RoomName.BATHROOM: room_2}
    current_room = RoomName.HALL
    chat_box = ChatBox(
        ui_manager=ui_manager,
        text_rect=pygame.Rect(200, 600, 400, 200),
        input_rect=pygame.Rect(200, 800, 400, 100),
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
