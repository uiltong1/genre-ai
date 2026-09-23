import os
import urllib.request
from interfaces.imodel_downloader import IModelDownloader


class HttpModelDownloaderService(IModelDownloader):
    def __init__(self, model_url: str, config_url: str):
        self.model_url = model_url
        self.config_url = config_url

    def _download_file(self, url: str, destination_path: str) -> None:
        print(f"Baixando artefato de {url} ...")
        urllib.request.urlretrieve(url, destination_path)
        print(f"✅ Arquivo salvo em: {destination_path}")

    def ensure_model_files(self, model_path: str, config_path: str) -> None:
        if not os.path.exists(config_path):
            print(f"Arquivo '{config_path}' não encontrado localmente.")
            self._download_file(self.config_url, config_path)
        else:
            print(f"✅ Arquivo '{config_path}' já existe localmente.")

        if not os.path.exists(model_path):
            print(f"Modelo '{model_path}' não encontrado localmente.")
            self._download_file(self.model_url, model_path)
        else:
            print(f"✅ Modelo '{model_path}' já existe localmente.")