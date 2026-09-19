# Implementation status

## Implemented in this ZIP

- Docker Compose runtime
- FastAPI API
- PostgreSQL models
- Redis/RQ worker
- free-only `yfinance` stock-data adapter
- `.JK` ticker normalization
- deterministic indicators and scoring
- Bull/Base/Bear scenarios
- deterministic research policy
- evidence hashes and source metadata
- local Ollama review
- Next.js UI
- tests and CI skeleton
- bootstrap, model pull, start/stop, smoke, backup/restore scripts

## Deliberately simplified vs full blueprint

This is an executable **MVP foundation**, not every P1/P2 capability in the blueprint. The following are extension work:

- full official filing parser and normalized financial-statement taxonomy
- complete corporate-action engine and KSEI reconciliation
- effective-dated IDX lot/tick/rule ingestion
- sector-specific DCF/residual-income/RNAV models for every sector
- point-in-time historical security master and survivorship-free backtester
- full policy/reviewer/publisher multi-user workflow
- OIDC/enterprise RBAC/ABAC
- immutable object store / MinIO evidence manifests
- production-grade licensing/entitlement service
- full outcome ledger and calibration dashboard

The repository structure and contracts are intended to let those modules be added without replacing the current deterministic engine or AI/data-provider boundaries.
