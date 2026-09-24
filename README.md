# Genre AI

> Classificação inteligente de gêneros musicais utilizando Deep Learning e Processamento Digital de Sinais.

## Sobre o Projeto

O **Genre AI** permite que usuários enviem arquivos de áudio ou vídeo para identificar automaticamente o gênero musical predominante (entre 10 categorias). A API realiza o pré-processamento do sinal de áudio, divide a faixa em segmentos temporais, gera Mel-espectrogramas e alimenta um modelo de Rede Neural Convolucional (CNN) para calcular a probabilidade de cada gênero.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic
- **Machine Learning & Audio:** TensorFlow/Keras, Librosa, Pydub, NumPy
- **Infraestrutura & Deploy:** Docker, Docker Compose, Hugging Face Hub (Model Server)
- **Arquitetura:** Design Patterns (Controller-Service-Repository), SOLID, Dependency Inversion

## Arquitetura

```
genre-ai/
├── docker-compose.yml          # sobe o frontend (porta 3000)
├── genre-ai-api/               # backend FastAPI (porta 8000)
│   ├── main.py                 # app, lifespan e endpoints
│   ├── controllers/            # regra de negócio do predict
│   ├── services/               # conversão, features, classifier, download
│   ├── interfaces/             # ABCs (contratos)
│   ├── models/                 # dataclasses e schemas Pydantic
│   ├── tests/                  # suíte pytest
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt / requirements-dev.txt
└── genre-ai-frontend/          # React 19 + CRA + Tailwind (porta 3000)
    ├── src/
    │   ├── App.js              # rotas / e /result
    │   ├── pages/Analyze.js    # upload e envio para /predict
    │   ├── pages/Result.js     # gráfico de probabilidades
    │   ├── setupProxy.js       # proxy dev /predict -> API
    │   └── setupTests.js       # setup do Jest
    ├── .env.example / .env.test
    └── Dockerfile
```

### Fluxo

1. Frontend (`/`) faz upload de arquivo de áudio.
2. `POST /predict` passa pelo proxy do dev server até a API.
3. `PredictController` valida extensão → converte para WAV → extrai mel-spectrogramas → classifica.
4. Resposta com gênero previsto, confiança e probabilidades de todos os gêneros.
5. Frontend renderiza o resultado em `/result`.

**Gêneros suportados:** blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock.

**Extensões aceitas:** `.mp3` `.wav` `.mp4` `.ogg` `.flac` `.m4a` `.aac` `.mkv`

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.11+ (testado em 3.12) |
| Node.js | 18+ |
| npm | 9+ |
| ffmpeg | qualquer (necessário para converter áudios que não sejam `.wav`) |
| Docker + Docker Compose *(opcional)* | para rodar o frontend em container |

---

## Variáveis de ambiente (`.env`)

Os arquivos **reais** `.env` são ignorados pelo Git. Use sempre os `.env.example` como referência e copie-os antes de rodar.

### Backend — `genre-ai-api/`

Criar `genre-ai-api/.env` a partir de `genre-ai-api/.env.example`:

| Variável | Obrigatória | Descrição | Default |
|---|---|---|---|
| `MODEL_URL` | Não | URL do modelo `.keras` baixado no startup (se o arquivo local não existir) | HuggingFace `uiltong1/generos-musicais-cnn` |
| `CONFIG_URL` | Não | URL do JSON de configuração (labels e normalização) | HuggingFace `uiltong1/generos-musicais-cnn` |

```bash
cd genre-ai-api
cp .env.example .env
# edite .env se quiser apontar para URLs internas/mirror
```

> Os arquivos `modelo_generos_musicais.keras` e `config_modelo.json` no diretório da API têm precedência: se existirem, o download não acontece. Ambos são ignorados pelo Git (binário pesado + config).

### Frontend — `genre-ai-frontend/`

Criar `genre-ai-frontend/.env` a partir de `genre-ai-frontend/.env.example`:

| Variável | Obrigatória | Descrição | Default |
|---|---|---|---|
| `REACT_APP_API_HOST` | Sim | Host da API usado pelo proxy do dev server (`src/setupProxy.js`) | `http://host.docker.internal:8000` no código |
| `REACT_APP_N8N_AUTH` | Não | Token n8n (hoje não é lido pelo código do app) | vazio |

```bash
cd genre-ai-frontend
cp .env.example .env
```

| Ambiente | Arquivo | Quando é carregado |
|---|---|---|
| Desenvolvimento | `.env` | `npm start` / `docker compose up` |
| Testes (Jest) | `.env.test` | `npm test` / `npm run test:ci` (commitado) |
| Local (não commitar) | `.env.local`, `.env.test.local` | sobrescreve os anteriores |

**Docker:** o `docker-compose.yml` usa `env_file: ./genre-ai-frontend/.env` — o arquivo precisa existir antes de subir o container.

**Proxy:** em dev, o frontend chama `fetch('/predict', ...)` (caminho relativo). O `setupProxy.js` encaminha para `REACT_APP_API_HOST`. Assim, em máquina local use `http://localhost:8000`; em Docker, `http://host.docker.internal:8000`.

---

## Como executar a aplicação

### Opção A — Docker (frontend) + API local

```bash
# 1. Backend
cd genre-ai-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Frontend (em outro terminal, na raiz do projeto)
cd genre-ai-frontend
cp .env.example .env   # se ainda não existir
docker compose up --build
# -> http://localhost:3000
```

### Opção B — Tudo local (sem Docker)

```bash
# Backend
cd genre-ai-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (em outro terminal)
cd genre-ai-frontend
cp .env.example .env
# ajuste REACT_APP_API_HOST=http://localhost:8000
npm install
npm start
# -> http://localhost:3000
```

### Verificar que a API está no ar

```bash
curl http://localhost:8000/
# {"status":"online","message":"Envie um arquivo para POST /predict para classificar o gênero."}
```

Docs interativas: [http://localhost:8000/docs](http://localhost:8000/docs)

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Health/status |
| `POST` | `/predict` | Classifica o gênero. Campo `file` (multipart) |

**Sucesso (`200`):**

```json
{
  "filename": "musica.mp3",
  "predicted_genre": "rock",
  "confidence": 0.9234,
  "confidence_percentage": "92.34%",
  "all_probabilities": { "rock": 0.9234, "pop": 0.0512, "metal": 0.0254 }
}
```

**Erros:**

| Código | Quando |
|---|---|
| `400` | Extensão não suportada |
| `422` | Arquivo ausente / áudio inválido (`ValueError`) |
| `500` | Falha inesperada no processamento |

Exemplo:

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@minha-musica.mp3"
```

### Rotas do frontend

| Rota | Página |
|---|---|
| `/` | Upload e análise (`Analyze`) |
| `/result` | Resultado com gráfico (`Result`) — precisa de `location.state`; sem estado, redireciona para `/` |

---

## Testes

### Backend (pytest)

```bash
cd genre-ai-api
source venv/bin/activate
pip install -r requirements-dev.txt   # pytest + httpx (uma vez)

pytest                                # roda a suíte
```

**Cobertura no terminal:**

```bash
pytest --cov=. --cov-report=term-missing
```

Ou só o código de produção (sem `tests/`):

```bash
pytest --cov=controllers --cov=models --cov=services --cov=main --cov-report=term-missing
```

**HTML:**

```bash
pytest --cov=. --cov-report=html
# abra htmlcov/index.html
```

Cobertura atual ~**97%** (87 testes). A principal lacuna é o `lifespan` do `main.py`, que carrega o modelo Keras real — os testes usam mocks e não baixam rede nem carregam o modelo de 43 MB.

Arquivos:

| Arquivo | Cobre |
|---|---|
| `tests/test_predict_controller.py` | validação de extensão, pipeline, erros 422/500, limpeza de temp files |
| `tests/test_api.py` | `GET /`, `POST /predict` (200/400/422/500) via TestClient |
| `tests/test_config_loader_service.py` | carga do JSON de configuração |
| `tests/test_http_model_downloader_service.py` | download condicional de modelo/config |
| `tests/test_audio_converter_service.py` | conversão WAV/pydub |
| `tests/test_audio_processor_service.py` | features com librosa (mock) |
| `tests/test_genre_classifier_service.py` | lógica de predição Keras (mock) |
| `tests/test_models.py` | dataclasses, schema Pydantic |

Config: `pytest.ini` (`testpaths = tests`, `pythonpath = .`).

> Os testes **não** exigem `ffmpeg`, TensorFlow carregado nem rede — dependências pesadas são mockadas.

### Frontend (Jest + React Testing Library)

```bash
cd genre-ai-frontend
npm install          # uma vez

npm test             # watch mode (interativo)
npm run test:ci      # uma vez, saída única (CI/local)
```

**Cobertura:**

```bash
CI=true npm test -- --coverage --watchAll=false
```

Cobertura atual: **13 testes** em 3 arquivos.

| Arquivo | Cobre |
|---|---|
| `src/App.test.js` | rota inicial renderiza `Analyze` |
| `src/pages/Analyze.test.js` | upload, extensão inválida, sem arquivo, sucesso no `/predict`, erros 422/500/502, falha de rede |
| `src/pages/Result.test.js` | dados do resultado, gêneros no gráfico, botão Voltar, redirect sem estado |

Setup: `src/setupTests.js` (jest-dom, polyfill `TextEncoder`/`ResizeObserver`, mock global de `fetch`). O `.env.test` fornece `REACT_APP_*` no ambiente de teste.

Config extra no `package.json`: `moduleNameMapper` para `react-router/dom` (compatibilidade Jest 27 / react-router v7) e script `test:ci`.

Lint:

```bash
npx eslint src/
```

---

## Estrutura de testes resumida

```bash
# Backend
cd genre-ai-api && ./venv/bin/pytest --cov=. --cov-report=term-missing

# Frontend
cd genre-ai-frontend && npm run test:ci
```

---

## Solução de problemas

| Problema | Solução |
|---|---|
| `ModuleNotFoundError: httpx` no backend | `pip install -r requirements-dev.txt` |
| Frontend: `Cannot find module 'react-router/dom'` | Já resolvido via `moduleNameMapper` no `package.json` — rode `npm install` |
| `fetch` falha do browser | Confira `REACT_APP_API_HOST` no `.env` e se a API está na porta 8000 |
| Conversão de áudio falha | Instale `ffmpeg` (`sudo apt install ffmpeg` ou use a imagem Docker da API) |
| Modelo não baixa no startup | Verifique `MODEL_URL`/`CONFIG_URL` ou coloque os arquivos localmente |
| Testes de end-to-end sem modelo | Os testes unitários usam mocks; para testar o modelo real, rode a API e envie um áudio via `/docs` |
| `docker compose up` falha | Garanta que `genre-ai-frontend/.env` existe (`cp .env.example .env`) |

---

## Stack

**Backend:** Python · FastAPI · TensorFlow/Keras · librosa · pydub · Pydantic · pytest

**Frontend:** React 19 · Create React App · React Router 7 · Tailwind CSS 3 · Recharts · Jest + React Testing Library

**Infra:** Docker · Docker Compose · uvicorn
