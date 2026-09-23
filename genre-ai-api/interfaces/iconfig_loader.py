from abc import ABC, abstractmethod
from models.domain.config_model import ModelConfig


class IConfigLoader(ABC):
    @abstractmethod
    def load_config(self, config_path: str) -> ModelConfig:
        pass