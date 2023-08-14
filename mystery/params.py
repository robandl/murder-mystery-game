from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Params:
    WIDTH: int = 800
    HEIGHT: int = 600
    CHAT_HEIGHT: int = 300
    NPC_RADIUS: float = 40.0

    @classmethod
    def from_config(cls, config_path: Path) -> Params:
        with open(config_path, 'r') as file:
            config_params = yaml.safe_load(file)["settings"]

        params = {k.upper(): v for k, v in config_params.items()}
        return cls(**params)
