from abc import ABC, abstractmethod


class IModelDownloader(ABC):
    @abstractmethod
    def ensure_model_files(self, model_path: str, config_path: str) -> None:
        """Garante que os arquivos do modelo e config estejam disponíveis localmente."""
        pass