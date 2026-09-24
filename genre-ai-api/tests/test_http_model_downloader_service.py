from unittest.mock import MagicMock, call

import pytest

from services.http_model_downloader_service import HttpModelDownloaderService


@pytest.fixture
def downloader():
    return HttpModelDownloaderService(
        model_url="https://example.com/model.keras",
        config_url="https://example.com/config.json",
    )


class TestEnsureModelFiles:
    def test_downloads_both_when_missing(self, downloader, tmp_path, monkeypatch):
        download = MagicMock()
        monkeypatch.setattr(downloader, "_download_file", download)

        model_path = str(tmp_path / "model.keras")
        config_path = str(tmp_path / "config.json")

        downloader.ensure_model_files(model_path, config_path)

        assert download.call_args_list == [
            call("https://example.com/config.json", config_path),
            call("https://example.com/model.keras", model_path),
        ]

    def test_skips_download_when_files_exist(self, downloader, tmp_path, monkeypatch):
        download = MagicMock()
        monkeypatch.setattr(downloader, "_download_file", download)

        model_path = tmp_path / "model.keras"
        config_path = tmp_path / "config.json"
        model_path.write_bytes(b"model")
        config_path.write_text("{}")

        downloader.ensure_model_files(str(model_path), str(config_path))

        download.assert_not_called()

    def test_downloads_only_config_when_model_exists(self, downloader, tmp_path, monkeypatch):
        download = MagicMock()
        monkeypatch.setattr(downloader, "_download_file", download)

        model_path = tmp_path / "model.keras"
        config_path = tmp_path / "config.json"
        model_path.write_bytes(b"model")

        downloader.ensure_model_files(str(model_path), str(config_path))

        assert download.call_args_list == [
            call("https://example.com/config.json", str(config_path)),
        ]

    def test_downloads_only_model_when_config_exists(self, downloader, tmp_path, monkeypatch):
        download = MagicMock()
        monkeypatch.setattr(downloader, "_download_file", download)

        model_path = tmp_path / "model.keras"
        config_path = tmp_path / "config.json"
        config_path.write_text("{}")

        downloader.ensure_model_files(str(model_path), str(config_path))

        assert download.call_args_list == [
            call("https://example.com/model.keras", str(model_path)),
        ]

    def test_download_file_uses_urlretrieve(self, downloader, tmp_path, monkeypatch):
        urlretrieve = MagicMock()
        monkeypatch.setattr(
            "services.http_model_downloader_service.urllib.request.urlretrieve",
            urlretrieve,
        )

        destination = str(tmp_path / "arquivo.bin")
        downloader._download_file("https://example.com/arquivo", destination)

        urlretrieve.assert_called_once_with("https://example.com/arquivo", destination)
