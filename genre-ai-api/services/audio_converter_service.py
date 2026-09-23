import os
import tempfile
from pydub import AudioSegment
from interfaces.iaudio_converter import IAudioConverter


class PydubAudioConverterService(IAudioConverter):
    def convert_to_wav(self, input_path: str, extension: str) -> str:
        if extension.lower() == ".wav":
            return input_path

        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_wav_path = tmp_wav.name
        tmp_wav.close()

        audio = AudioSegment.from_file(input_path)
        audio.export(tmp_wav_path, format="wav")
        return tmp_wav_path