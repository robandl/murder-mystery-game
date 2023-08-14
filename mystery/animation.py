from enum import Enum
from pathlib import Path
from typing import List, Optional

import pygame
from utils import WHITE


class Direction(Enum):
    LEFT = 1
    RIGHT = 2


class Animation:
    def __init__(
        self, chat_img: Optional[Path] = None, figure_img: Optional[Path] = None, walking_sprites: Optional[Path] = None
    ):

        self.figure_size = (70, 140)
        self.chat_img = self._load_img(chat_img)
        self.figure_img = self._load_img(figure_img)
        self.last_update_time = pygame.time.get_ticks()

        self.current_frame = 0
        if walking_sprites and walking_sprites.is_dir():
            self.walking_sprites_imgs: List[pygame.Surface] = self._load_walking_sprites(walking_sprites)

        self.frame_duration = (
            1000 // len(self.walking_sprites_imgs) if walking_sprites and walking_sprites.is_dir() else 0
        )  # one walking cycle takes 1000 ms

    def _load_img(self, img_path: Optional[Path]) -> Optional[pygame.Surface]:
        if img_path is None:
            return
        img = pygame.image.load(str(img_path))
        img = pygame.transform.scale(img, self.figure_size)
        return img

    def _load_walking_sprites(self, dir_path: Path):
        walking_sprites_imgs = []
        for img_path in sorted(dir_path.iterdir()):
            if img_path.suffix in ['.png', '.jpg', '.jpeg']:
                walking_sprites_imgs.append(self._load_img(img_path))
        return walking_sprites_imgs

    def draw(self, screen, pos, direction: Optional[Direction] = None):
        current_time = pygame.time.get_ticks()

        if direction == Direction.RIGHT:
            if current_time - self.last_update_time > self.frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.walking_sprites_imgs)
                self.last_update_time = current_time
            img = self.walking_sprites_imgs[self.current_frame]

        elif direction == Direction.LEFT:
            if current_time - self.last_update_time > self.frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.walking_sprites_imgs)
                self.last_update_time = current_time
            img = pygame.transform.flip(self.walking_sprites_imgs[self.current_frame], True, False)

        else:
            if self.figure_img:
                img = self.figure_img
            elif self.walking_sprites_imgs:
                img = self.walking_sprites_imgs[0]
            else:
                pygame.draw.circle(screen, WHITE, (int(pos.x), int(pos.y)), 20)
                return

        rect = img.get_rect(center=(int(pos.x), int(pos.y)))
        screen.blit(img, rect.topleft)
