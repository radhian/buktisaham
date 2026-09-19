# Verification record

Generated: 19 September 2026

Verified in the build environment:

- Python source compiled successfully with `compileall`.
- All 7 backend tests passed, including deterministic quant/policy behavior and the analysis-engine AI authority boundary.
- Ruff static checks passed for backend application and test code.
- Docker Compose YAML parsed successfully and the configurable mappings were verified: API `18000:8000`, web `3000:3000`, and Ollama `11434:11434` by default.
- All shell scripts passed `bash -n` syntax validation.
- The production Next.js frontend compiled successfully using `NEXT_PUBLIC_API_BASE_URL=http://localhost:18000`.
- Package verification confirms the free-only data guard, local Ollama guard, and configurable host-port contract.
- Updated PRD/TRD DOCX rendered successfully to 30 pages and was visually reviewed.
- Updated PDF preflight passed: 30 pages, openable, not encrypted, not scanned; PDF rendering succeeded.

Environment limitations during packaging:

- The build environment had no Docker executable, so the Docker Compose stack could not be launched here.
- A live `yfinance` call and real Ollama model pull were not executed during this port-conflict patch.

The repository includes `scripts/bootstrap.sh`, `scripts/smoke-test.sh`, and CI so those live checks run in a normal Internet-connected Docker environment.
