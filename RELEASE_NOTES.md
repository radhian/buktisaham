# Release notes - MVP 0.1.1

## Port-conflict fix

- The API host port is no longer hard-coded to `8000`.
- The default host-facing API URL is now `http://localhost:18000`; the API still listens on `8000` inside Docker.
- `API_HOST_PORT`, `WEB_HOST_PORT`, and `OLLAMA_HOST_PORT` make every published port configurable.
- The frontend build, API examples, bootstrap output, and smoke test now use the configured host mapping.
- Added troubleshooting guidance for detecting and resolving an occupied port.

## Requested adjustments

- AI review is explicitly local through Ollama.
- Default model is `qwen3:8b` and is configurable through `OLLAMA_MODEL`.
- No cloud AI API adapter is implemented.
- Stock data is explicitly free-only for the current MVP.
- Default/only stock-data adapter is `yfinance` with Indonesian `.JK` ticker normalization.
- There is no paid stock-data fallback.

## Runnable implementation

This ZIP contains a working application skeleton: FastAPI + PostgreSQL + Redis/RQ + local Ollama + Next.js, deterministic analysis/policy, evidence metadata, tests, Docker Compose, and operational scripts.

See `docs/IMPLEMENTATION_STATUS.md` for capabilities deliberately left for later phases of the full blueprint.
