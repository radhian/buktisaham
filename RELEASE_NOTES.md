# Release notes - MVP 0.1.0

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
