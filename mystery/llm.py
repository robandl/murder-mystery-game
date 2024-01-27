from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from langchain.llms.base import LLM

HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'


@dataclass
class LlmConfig:
    user_str: str  # string to begin the query
    ai_str: str  # string to begin the model response
    instruction_str: str = ""  # string to begin the instruction block
    stop_tokens: Optional[List[str]] = None


@dataclass
class Bot:
    llm: LLM
    config: LlmConfig


class LocalLlm(LLM):
    def __init__(self, stop_tokens: Optional[List[str]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:

        response = requests.post(
            URI,
            json={
                "prompt": prompt,
                "temperature": 0.01,
                "max_new_tokens": 200,
                "early_stopping": False,
                "stopping_strings": stop,
                'do_sample': True,
                'top_p': 0.9,
                'typical_p': 1,
                'repetition_penalty': 1.15,
                'top_k': 20,
                'min_length': 0,
                'no_repeat_ngram_size': 0,
                'num_beams': 1,
                'penalty_alpha': 0,
                'length_penalty': 1,
                'seed': -1,
                'add_bos_token': True,
                'truncation_length': 2000,
                'ban_eos_token': False,
                'skip_special_tokens': True,
            },
        )
        response.raise_for_status()
        return response.json()['results'][0]['text']

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {}


def get_llm(model: str) -> Bot:
    if model == "chat_gpt":
        from langchain import OpenAI

        return Bot(
            llm=OpenAI(temperature=0),
            config=LlmConfig(
                user_str="Detective {user}", ai_str="You", instruction_str="Instructions:", stop_tokens=["Detective"]
            ),
        )
    elif model == "local":
        stop_tokens = ["###", "Input"]
        return Bot(
            llm=LocalLlm(stop_tokens=stop_tokens),
            config=LlmConfig(
                # TheBloke_Nous-Hermes-13B-GPTQ
                user_str="### Input",
                ai_str="### Response",
                instruction_str="### Instruction",
                stop_tokens=stop_tokens,
            ),
        )
    else:
        raise NotImplementedError(model)
