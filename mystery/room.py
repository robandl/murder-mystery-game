from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from door import Door
from npc import NPC
from utils import RoomName


@dataclass
class Room:
    name: RoomName
    npcs: List[NPC]
    doors: List[Door]
    terrain: np.array
    background: Tuple
