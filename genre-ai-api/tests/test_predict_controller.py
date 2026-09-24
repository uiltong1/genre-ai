import os
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from tests.conftest import make_upload


class TestExtensionValidation:
    def test_rejects_unsupported_extension(self, controller):
        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload("documento.txt"))

        assert exc_info.value.status_code == 400
        assert ".txt" in exc_info.value.detail
        assert "não suportada" in exc_info.value.detail

    @pytest.mark.parametrize(
        "filename",
        ["a.pdf", "a.doc", "a.zip", "a.exe", "a."],
    )
    def test_rejects_other_unsupported_extensions(self, controller, filename):
        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload(filename))

        assert exc_info.value.status_code == 400

    @pytest.mark.parametrize(
        "filename",
        [
            "musica.mp3",
            "musica.wav",
            "video.mp4",
            "musica.ogg",
            "musica.flac",
            "musica.m4a",
            "musica.aac",
            "video.mkv",
        ],
    )
    def test_accepts_allowed_extensions(self, controller, filename, mock_converter):
        controller.predict(make_upload(filename))
        mock_converter.convert_to_wav.assert_called_once()

    def test_extension_check_is_case_insensitive(self, controller, mock_converter):
        controller.predict(make_upload("MUSICA.MP3"))
        mock_converter.convert_to_wav.assert_called_once()


class TestSuccessPath:
    def test_returns_predict_response_schema(
        self, controller, prediction_result, mock_converter, mock_processor, mock_classifier
    ):
        result = controller.predict(make_upload("musica.mp3"))

        assert result.filename == "musica.mp3"
        assert result.predicted_genre == "rock"
        assert result.confidence == 0.91
        assert result.confidence_percentage == "91.0%"
        assert result.all_probabilities == prediction_result.all_probabilities

    def test_rounds_confidence_to_four_decimal_places(self, controller, mock_classifier):
        raw = controller.classifier.predict.return_value
        object.__setattr__(raw, "confidence", 0.123456789)

        result = controller.predict(make_upload("musica.mp3"))

        assert result.confidence == 0.1235

    def test_pipeline_is_executed_in_order(
        self, controller, mock_converter, mock_processor, mock_classifier, config
    ):
        controller.predict(make_upload("musica.mp3"))

        mock_converter.convert_to_wav.assert_called_once()
        wav_path = mock_converter.convert_to_wav.call_args[0][0]
        mock_processor.extract_features.assert_called_once_with(wav_path, config)
        mock_classifier.predict.assert_called_once_with(
            mock_processor.extract_features.return_value,
            config,
            "musica.mp3",
        )


class TestErrorMapping:
    def test_value_error_maps_to_422(self, controller, mock_converter):
        mock_converter.convert_to_wav.side_effect = ValueError(
            "O áudio é muito curto ou não gerou segmentos válidos."
        )

        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload("curta.mp3"))

        assert exc_info.value.status_code == 422
        assert "O áudio é muito curto" in exc_info.value.detail

    def test_value_error_from_processor_maps_to_422(self, controller, mock_processor):
        mock_processor.extract_features.side_effect = ValueError("duração inválida")

        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload("musica.mp3"))

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail == "duração inválida"

    def test_generic_exception_maps_to_500(self, controller, mock_converter):
        mock_converter.convert_to_wav.side_effect = RuntimeError("ffmpeg quebrou")

        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload("musica.mp3"))

        assert exc_info.value.status_code == 500
        assert "Erro ao processar o áudio" in exc_info.value.detail
        assert "ffmpeg quebrou" in exc_info.value.detail

    def test_classifier_exception_maps_to_500(self, controller, mock_classifier):
        mock_classifier.predict.side_effect = OSError("modelo corrompido")

        with pytest.raises(HTTPException) as exc_info:
            controller.predict(make_upload("musica.mp3"))

        assert exc_info.value.status_code == 500


class TestTempFileCleanup:
    def test_removes_temp_files_after_success(self, controller, mock_converter):
        controller.predict(make_upload("musica.mp3"))

        original_path = mock_converter.convert_to_wav.call_args[0][0]
        assert not os.path.exists(original_path)

    def test_removes_temp_files_after_value_error(self, controller, mock_converter):
        mock_converter.convert_to_wav.side_effect = ValueError("falhou")

        with pytest.raises(HTTPException):
            controller.predict(make_upload("musica.mp3"))

        original_path = mock_converter.convert_to_wav.call_args[0][0]
        assert not os.path.exists(original_path)

    def test_removes_temp_files_after_generic_error(self, controller, mock_converter):
        mock_converter.convert_to_wav.side_effect = RuntimeError("falhou")

        with pytest.raises(HTTPException):
            controller.predict(make_upload("musica.mp3"))

        original_path = mock_converter.convert_to_wav.call_args[0][0]
        assert not os.path.exists(original_path)

    def test_removes_converted_wav_when_different_from_original(
        self, controller, mock_converter, tmp_path
    ):
        separate_wav = tmp_path / "converted.wav"
        separate_wav.write_bytes(b"RIFFwav")

        original_paths = []

        def convert(input_path, ext):
            original_paths.append(input_path)
            return str(separate_wav)

        mock_converter.convert_to_wav.side_effect = convert

        controller.predict(make_upload("musica.mp3"))

        assert not os.path.exists(original_paths[0])
        assert not separate_wav.exists()
