# Genre AI — Backend (API)

FastAPI + TensorFlow para classificação de gêneros musicais.

Documentação completa do projeto (roda, envs, testes): ver [README na raiz](../README.md).

## Variáveis de ambiente

```bash
cp .env.example .env
```

| Variável | Descrição | Default |
|---|---|---|
| `MODEL_URL` | URL do modelo `.keras` (download no startup se local ausente) | HuggingFace |
| `CONFIG_URL` | URL do `config_modelo.json` | HuggingFace |

Se `modelo_generos_musicais.keras` e `config_modelo.json` existirem no diretório, o download é pulado.

## Executar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

Docker:

```bash
docker build -t genre-ai-api .
docker run -p 8000:8000 genre-ai-api
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status |
| `POST` | `/predict` | Classifica arquivo de áudio (campo `file`) |

Extensões aceitas: `.mp3` `.wav` `.mp4` `.ogg` `.flac` `.m4a` `.aac` `.mkv`

Erros: `400` extensão · `422` áudio inválido · `500` falha interna.

## Testes

```bash
pip install -r requirements-dev.txt   # pytest + httpx

pytest                                              # 87 testes
pytest --cov=. --cov-report=term-missing            # cobertura no terminal
pytest --cov=. --cov-report=html                    # htmlcov/index.html
```

Os testes usam mocks (sem rede, sem carregar o modelo Keras real, sem ffmpeg).

| Arquivo | Cobre |
|---|---|
| `tests/test_predict_controller.py` | validação, pipeline, erros, temp files |
| `tests/test_api.py` | endpoints via TestClient |
| `tests/test_config_loader_service.py` | loader de config |
| `tests/test_http_model_downloader_service.py` | download de artefatos |
| `tests/test_audio_converter_service.py` | conversão pydub |
| `tests/test_audio_processor_service.py` | features librosa |
| `tests/test_genre_classifier_service.py` | classificador Keras |
| `tests/test_models.py` | dataclasses e schema |

Config: `pytest.ini`.

## Estrutura

```
main.py                 # app FastAPI, lifespan, endpoints
controllers/            # PredictController (validação + orquestração)
services/               # converter, processor, classifier, downloader, config loader
interfaces/             # ABCs
models/                 # ModelConfig, PredictionResult, PredictResponseSchema
tests/                  # suíte pytest
```
