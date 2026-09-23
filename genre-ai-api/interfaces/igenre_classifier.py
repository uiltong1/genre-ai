from abc import ABC, abstractmethod
import numpy as np
from models.config_model import ModelConfig
from models.prediction_model import PredictionResult


class IGenreClassifier(ABC):
    @abstractmethod
    def predict(
        self,
        features: np.ndarray,
        config: ModelConfig,
        filename: str,
    ) -> PredictionResult:
        pass