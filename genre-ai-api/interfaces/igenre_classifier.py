from abc import ABC, abstractmethod
import numpy as np
from models.domain.config_model import ModelConfig
from models.domain.prediction_model import PredictionResult


class IGenreClassifier(ABC):
    @abstractmethod
    def predict(
        self,
        features: np.ndarray,
        config: ModelConfig,
        filename: str,
    ) -> PredictionResult:
        pass