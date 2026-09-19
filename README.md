# BuktiSaham

Local-first, evidence-oriented Indonesian equity research MVP.

This implementation follows two explicit constraints:

1. **AI review is local through Ollama**. The LLM can summarize and challenge deterministic analysis, but it cannot change prices, calculations, scenario values, or the research action.
2. **Stock data is free-only for now**. The only enabled market-data adapter is `yfinance` (Yahoo Finance public/unofficial endpoints). There is **no paid-provider fallback** in this repository.

> Important: `yfinance` is an open-source client for Yahoo Finance's public/unofficial endpoints. Availability can change and Yahoo's terms may limit use. Treat this MVP as research/personal-use infrastructure until your data rights are reviewed. The application exposes provider metadata so you can later replace the adapter without changing the research engine.

## What is implemented

- FastAPI REST API
- PostgreSQL persistence for research tasks, runs, recommendation versions, and evidence
- Redis + RQ background worker
- Free-only Indonesian stock data adapter (`yfinance`, `.JK` normalization)
- Deterministic technical/fundamental scoring, Bull/Base/Bear scenarios, and policy action
- Evidence payload with source/provider/freshness metadata
- Local Ollama review (`qwen3:8b` by default)
- Next.js single-page research UI
- Docker Compose for Postgres, Redis, Ollama, API, worker, and web
- Unit tests, smoke-test script, backup/restore scripts, and CI workflow

## Quick start - Docker (recommended)

Requirements:

- Docker Desktop / Docker Engine with Compose v2
- At least ~8 GB free RAM is recommended for the default `qwen3:8b` model; use a smaller Ollama model by changing `OLLAMA_MODEL` if needed.

```bash
cp .env.example .env
./scripts/bootstrap.sh
```

Then open:

- Web UI: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

The bootstrap script starts the infrastructure, pulls the configured Ollama model, builds the application, and runs a smoke test.

### Try an Indonesian ticker

The UI accepts `BBCA` or `BBCA.JK`. The backend normalizes bare IDX tickers to `.JK`.

```bash
curl http://localhost:8000/v1/market/BBCA/quote
```

Create a research task:

```bash
curl -X POST http://localhost:8000/v1/research-tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "ticker": "BBCA",
    "horizon_days": 90,
    "capital_idr": "100000000"
  }'
```

Start a run using the returned task ID:

```bash
curl -X POST http://localhost:8000/v1/research-tasks/<TASK_ID>/runs
```

Poll the run:

```bash
curl http://localhost:8000/v1/runs/<RUN_ID>
```

## Local development without Docker

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL='sqlite:///./buktisaham-local.db'
export REDIS_URL='redis://localhost:6379/0'
export OLLAMA_BASE_URL='http://localhost:11434'
pytest -q
uvicorn app.main:app --reload
```

The worker requires Redis:

```bash
cd backend
source .venv/bin/activate
python -m app.worker
```

Frontend:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## AI authority boundary

The deterministic engine computes:

- price/return metrics
- moving averages / RSI / volatility / drawdown
- available fundamental factors
- scenario prices and expected return
- technical, fundamental, liquidity, completeness, and confidence scores
- the final research action (`BUY_RESEARCH`, `HOLD_RESEARCH`, `SELL_RESEARCH`, or `WATCH`)

Ollama receives a read-only JSON snapshot of those values and produces only:

- plain-language summary
- drivers
- risks
- contradictions / caveats
- analyst review questions

If Ollama is unavailable, the run still completes and `ai_review.status` is `unavailable`.

## Free-only market-data policy

At startup, configuration rejects any `MARKET_DATA_PROVIDER` other than `yfinance` while `FREE_ONLY_MARKET_DATA=true`.

There is intentionally no automatic paid fallback. If Yahoo is unavailable, the run fails with a clear market-data error rather than silently switching to a billable service.

The provider interface lives at:

```text
backend/app/services/market/base.py
backend/app/services/market/yfinance_provider.py
```

A future licensed provider can implement the same interface without changing the research engine.

## Scripts

```text
scripts/bootstrap.sh       first-time setup + Ollama model pull + build + smoke test
scripts/start.sh           start all services
scripts/stop.sh            stop services
scripts/pull-model.sh      pull the configured local Ollama model
scripts/test.sh            backend + frontend checks
scripts/smoke-test.sh      end-to-end API smoke test
scripts/backup.sh          Postgres + object-data backup
scripts/restore.sh         restore a backup directory
scripts/verify-package.sh  fast structural/syntax verification
scripts/git-init-and-push.sh initialize Git and push to a remote you provide
```

## Repository map

```text
backend/     FastAPI, worker, deterministic research engine, Ollama client
frontend/    Next.js UI
docs/        architecture, data-source policy, implementation status
scripts/     plug-and-play operational scripts
.github/     CI
```

## Security / product boundary

This is a research prototype, not a broker, order router, custody system, or personalized investment-advice engine. The local LLM never has authority to publish or change the deterministic research action.

## Useful commands

```bash
make bootstrap
make up
make down
make logs
make test
make smoke
make backup
```

## Push to your GitHub

After you unzip the repository and review `.env`:

```bash
./scripts/git-init-and-push.sh https://github.com/YOUR_USER/YOUR_REPO.git
```

The script initializes `main` if needed, creates a first commit from the current files, configures `origin`, and pushes. It does not create the GitHub repository itself; create an empty repository first.
