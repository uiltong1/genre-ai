from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModelConfig:
    genre_names: List[str]
    mean: float
    std: float