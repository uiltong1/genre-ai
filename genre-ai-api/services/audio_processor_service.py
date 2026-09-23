import librosa
import numpy as np
from interfaces.iaudio_processor import IAudioProcessor
from models.config_model import ModelConfig


class LibrosaAudioProcessorService(IAudioProcessor):
    def __init__(
        self,
        sample_rate: int = 22050,
        duration: int = 30,
        segment_duration: int = 3,
    ):
        self.sample_rate = sample_rate
        self.duration = duration
        self.segment_duration = segment_duration

    def extract_features(self, wav_path: str, config: ModelConfig) -> np.ndarray:
        signal, sr = librosa.load(
            wav_path, sr=self.sample_rate, duration=self.duration
        )

        samples_per_segment = int(sr * self.segment_duration)
        num_segments = int(self.duration / self.segment_duration)
        spectrograms = []

        for s in range(num_segments):
            start = samples_per_segment * s
            finish = start + samples_per_segment
            segment = signal[start:finish]

            if len(segment) < samples_per_segment:
                break

            mel_spec = librosa.feature.melspectrogram(
                y=segment, sr=sr, n_fft=2048, hop_length=512, n_mels=128
            )
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

            if mel_spec_db.shape == (128, 130):
                spectrograms.append(mel_spec_db)

        if not spectrograms:
            raise ValueError(
                "O áudio é muito curto ou não gerou segmentos válidos."
            )

        spectrograms_arr = np.array(spectrograms)[..., np.newaxis]
        return (spectrograms_arr - config.mean) / config.std