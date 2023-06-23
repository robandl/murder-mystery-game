import numpy as np
import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NPC Interaction Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

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


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.speed = 0.25
        self.dx = 0
        self.dy = 0

    def move(self, npcs, terrain):
        new_pos = [self.pos[0] + self.dx * self.speed, self.pos[1] + self.dy * self.speed]

        if not (self.collides_with_terrain(new_pos, terrain_mask) or self.collides_with_npcs(new_pos, npcs)):
            self.pos = new_pos

    def draw(self):
        pygame.draw.circle(screen, WHITE, self.pos, 20)

    def collides_with_terrain(self, pos, terrain_mask):
        x, y = int(pos[0]), int(pos[1])
        if 0 <= x < terrain_mask.shape[1] and 0 <= y < terrain_mask.shape[0]:
            return terrain_mask[y, x]
        return False

    def collides_with_npcs(self, pos, npcs):
        for npc in npcs:
            if self.collides_with_single_npc(pos, npc):
                return True
        return False

    def collides_with_single_npc(self, pos, npc):
        distance = ((pos[0] - npc.pos[0]) ** 2 + (pos[1] - npc.pos[1]) ** 2) ** 0.5
        return distance <= NPC_RADIUS


class NPC:
    def __init__(self, name, pos):
        self.pos = pos
        self.name = name

    def draw(self):
        pygame.draw.circle(screen, WHITE, self.pos, 20)


def draw_menu():
    # TODO: Draw the menu screen, including buttons for starting the game and closing the application
    pass


def handle_menu_events():
    # TODO: Handle menu interactions, such as button clicks, to transition to the GAME state
    return True


def draw_game(player, npcs):
    # Draw player character
    player.draw()

    # Draw NPCs
    for npc in npcs:
        npc.draw()


def handle_game_events(player, npcs):
    for event in pygame.event.get():
        if event.type == QUIT:
            return False

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
                for npc in npcs:
                    distance = ((player.pos[0] - npc.pos[0]) ** 2 + (player.pos[1] - npc.pos[1]) ** 2) ** 0.5
                    if distance <= NPC_RADIUS:  # Adjust the distance as needed
                        # TODO: Open chat window and handle NPC interaction
                        print(f"Chatting with npc {npc.name}")

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
    player = Player([WIDTH / 2, HEIGHT / 2])

    # Create NPCs
    npcs = [NPC("a", (100, 100)), NPC("b", (200, 200))]

    state = GAME
    while True:
        if state == MENU:
            draw_menu()
            if not handle_menu_events():
                break

        elif state == GAME:
            if not handle_game_events(player, npcs):
                break

            player.move(npcs=npcs, terrain=terrain_mask)

            screen.fill(BLACK)
            draw_game(player, npcs)
            pygame.display.flip()


# Game loop
state = MENU
game_loop()

# Quit the game
pygame.quit()
