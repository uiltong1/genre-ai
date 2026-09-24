import io
from dataclasses import dataclass
from typing import Dict
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile

from controllers.predict_controller import PredictController
from models.config_model import ModelConfig
from models.prediction_model import PredictionResult
from models.schemas.predict_schema import PredictResponseSchema


SAMPLE_GENRES = [
    "blues",
    "classical",
    "country",
    "disco",
    "hiphop",
    "jazz",
    "metal",
    "pop",
    "reggae",
    "rock",
]


@pytest.fixture
def config() -> ModelConfig:
    return ModelConfig(
        genre_names=list(SAMPLE_GENRES),
        mean=-40.475101470947266,
        std=15.267413139343262,
    )


@pytest.fixture
def prediction_result() -> PredictionResult:
    probs: Dict[str, float] = {genre: 0.01 for genre in SAMPLE_GENRES}
    probs["rock"] = 0.91
    return PredictionResult(
        filename="musica.mp3",
        predicted_genre="rock",
        confidence=0.91,
        all_probabilities=dict(
            sorted(probs.items(), key=lambda item: item[1], reverse=True)
        ),
    )


@pytest.fixture
def mock_converter() -> MagicMock:
    converter = MagicMock()
    converter.convert_to_wav.side_effect = lambda path, ext: path
    return converter


@pytest.fixture
def mock_processor() -> MagicMock:
    processor = MagicMock()
    processor.extract_features.return_value = MagicMock()
    return processor


@pytest.fixture
def mock_classifier(prediction_result) -> MagicMock:
    classifier = MagicMock()
    classifier.predict.return_value = prediction_result
    return classifier


@pytest.fixture
def controller(config, mock_converter, mock_processor, mock_classifier) -> PredictController:
    return PredictController(
        converter=mock_converter,
        processor=mock_processor,
        classifier=mock_classifier,
        config=config,
    )


def make_upload(filename: str, content: bytes = b"fake-audio") -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)
