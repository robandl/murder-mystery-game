import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import pygame
from langchain import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from llm import Bot, LlmConfig
from pygame.surface import Surface
from room import Room
from utils import GREEN, WHITE, Point2D, draw_contour


def load_contour_image(img_path: Path) -> Surface:
    img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
    img_with_contour = draw_contour(img, thickness=20)
    # TODO: how to load surface directly from numpy with alpha channel?
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img_with_contour)
        return pygame.image.load(f.name)


@dataclass
class NPC:
    name: str
    pos: Point2D
    room: Room
    chat_history: str = ""
    chat_open: bool = False

    def draw(self, screen):

        if self.get_figure_image() is None:
            color = GREEN if self.chat_open else WHITE
            pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), 20)
            return

        # TODO: remove hardcode
        img_size = self.get_image_size()
        img_pos = (
            int(self.pos.x - img_size[0] / 2),
            int(self.pos.y - img_size[0] / 2),
        )
        figure_image = pygame.transform.scale(self.get_figure_image(), img_size)
        screen.blit(figure_image, img_pos)

    def open_chat(self):
        self.chat_open = True

    def close_chat(self):
        self.chat_open = False

    def load_chat_history(self) -> str:
        return self.chat_history

    def chat(self, new_message):
        assert self.chat_open

        self.chat_history += f"Player: {new_message}\n"

        answer = f"{self.name}: Answer\n"
        self.chat_history += answer

        return self.chat_history

    def get_chat_image(self):
        return None

    def get_figure_image(self):
        return None

    def get_image_size(self):
        return None


class LlmNPC(NPC):
    def __init__(
        self,
        bot: Bot,
        prompt_path,
        user,
        chat_img: Optional[Path] = None,
        figure_img: Optional[Path] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bot = bot

        prompt = self._load_prompt(prompt_path=prompt_path, config=bot.config, user=user)

        verbose = True
        prompt = PromptTemplate(template=prompt, input_variables=["user_input", "history"])
        full_user_name = bot.config.user_str
        if "{user}" in full_user_name:
            full_user_name.replace("{user}", user)
        memory = ConversationBufferWindowMemory(
            k=3, human_prefix=full_user_name, ai_prefix=bot.config.ai_str, memory_key="history", input_key="user_input"
        )
        self.llm_chain = LLMChain(llm=bot.llm, prompt=prompt, verbose=verbose, memory=memory)
        self.user = user
        self._stop_tokens = bot.config.stop_tokens

        self._chat_image = None
        if chat_img is not None:
            self._chat_image = pygame.image.load(chat_img)
        self._figure_image = None
        if figure_img is not None:
            self._figure_image = load_contour_image(figure_img)

    def _load_prompt(self, prompt_path, config: LlmConfig, user: str):
        with open(prompt_path, 'r') as file:
            prompt = file.read().rstrip("\n")

        prompt = prompt.replace("{instruction_str}", config.instruction_str)
        prompt = prompt.replace("{user_str}", config.user_str)
        prompt = prompt.replace("{ai_str}", config.ai_str)
        prompt = prompt.replace("{user}", user)
        return prompt

    def open_chat(self):
        self.chat_history += f"<font color=#E0C834>You're talking with {self.name}.\n</font>"
        return super().open_chat()

    def chat(self, new_message):
        assert self.chat_open
        self.chat_history += f"Detective {self.user}: {new_message}\n"

        ins = {"stop": self._stop_tokens, "user_input": new_message}
        res = self.llm_chain(ins)
        answer = res["text"].lstrip()

        answer = f"{self.name}: {answer}\n"
        self.chat_history += answer

        return self.chat_history

    def get_chat_image(self):
        return self._chat_image

    def get_figure_image(self):
        return self._figure_image

    def get_image_size(self):
        return [40, 60]
