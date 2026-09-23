from abc import ABC, abstractmethod
import numpy as np
from models.config_model import ModelConfig


class IAudioProcessor(ABC):
    @abstractmethod
    def extract_features(self, wav_path: str, config: ModelConfig) -> np.ndarray:
        pass