# Verification record

Generated: 19 September 2026

Verified for the v0.2.1 localization and research-guidance release:

- Package structure verification passed all 8 checks, including the task contract, localization contract, Mermaid architecture marker, and patched frontend dependency guard.
- Python source compiled successfully with `compileall`.
- All 12 backend tests passed. Coverage includes deterministic quant and policy behavior, the AI authority boundary, multi-ticker validation, legacy ticker compatibility, unknown-module rejection, task CRUD, and immutable configuration versioning.
- Ruff static checks passed for the backend application and test code.
- Every shell script passed `bash -n` syntax validation.
- The production frontend v0.2.1 compiled successfully with Next.js 15.5.24. Type checking covered the complete English/Bahasa Indonesia message catalog and localized component contracts. The route was statically generated and the first-load JavaScript bundle was approximately 115 kB.
- Static verification confirmed that the language selection is persisted under `buktisaham-language`, application-owned labels use the translation catalog, and the README contains the detailed Mermaid architecture.
- The combined PRD/TRD v2.1 PDF passed preflight: 28 A4 pages, openable, not encrypted, searchable text, and no suspicious PDF features.
- Every PDF page was rendered to PNG and reviewed in contact sheets; representative pages were also inspected at full resolution. No clipping, overlap, missing glyph, or margin defects were found.
- The final repository archive passed `unzip -t` integrity validation and excludes dependency caches, build output, temporary renders, Python bytecode, and the superseded v2.0 generated PDF.

Environment limitations during packaging:

- The packaging environment had no Docker executable, so the Compose stack was not launched here.
- No live Yahoo Finance request or Ollama model pull was performed during packaging.

For a connected machine with Docker, run `./scripts/bootstrap.sh`, then `./scripts/smoke-test.sh` and `./scripts/task-demo.sh` to validate the full runtime path.
