from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import main
from models.schemas.predict_schema import PredictResponseSchema


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def stub_controller(monkeypatch):
    controller = MagicMock()
    controller.predict.return_value = PredictResponseSchema(
        filename="musica.mp3",
        predicted_genre="rock",
        confidence=0.9234,
        confidence_percentage="92.34%",
        all_probabilities={"rock": 0.9234, "pop": 0.0512, "metal": 0.0254},
    )
    monkeypatch.setattr(main.Container, "predict_controller", controller)
    return controller


class TestHomeEndpoint:
    def test_returns_online_status(self, client):
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "POST /predict" in data["message"]


class TestPredictEndpointValidation:
    def test_missing_file_returns_422(self, client):
        response = client.post("/predict")

        assert response.status_code == 422

    def test_unsupported_extension_returns_400(
        self, client, config, mock_converter, mock_processor, mock_classifier, monkeypatch
    ):
        import main
        from controllers.predict_controller import PredictController

        real_controller = PredictController(
            converter=mock_converter,
            processor=mock_processor,
            classifier=mock_classifier,
            config=config,
        )
        monkeypatch.setattr(main.Container, "predict_controller", real_controller)

        response = client.post(
            "/predict",
            files={"file": ("documento.txt", b"conteudo", "text/plain")},
        )

        assert response.status_code == 400
        assert ".txt" in response.json()["detail"]
        mock_converter.convert_to_wav.assert_not_called()

    def test_missing_file_field_returns_422(self, client, stub_controller):
        response = client.post("/predict", data={"other": "value"})

        assert response.status_code == 422
        stub_controller.predict.assert_not_called()


class TestPredictEndpointSuccess:
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
    def test_allowed_extensions_reach_controller(
        self, client, stub_controller, filename
    ):
        response = client.post(
            "/predict",
            files={"file": (filename, b"fake-audio", "application/octet-stream")},
        )

        assert response.status_code == 200
        stub_controller.predict.assert_called_once()

    def test_returns_predicted_payload(self, client, stub_controller):
        response = client.post(
            "/predict",
            files={"file": ("musica.mp3", b"fake-audio", "audio/mpeg")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "musica.mp3"
        assert data["predicted_genre"] == "rock"
        assert data["confidence"] == 0.9234
        assert data["confidence_percentage"] == "92.34%"
        assert data["all_probabilities"]["rock"] == 0.9234
        assert set(data["all_probabilities"]) == {"rock", "pop", "metal"}

    def test_upload_file_is_passed_to_controller(self, client, stub_controller):
        content = b"conteudo-do-arquivo"

        client.post(
            "/predict",
            files={"file": ("musica.mp3", content, "audio/mpeg")},
        )

        upload = stub_controller.predict.call_args[0][0]
        assert upload.filename == "musica.mp3"


class TestPredictEndpointErrors:
    def test_controller_value_error_returns_422(self, client, stub_controller):
        from fastapi import HTTPException

        stub_controller.predict.side_effect = HTTPException(
            status_code=422, detail="O áudio é muito curto"
        )

        response = client.post(
            "/predict",
            files={"file": ("musica.mp3", b"fake-audio", "audio/mpeg")},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "O áudio é muito curto"

    def test_controller_runtime_error_bubbles_up(self, client, stub_controller):
        stub_controller.predict.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            client.post(
                "/predict",
                files={"file": ("musica.mp3", b"fake-audio", "audio/mpeg")},
            )

    def test_controller_http_exception_is_returned(self, client, stub_controller):
        from fastapi import HTTPException

        stub_controller.predict.side_effect = HTTPException(
            status_code=500, detail="Erro ao processar o áudio: boom"
        )

        response = client.post(
            "/predict",
            files={"file": ("musica.mp3", b"fake-audio", "audio/mpeg")},
        )

        assert response.status_code == 500
        assert "Erro ao processar" in response.json()["detail"]


class TestContainerState:
    def test_predict_fails_without_lifespan_initialization(self, monkeypatch):
        monkeypatch.setattr(main.Container, "predict_controller", None)
        client = TestClient(main.app, raise_server_exceptions=False)

        response = client.post(
            "/predict",
            files={"file": ("musica.mp3", b"fake-audio", "audio/mpeg")},
        )

        assert response.status_code == 500

    def test_app_metadata(self):
        assert main.app.title == "API de Classificação de Gêneros Musicais"
        assert main.app.version == "2.3.0"

    def test_model_and_config_paths(self):
        assert main.MODEL_LOCAL_PATH == "modelo_generos_musicais.keras"
        assert main.CONFIG_LOCAL_PATH == "config_modelo.json"
