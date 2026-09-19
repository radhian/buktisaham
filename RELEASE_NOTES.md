# Release notes - BuktiSaham v0.2.0

## Product reframing

BuktiSaham is now a task-based Indonesian equity research orchestrator. A user creates a reusable mandate, runs its saved methodology, watches progress, and compares immutable results over time.

## Added

- Multi-ticker tasks
- Task name and thesis
- Versioned configuration and hashes
- Config snapshots per run
- Dashboard and task workspace
- Run history and event timeline
- Progress stages
- Complete, partial, and failed publication
- Per-ticker result navigation
- End-to-end task demo script
- Task orchestration documentation and APIs

## Preserved

- Free-only yfinance provider
- Local Ollama
- Explanation-only AI authority
- Deterministic policy action
- Port-conflict fix using host API port 18000
- Existing single-ticker API compatibility

## Security maintenance

- Next.js updated to 15.5.24
- React and React DOM updated to 19.1.5

## Not yet implemented

- Automatic scheduler
- Authentication
- Automatic run PDF generation
- Licensed or official real-time IDX feed
- Sector-specific valuation models
