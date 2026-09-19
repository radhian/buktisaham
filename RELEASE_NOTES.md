# Release notes - BuktiSaham v0.2.1

## Localization and guidance update

- Added a Settings control for instant English/Bahasa Indonesia interface switching.
- Persisted the selected language in browser local storage.
- Localized navigation, forms, tables, settings, methodology, statuses, stages, and known orchestration messages.
- Kept stored evidence, hashes, and user-entered content unchanged when the display language changes.
- Expanded the README with a detailed Mermaid runtime architecture.
- Added disciplined Indonesian-stock research pro tips and a pre-run checklist to the PRD/TRD.
- Updated the combined PRD/TRD blueprint to v2.1.

## v0.2.0 task-orchestration foundation

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
