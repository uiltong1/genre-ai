import dataclasses

import pytest

from models.config_model import ModelConfig
from models.prediction_model import PredictionResult
from models.schemas.predict_schema import PredictResponseSchema


class TestModelConfig:
    def test_is_frozen(self):
        config = ModelConfig(genre_names=["rock"], mean=0.0, std=1.0)

        with pytest.raises(dataclasses.FrozenInstanceError):
            config.mean = 1.0

    def test_holds_values(self):
        config = ModelConfig(genre_names=["a", "b"], mean=-1.5, std=2.5)

        assert config.genre_names == ["a", "b"]
        assert config.mean == -1.5
        assert config.std == 2.5


class TestPredictionResult:
    def test_is_frozen(self):
        result = PredictionResult(
            filename="a.mp3",
            predicted_genre="rock",
            confidence=0.5,
            all_probabilities={"rock": 0.5},
        )

        with pytest.raises(dataclasses.FrozenInstanceError):
            result.confidence = 1.0

    @pytest.mark.parametrize(
        ("confidence", "expected"),
        [
            (0.0, "0.0%"),
            (0.5, "50.0%"),
            (0.9234, "92.34%"),
            (1.0, "100.0%"),
            (0.12345, "12.35%"),
            (0.12344, "12.34%"),
        ],
    )
    def test_confidence_percentage(self, confidence, expected):
        result = PredictionResult(
            filename="a.mp3",
            predicted_genre="rock",
            confidence=confidence,
            all_probabilities={"rock": confidence},
        )

        assert result.confidence_percentage == expected


class TestPredictResponseSchema:
    def test_validates_successfully(self):
        schema = PredictResponseSchema(
            filename="musica.mp3",
            predicted_genre="rock",
            confidence=0.9234,
            confidence_percentage="92.34%",
            all_probabilities={"rock": 0.9234, "pop": 0.0766},
        )

        assert schema.filename == "musica.mp3"
        assert schema.predicted_genre == "rock"
        assert schema.confidence == 0.9234

    @pytest.mark.parametrize(
        "missing_field",
        [
            "filename",
            "predicted_genre",
            "confidence",
            "confidence_percentage",
            "all_probabilities",
        ],
    )
    def test_requires_all_fields(self, missing_field):
        payload = {
            "filename": "musica.mp3",
            "predicted_genre": "rock",
            "confidence": 0.9,
            "confidence_percentage": "90.0%",
            "all_probabilities": {"rock": 0.9},
        }
        del payload[missing_field]

        with pytest.raises(Exception):
            PredictResponseSchema(**payload)

    def test_from_prediction_result(self):
        result = PredictionResult(
            filename="musica.mp3",
            predicted_genre="rock",
            confidence=0.91,
            all_probabilities={"rock": 0.91, "pop": 0.09},
        )

        schema = PredictResponseSchema(
            filename=result.filename,
            predicted_genre=result.predicted_genre,
            confidence=round(result.confidence, 4),
            confidence_percentage=result.confidence_percentage,
            all_probabilities=result.all_probabilities,
        )

        assert schema.confidence_percentage == "91.0%"
