from abc import ABC, abstractmethod


class IAudioConverter(ABC):
    @abstractmethod
    def convert_to_wav(self, input_path: str, extension: str) -> str:
        pass