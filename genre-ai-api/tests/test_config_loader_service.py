import json

import pytest

from services.config_loader_service import JsonConfigLoaderService


@pytest.fixture
def loader():
    return JsonConfigLoaderService()


class TestJsonConfigLoaderService:
    def test_raises_file_not_found_when_path_is_missing(self, loader, tmp_path):
        missing = tmp_path / "nao_existe.json"

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_config(str(missing))

        assert str(missing) in str(exc_info.value)

    def test_loads_valid_config(self, loader, tmp_path):
        path = tmp_path / "config_modelo.json"
        path.write_text(
            json.dumps(
                {
                    "genre_names": ["rock", "pop"],
                    "mean": -40.5,
                    "std": 15.25,
                }
            ),
            encoding="utf-8",
        )

        config = loader.load_config(str(path))

        assert config.genre_names == ["rock", "pop"]
        assert config.mean == -40.5
        assert config.std == 15.25

    def test_coerces_mean_and_std_to_float(self, loader, tmp_path):
        path = tmp_path / "config.json"
        path.write_text(
            json.dumps({"genre_names": ["rock"], "mean": "1", "std": "2"}),
            encoding="utf-8",
        )

        config = loader.load_config(str(path))

        assert isinstance(config.mean, float)
        assert isinstance(config.std, float)

    def test_raises_key_error_when_keys_are_missing(self, loader, tmp_path):
        path = tmp_path / "config.json"
        path.write_text(json.dumps({"genre_names": ["rock"]}), encoding="utf-8")

        with pytest.raises(KeyError):
            loader.load_config(str(path))

    def test_loads_real_project_config(self, loader):
        config = loader.load_config("config_modelo.json")

        assert len(config.genre_names) == 10
        assert "rock" in config.genre_names
        assert config.mean < 0
        assert config.std > 0
