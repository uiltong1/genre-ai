import json
import os
from interfaces.iconfig_loader import IConfigLoader
from models.config_model import ModelConfig


class JsonConfigLoaderService(IConfigLoader):
    def load_config(self, config_path: str) -> ModelConfig:
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {config_path}"
            )

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ModelConfig(
            genre_names=data["genre_names"],
            mean=float(data["mean"]),
            std=float(data["std"]),
        )