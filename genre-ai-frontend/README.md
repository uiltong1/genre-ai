# Genre AI — Frontend

React 19 + Create React App + Tailwind CSS. Classifica gêneros musicais enviando áudio para a API.

Documentação completa do projeto (roda, envs, testes backend + frontend): ver [README na raiz](../README.md).

## Variáveis de ambiente

Copie o example antes de rodar:

```bash
cp .env.example .env
```

| Arquivo | Quando carrega | Commitado? |
|---|---|---|
| `.env.example` | referência | Sim |
| `.env` | `npm start` / Docker | Não (gitignored) |
| `.env.test` | `npm test` / `npm run test:ci` | Sim |
| `.env.local`, `.env.test.local` | sobrescreve os anteriores | Não |

| Variável | Descrição |
|---|---|
| `REACT_APP_API_HOST` | Host da API no proxy do dev server (`src/setupProxy.js`) |
| `REACT_APP_N8N_AUTH` | Opcional, token n8n (não usado pelo código atual) |

## Scripts

```bash
npm install

npm start         # dev server -> http://localhost:3000
npm run build     # build de produção em build/
npm test          # Jest em watch mode
npm run test:ci   # Jest uma vez (CI)
npx eslint src/   # lint
```

## Testes com cobertura

```bash
CI=true npm test -- --coverage --watchAll=false
```

- `src/setupTests.js` — jest-dom, polyfills e mock global de `fetch`
- 13 testes: `App.test.js`, `pages/Analyze.test.js`, `pages/Result.test.js`

## Rotas

| Rota | Página |
|---|---|
| `/` | Upload (`Analyze`) |
| `/result` | Resultado (`Result`) — requer `location.state.result` |

## Docker

```bash
# na raiz do projeto
cp genre-ai-frontend/.env.example genre-ai-frontend/.env
docker compose up --build
```
