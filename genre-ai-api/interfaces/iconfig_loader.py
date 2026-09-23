from abc import ABC, abstractmethod
from models.config_model import ModelConfig


class IConfigLoader(ABC):
    @abstractmethod
    def load_config(self, config_path: str) -> ModelConfig:
        pass