# BuktiSaham

Task-based Indonesian equity research orchestration.

BuktiSaham lets a user define a reusable research mandate, run that exact methodology repeatedly, follow its execution stages, and inspect recommendation evidence for every ticker in the task. It is no longer designed as a one-shot ticker calculator.

## Product model

~~~mermaid
flowchart LR
    A[Create research task] --> B[Versioned config]
    B --> C[Queue run]
    C --> D[Free IDX data]
    D --> E[Deterministic analysis]
    E --> F[Local Ollama review]
    F --> G[Evidence packet]
    G --> H[Run history and rerun]
~~~

The primary objects are:

| Object | Purpose |
| --- | --- |
| Research Task | Reusable mandate containing name, thesis, IDX universe, horizon, capital context, and methodology modules |
| Task Config Version | Immutable hash and version for every saved task configuration |
| Task Run | One asynchronous execution against a saved configuration snapshot |
| Run Event | Stage, progress, timestamp, and message emitted by the worker |
| Stock Analysis | Deterministic per-ticker metrics, scenarios, scores, policy action, and Ollama review |
| Evidence Packet | Source lineage and hashes for the published task result |

## Current MVP boundaries

- Local AI review through Ollama; no cloud AI key is required.
- Stock market data is free-only through **yfinance**.
- Indonesian symbols are normalized to Yahoo's **.JK** convention.
- Up to 10 tickers can be analyzed in one task.
- Runs are started manually in v0.2.0.
- Cadence is stored in the task contract for future scheduler support, but automatic scheduling is not claimed as implemented.
- The product is EOD/delayed research infrastructure, not an exchange-grade real-time terminal.
- BuktiSaham does not place trades or connect to a broker.

## What changed in v0.2.0

- Reframed the product around reusable research tasks.
- Added multi-ticker task universes.
- Added immutable task configuration versions and hashes.
- Added run-time configuration snapshots.
- Added duplicate-active-run protection.
- Added worker stage events and aggregate progress.
- Added partial publication when one ticker fails and others succeed.
- Added dashboard, task workspace, run history, live orchestration trace, methodology view, and per-ticker result drill-down.
- Preserved deterministic recommendation authority and local Ollama's explanation-only boundary.
- Preserved free-only market data with no paid fallback.
- Updated Next.js to the current 15.5 maintenance security release.

## Quick start

Requirements:

- Docker Desktop or Docker Engine with Compose v2
- Approximately 8 GB available RAM for the default **qwen3:8b** Ollama model
- Internet access for first-time image/model downloads and free market-data requests

~~~bash
cp .env.example .env
./scripts/bootstrap.sh
~~~

Open:

- Web workspace: http://localhost:3000
- API documentation: http://localhost:18000/docs
- API health: http://localhost:18000/health
- Local Ollama API: http://localhost:11434

The API remains on port 8000 inside Docker and is exposed on host port 18000 by default.

## First task

Use the web interface and select **New task**, or run the included example:

~~~bash
./scripts/task-demo.sh
~~~

The demo creates an Indonesian banking research task for BBCA, BBRI, and BMRI, starts a run, follows progress, and prints the published action counts and immutable bundle hash.

## API example

Create a reusable task:

~~~bash
curl -X POST http://localhost:18000/v1/research-tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "IDX Banking Quality Review",
    "thesis": "Compare large Indonesian banks using one repeatable evidence-based method.",
    "tickers": ["BBCA", "BBRI", "BMRI"],
    "horizon_days": 90,
    "capital_idr": "100000000",
    "cadence": "manual"
  }'
~~~

Start a run and observe progress:

~~~bash
curl -X POST http://localhost:18000/v1/research-tasks/<TASK_ID>/runs
curl http://localhost:18000/v1/runs/<RUN_ID>
~~~

List tasks and history:

~~~bash
curl http://localhost:18000/v1/research-tasks
curl http://localhost:18000/v1/runs
curl http://localhost:18000/v1/research-tasks/<TASK_ID>/runs
~~~

## Run lifecycle

~~~mermaid
stateDiagram-v2
    [*] --> QUEUED
    QUEUED --> RUNNING
    RUNNING --> COMPLETED
    RUNNING --> PARTIAL
    RUNNING --> FAILED
    QUEUED --> FAILED
    COMPLETED --> [*]
    PARTIAL --> [*]
    FAILED --> [*]
~~~

Typical event stages:

~~~text
queued
initialize
collect
validate
score
scenario
policy
ai_review
package
complete
~~~

Progress is aggregated across every ticker in the task. If one ticker fails, the worker records **symbol_failed** and continues. A run becomes **PARTIAL** when at least one analysis succeeds and at least one fails.

## Indonesian-stock methodology

Each ticker is processed independently inside the task:

1. Normalize the IDX ticker to **.JK**.
2. Retrieve one year of free EOD price/volume history and available fundamentals.
3. Validate data presence and evidence completeness.
4. Calculate technical indicators, volatility, drawdown, and liquidity.
5. Score technical, fundamental, liquidity, and evidence dimensions.
6. Build Bear, Base, and Bull scenario prices and probabilities.
7. Apply deterministic recommendation gates.
8. Assemble evidence records and deterministic hashes.
9. Ask local Ollama to explain drivers, risks, contradictions, and analyst questions.
10. Publish the per-stock analyses as one task-level evidence packet.

The deterministic engine is authoritative for market facts, score calculations, scenarios, policy gates, and **BUY_RESEARCH**, **HOLD_RESEARCH**, **SELL_RESEARCH**, or **WATCH**. Ollama cannot change those values.

## Architecture

~~~mermaid
flowchart TB
    UI[Next.js task workspace] --> API[FastAPI orchestration API]
    API --> DB[(PostgreSQL)]
    API --> Q[Redis research queue]
    Q --> W[Research worker]
    W --> Y[yfinance free EOD adapter]
    W --> QNT[Deterministic Python engine]
    W --> O[Local Ollama]
    W --> DB
~~~

Runtime services:

| Service | Responsibility |
| --- | --- |
| web | Dashboard, task creation, task detail, run history, result drill-down |
| api | Task/config/run APIs, validation, queue submission, read models |
| worker | Multi-ticker orchestration, progress events, publication |
| postgres | Tasks, config versions, runs, events, evidence, recommendation packets |
| redis | Background job queue |
| ollama | Local explanation and evidence review |

## Data and AI policies

~~~env
FREE_ONLY_MARKET_DATA=true
MARKET_DATA_PROVIDER=yfinance

AI_REVIEW_ENABLED=true
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen3:8b
~~~

Startup rejects a non-yfinance market provider while free-only mode is enabled. There is no paid-provider fallback.

yfinance uses Yahoo Finance public/unofficial endpoints. Availability and upstream terms can change. Review data rights before commercial or public production use.

## Port configuration

~~~env
API_HOST_PORT=18000
WEB_HOST_PORT=3000
OLLAMA_HOST_PORT=11434
NEXT_PUBLIC_API_BASE_URL=http://localhost:18000
~~~

If a host port is occupied, update both **API_HOST_PORT** and **NEXT_PUBLIC_API_BASE_URL**, then rebuild:

~~~bash
docker compose down
docker compose up -d --build
./scripts/smoke-test.sh
~~~

## Upgrade from v0.1.x

The new task orchestration tables are created automatically by SQLAlchemy:

- task_config_version
- run_event

Existing research_task and task_run rows remain readable. Old single-ticker tasks are presented as one-ticker task configurations and can be rerun.

Recommended upgrade:

~~~bash
docker compose down
git pull
docker compose up -d --build
./scripts/smoke-test.sh
~~~

Back up first when the existing local database matters:

~~~bash
./scripts/backup.sh
~~~

## Development

Backend:

~~~bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL='sqlite:///./buktisaham-local.db'
export REDIS_URL='redis://localhost:6379/0'
export OLLAMA_BASE_URL='http://localhost:11434'
pytest -q
uvicorn app.main:app --reload
~~~

Frontend:

~~~bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:18000 npm run dev
~~~

## Operational scripts

| Script | Purpose |
| --- | --- |
| scripts/bootstrap.sh | First-time infrastructure, model pull, build, and smoke test |
| scripts/start.sh | Start all services |
| scripts/stop.sh | Stop all services |
| scripts/task-demo.sh | Create and execute a multi-stock task end to end |
| scripts/pull-model.sh | Pull the configured Ollama model |
| scripts/test.sh | Backend and frontend checks |
| scripts/smoke-test.sh | Health and free-market-data smoke test |
| scripts/backup.sh | PostgreSQL backup |
| scripts/restore.sh | Restore a backup |
| scripts/verify-package.sh | Structural, syntax, policy, and orchestration checks |
| scripts/git-init-and-push.sh | Initialize Git and push to a remote you provide |

Useful commands:

~~~bash
make bootstrap
make up
make down
make logs
make test
make smoke
make demo
make backup
~~~

## Repository map

~~~text
backend/                 FastAPI, worker, orchestration, quant, data and Ollama
frontend/                Next.js task-based workspace
docs/                    Architecture, APIs, methodology and implementation status
output/pdf/              Generated PRD/TRD PDF
docs/blueprint/          Legacy v1.1 blueprint reference
scripts/                 Plug-and-play operational scripts
.github/workflows/       Continuous integration
~~~

## Security and product boundary

- Local development is single-user and has no built-in authentication.
- Do not expose the default Docker deployment directly to the public internet.
- Add authentication, authorization, rate limiting, TLS termination, and secrets management before multi-user deployment.
- The application is research decision support, not a broker, order router, custody product, or guarantee of investment returns.

The frontend uses the patched Next.js 15.5 maintenance release recommended by the official [Next.js security advisory](https://nextjs.org/blog/tag/security).
