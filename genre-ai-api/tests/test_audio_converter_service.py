from unittest.mock import MagicMock, patch

import pytest

from services.audio_converter_service import PydubAudioConverterService


@pytest.fixture
def converter():
    return PydubAudioConverterService()


class TestPydubAudioConverterService:
    @pytest.mark.parametrize("extension", [".wav", ".WAV", ".Wav"])
    def test_wav_returns_same_path(self, converter, tmp_path, extension):
        source = tmp_path / f"arquivo{extension}"
        source.write_bytes(b"RIFF")

        result = converter.convert_to_wav(str(source), extension)

        assert result == str(source)

    @pytest.mark.parametrize("extension", [".mp3", ".ogg", ".flac", ".m4a"])
    def test_non_wav_creates_temp_wav(self, converter, tmp_path, extension):
        source = tmp_path / f"arquivo{extension}"
        source.write_bytes(b"audio")

        fake_audio = MagicMock()
        with patch(
            "services.audio_converter_service.AudioSegment.from_file",
            return_value=fake_audio,
        ) as from_file:
            result = converter.convert_to_wav(str(source), extension)

        from_file.assert_called_once_with(str(source))
        fake_audio.export.assert_called_once()
        assert result.endswith(".wav")
        assert result != str(source)
