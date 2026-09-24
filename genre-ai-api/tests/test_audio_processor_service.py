from unittest.mock import patch

import numpy as np
import pytest

from models.config_model import ModelConfig
from services.audio_processor_service import LibrosaAudioProcessorService


@pytest.fixture
def config():
    return ModelConfig(
        genre_names=["rock"],
        mean=-40.0,
        std=15.0,
    )


@pytest.fixture
def processor():
    return LibrosaAudioProcessorService(
        sample_rate=22050,
        duration=30,
        segment_duration=3,
    )


def make_signal(seconds: float, sample_rate: int = 22050) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


class TestLibrosaAudioProcessorService:
    def test_raises_value_error_when_audio_is_too_short(self, processor, config):
        short_signal = make_signal(seconds=1.0)

        with patch(
            "services.audio_processor_service.librosa.load",
            return_value=(short_signal, 22050),
        ), patch(
            "services.audio_processor_service.librosa.feature.melspectrogram",
            return_value=np.zeros((128, 50)),
        ):
            with pytest.raises(ValueError, match="muito curto"):
                processor.extract_features("curta.wav", config)

    def test_raises_value_error_when_no_segment_has_expected_shape(
        self, processor, config
    ):
        signal = make_signal(seconds=30.0)

        with patch(
            "services.audio_processor_service.librosa.load",
            return_value=(signal, 22050),
        ), patch(
            "services.audio_processor_service.librosa.feature.melspectrogram",
            return_value=np.zeros((128, 100)),
        ):
            with pytest.raises(ValueError, match="segmentos válidos"):
                processor.extract_features("audio.wav", config)

    def test_returns_normalized_features_with_channel_dimension(
        self, processor, config
    ):
        signal = make_signal(seconds=30.0)
        mel = np.full((128, 130), -20.0)

        with patch(
            "services.audio_processor_service.librosa.load",
            return_value=(signal, 22050),
        ), patch(
            "services.audio_processor_service.librosa.feature.melspectrogram",
            return_value=mel,
        ), patch(
            "services.audio_processor_service.librosa.power_to_db",
            return_value=mel,
        ):
            features = processor.extract_features("audio.wav", config)

        assert features.shape == (10, 128, 130, 1)

        expected = (np.full((10, 128, 130, 1), -20.0) - config.mean) / config.std
        np.testing.assert_allclose(features, expected, rtol=1e-6)

    def test_skips_incomplete_final_segment(self, processor, config):
        signal = make_signal(seconds=9.5)
        mel = np.full((128, 130), -10.0)

        with patch(
            "services.audio_processor_service.librosa.load",
            return_value=(signal, 22050),
        ), patch(
            "services.audio_processor_service.librosa.feature.melspectrogram",
            return_value=mel,
        ), patch(
            "services.audio_processor_service.librosa.power_to_db",
            return_value=mel,
        ):
            features = processor.extract_features("audio.wav", config)

        assert features.shape[0] == 3
