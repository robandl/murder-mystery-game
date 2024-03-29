from collections import namedtuple
from enum import Enum, auto
from pathlib import Path

from langchain import LLMChain
from langchain.prompts import PromptTemplate
from llm import Bot

Question = namedtuple("Question", ["question", "prompt"])


class JudgeState(Enum):
    IDLE = auto()
    PRE_EXAM = auto()
    EXAM = auto()
    POST_EXAM = auto()


class Judge:
    def __init__(
        self,
        bot: Bot,
        judge_path: Path,
        user: str,
        name: str = "Game-Judge",
    ):

        self.questions = self._load_questions(judge_path)
        self._num_attempts = 0
        self.points = {i: 0 for i in range(len(self.questions))}

        self.bot = bot
        self.stop_tokens = bot.config.stop_tokens
        self.name = name
        self.user = user

        self.chat_open = False
        self.chat_history = ""
        self.judge_state = JudgeState.IDLE
        self.current_question_id = 0

    def open_chat(self):
        self.chat_open = True
        self._pre_exam()
        self.judge_state = JudgeState.PRE_EXAM
        self.current_question_id = min(self.points, key=self.points.get)

    def close_chat(self):
        self.chat_open = False
        self.chat_history = ""
        self.judge_state = JudgeState.IDLE

    def load_chat_history(self) -> str:
        return self.chat_history

    def _load_questions(self, judge_path: Path) -> list[Question]:
        questions = []
        question_paths = sorted(list(judge_path.glob("*.txt")))
        for q_path in question_paths:
            with open(q_path, "r") as f:
                prompt = f.read().rstrip("\n")
            lines = prompt.split("\n")
            question = lines[0]
            prompt = '\n'.join(lines[2:])
            questions.append(Question(question, prompt))
        return questions

    def _pre_exam(self):
        msg = f"{self.name}: Detective {self.user}, are you ready to hand in your conclusion?\n"
        msg += "<font color=#E0C834>Warning: Giving wrong answers will result in points being deducted from your final score. </font>"
        msg += "<font color=#E0C834>Press [ESC] if you are not ready yet. Type `yes` if you know who the murderer is. </font>\n\n"
        self.chat_history += msg

    def _prepare_prompt(self, prompt):
        prompt = prompt.replace("{instruction_str}", self.bot.config.instruction_str)
        prompt = prompt.replace("{user_str}", self.bot.config.user_str)
        prompt = prompt.replace("{ai_str}", self.bot.config.ai_str)
        prompt = prompt.replace("{user}", self.user)
        return prompt

    #        full_user_name = self.bot.config.user_str
    #        if "{user}" in full_user_name:
    #            full_user_name.replace("{user}", user)

    def _eval_answer(self, user_msg):
        assert self.chat_open
        llm_prompt = self.questions[self.current_question_id].prompt
        prompt = self._prepare_prompt(llm_prompt)
        prompt = PromptTemplate(template=prompt, input_variables=["user_input"])
        self.llm_chain = LLMChain(llm=self.bot.llm, prompt=prompt, verbose=True)

        self.chat_history += f"Detective {self.user}: {user_msg}\n"

        ins = {"stop": self.stop_tokens, "user_input": user_msg}
        res = self.llm_chain(ins)
        answer = res["text"].lstrip()
        if "<passed>" in answer:
            answer = answer.replace("<passed>", "").lstrip(" ")
            self.chat_history += f"{self.name}: {answer}\n"
            points = f"{sum(self.points.values())+1}/{len(self.points)}"
            self.chat_history += f"<font color=#E0C834>Your answer was correct. Points: {points}.</font>\n\n"
            return True
        answer = answer.replace("<failed>", "").lstrip(" ")
        self.chat_history += f"{self.name}: {answer}\n"
        points = f"{sum(self.points.values())}/{len(self.points)}"
        self.chat_history += f"<font color=#E0C834>Your answer was not correct. Points: {points}.</font>\n\n"
        return False

    def _ask_question(self):
        self.chat_history += f"{self.name}: {self.questions[self.current_question_id].question}"

    def chat(self, new_message):
        if self.judge_state == JudgeState.PRE_EXAM:
            # TODO: For now, any `new_message` will be treated as a confirmation to start the exam
            self._ask_question()
            self.judge_state = JudgeState.EXAM
            self._num_attempts += 1
        elif self.judge_state == JudgeState.EXAM:
            if self._eval_answer(new_message):
                self.points[self.current_question_id] = 1

            if sum(self.points.values()) == len(self.points):
                self.chat_history += "<font color=#E0C834>Congratulations, you have won the game!</font>\n\n"

            elif self.current_question_id < len(self.questions) - 1:
                self.current_question_id += 1
                self._ask_question()
            elif self.current_question_id == len(self.questions) - 1:
                self.judge_state == JudgeState.POST_EXAM

        return self.chat_history

    def get_chat_image(self):
        return None

    def get_figure_image(self):
        return None

    @property
    def is_game_won(self) -> bool:
        return sum(self.points.values()) == len(self.points)

    @property
    def num_attempts(self) -> int:
        return self._num_attempts
