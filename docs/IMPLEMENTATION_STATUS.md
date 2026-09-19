# Implementation status - v0.2.1

## Implemented

- Task-first dashboard and navigation
- Multi-ticker research tasks, maximum 10 symbols
- Task name, thesis, horizon, capital context, cadence metadata, and methodology modules
- Immutable task configuration versions and SHA-256 hashes
- Run-time configuration snapshot
- Redis/RQ background execution
- Duplicate active-run protection
- Per-stage events and aggregate progress
- Complete, partial, and failed terminal states
- Per-ticker deterministic analysis
- Bear/Base/Bull scenario packet
- Technical, fundamental, liquidity, completeness, and confidence scoring
- Deterministic research action
- Evidence source metadata and hashes
- Local Ollama explanation-only review
- Free-only yfinance market-data guard
- Dashboard, task detail, run history, trace, result drill-down, methodology, and settings views
- Instant English/Bahasa Indonesia interface switching with browser persistence
- Localized application-owned labels, statuses, stages, and known orchestration messages
- Language switching does not mutate evidence, hashes, or user-entered research content
- Backward-compatible single-ticker create payload
- Upgrade compatibility for v0.1.x rows
- Docker Compose and operational scripts

## Explicitly not implemented

- Automatic cadence scheduler
- Authentication and multi-user authorization
- Broker or order execution
- Licensed IDX real-time feed
- Corporate-action reconciliation against a second provider
- Normalized IDX/OJK filing ingestion
- Sector-specific valuation routing
- Point-in-time survivorship-free backtesting
- Portfolio holdings and transaction accounting
- Automatic run PDF report generation

These gaps are not represented as completed features in the UI or PRD/TRD.

## Recommended next implementation order

1. Automatic scheduler with idempotency and missed-run recovery
2. Run-level downloadable PDF report
3. Authentication and user-scoped tasks
4. Official filing ingestion and document evidence
5. Sector model routing for banks, insurers, commodity issuers, and REIT-like vehicles
6. Outcome ledger and point-in-time validation
