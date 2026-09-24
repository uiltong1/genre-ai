from unittest.mock import MagicMock

import numpy as np
import pytest

from models.config_model import ModelConfig
from services.genre_classifier_service import KerasGenreClassifierService


@pytest.fixture
def config():
    return ModelConfig(genre_names=["blues", "rock", "pop"], mean=0.0, std=1.0)


def make_service(predictions: np.ndarray) -> KerasGenreClassifierService:
    service = object.__new__(KerasGenreClassifierService)
    service.model = MagicMock()
    service.model.predict.return_value = predictions
    return service


class TestKerasGenreClassifierService:
    def test_raises_file_not_found_when_model_is_missing(self, tmp_path):
        missing = str(tmp_path / "nao_existe.keras")

        with pytest.raises(FileNotFoundError) as exc_info:
            KerasGenreClassifierService(missing)

        assert missing in str(exc_info.value)

    def test_predict_averages_segments_and_selects_top_genre(self, config):
        predictions = np.array(
            [
                [0.1, 0.7, 0.2],
                [0.2, 0.6, 0.2],
            ]
        )
        service = make_service(predictions)

        result = service.predict(
            features=np.zeros((2, 128, 130, 1)),
            config=config,
            filename="musica.mp3",
        )

        service.model.predict.assert_called_once()
        assert result.predicted_genre == "rock"
        assert result.filename == "musica.mp3"
        assert result.confidence == pytest.approx(0.65)

    def test_probabilities_are_sorted_descending(self, config):
        predictions = np.array([[0.05, 0.1, 0.85]])
        service = make_service(predictions)

        result = service.predict(
            features=np.zeros((1, 128, 130, 1)),
            config=config,
            filename="a.mp3",
        )

        values = list(result.all_probabilities.values())
        assert values == sorted(values, reverse=True)
        assert list(result.all_probabilities.keys())[0] == "pop"

    def test_all_genres_are_present(self, config):
        predictions = np.array([[0.1, 0.3, 0.6]])
        service = make_service(predictions)

        result = service.predict(
            features=np.zeros((1, 128, 130, 1)),
            config=config,
            filename="a.mp3",
        )

        assert set(result.all_probabilities.keys()) == set(config.genre_names)
