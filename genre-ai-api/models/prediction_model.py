from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PredictionResult:
    filename: str
    predicted_genre: str
    confidence: float
    all_probabilities: Dict[str, float]

    @property
    def confidence_percentage(self) -> str:
        return f"{round(self.confidence * 100, 2)}%"