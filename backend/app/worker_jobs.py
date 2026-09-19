from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from app.db import SessionLocal
from app.models import EvidenceItem, RecommendationVersion, ResearchTask, RunEvent, TaskRun
from app.services.analysis_engine import AnalysisEngine
from app.services.evidence import content_hash


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _record_event(db, run_id: str, stage: str, progress: int, message: str) -> None:
    db.add(
        RunEvent(
            run_id=run_id,
            stage=stage,
            progress=max(0, min(100, int(progress))),
            message=message,
        )
    )
    db.commit()


def _task_config(task: ResearchTask, run: TaskRun) -> dict[str, Any]:
    envelope = dict(run.result_json or {})
    snapshot = envelope.get("config_snapshot") or {}
    if snapshot.get("config"):
        return dict(snapshot["config"])
    params = dict(task.params_json or {})
    return {
        "name": params.get("name") or f"{task.ticker} research task",
        "thesis": params.get("thesis") or "",
        "tickers": params.get("tickers") or [task.ticker],
        "horizon_days": task.horizon_days,
        "capital_idr": task.capital_idr,
        "cadence": params.get("cadence", "manual"),
        "analysis_modules": params.get("analysis_modules") or [],
        "market_data_mode": "FREE_ONLY",
        "provider": "yfinance",
    }


def _build_bundle(
    *,
    task: ResearchTask,
    config: dict[str, Any],
    analyses: list[dict[str, Any]],
    errors: list[dict[str, str]],
    config_snapshot: dict[str, Any],
) -> dict[str, Any]:
    counts = Counter(item["research_action"] for item in analyses)
    confidence_values = [float(item.get("scores", {}).get("confidence", 0)) for item in analyses]
    bundle: dict[str, Any] = {
        "schema_version": "2.0",
        "product_mode": "TASK_ORCHESTRATION",
        "task": {
            "id": task.id,
            "name": config.get("name"),
            "thesis": config.get("thesis"),
            "tickers": config.get("tickers"),
            "horizon_days": config.get("horizon_days"),
            "capital_idr": config.get("capital_idr"),
        },
        "config_snapshot": config_snapshot,
        "summary": {
            "requested_symbols": len(config.get("tickers") or []),
            "completed_symbols": len(analyses),
            "failed_symbols": len(errors),
            "action_counts": dict(counts),
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 2)
            if confidence_values
            else 0,
        },
        "analyses": analyses,
        "errors": errors,
        "generated_at": utcnow().isoformat(),
    }
    bundle["primary_analysis"] = analyses[0] if analyses else None
    bundle["bundle_hash"] = content_hash(bundle)
    return bundle


def run_analysis_job(run_id: str) -> None:
    db = SessionLocal()
    try:
        run = db.get(TaskRun, run_id)
        if not run:
            return
        task = db.get(ResearchTask, run.task_id)
        if not task:
            run.status = "FAILED"
            run.error = "Research task not found"
            run.finished_at = utcnow()
            db.commit()
            _record_event(db, run_id, "failed", 100, run.error)
            return

        config = _task_config(task, run)
        tickers = list(config.get("tickers") or [task.ticker])
        config_snapshot = dict((run.result_json or {}).get("config_snapshot") or {})
        if not config_snapshot:
            config_snapshot = {"config": config, "config_hash": content_hash(config), "config_version": 1}

        run.status = "RUNNING"
        run.started_at = utcnow()
        db.commit()
        _record_event(db, run.id, "initialize", 7, f"Loaded immutable task configuration for {len(tickers)} ticker(s)")

        analyses: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        engine = AnalysisEngine()
        total = max(1, len(tickers))

        for index, ticker in enumerate(tickers):
            base = 8 + (index / total) * 84
            span = 84 / total

            def progress(stage: str, local_progress: int, message: str) -> None:
                aggregate = int(base + (local_progress / 100) * span)
                _record_event(db, run.id, stage, aggregate, message)

            try:
                result = engine.analyze(
                    ticker=ticker,
                    horizon_days=int(config.get("horizon_days", task.horizon_days)),
                    capital_idr=str(config.get("capital_idr", task.capital_idr)),
                    progress_callback=progress,
                )
                analyses.append(result)
            except Exception as exc:
                errors.append({"ticker": ticker, "error": str(exc)})
                _record_event(
                    db,
                    run.id,
                    "symbol_failed",
                    int(base + span),
                    f"{ticker} failed; continuing with the remaining task universe",
                )

        bundle = _build_bundle(
            task=task,
            config=config,
            analyses=analyses,
            errors=errors,
            config_snapshot=config_snapshot,
        )
        run.result_json = bundle
        run.finished_at = utcnow()

        if not analyses:
            run.status = "FAILED"
            run.error = "; ".join(f"{item['ticker']}: {item['error']}" for item in errors)
            db.commit()
            _record_event(db, run.id, "failed", 100, "No ticker analysis completed")
            return

        run.status = "PARTIAL" if errors else "COMPLETED"
        run.error = "; ".join(f"{item['ticker']}: {item['error']}" for item in errors) if errors else None

        db.add(
            RecommendationVersion(
                run_id=run.id,
                version=1,
                research_action="TASK_RESEARCH_PACKET",
                content_hash=bundle["bundle_hash"],
                payload_json=bundle,
            )
        )
        for analysis in analyses:
            for item in analysis.get("evidence", []):
                db.add(
                    EvidenceItem(
                        run_id=run.id,
                        evidence_type=item["evidence_type"],
                        source_name=item["source_name"],
                        source_uri=item.get("source_uri"),
                        payload_json={
                            "ticker": analysis.get("ticker"),
                            **item.get("payload", {}),
                        },
                        content_hash=item["content_hash"],
                    )
                )
        db.commit()
        final_message = (
            f"Published {len(analyses)} analysis result(s)"
            if not errors
            else f"Published {len(analyses)} result(s) with {len(errors)} ticker error(s)"
        )
        _record_event(db, run.id, "complete", 100, final_message)
    except Exception as exc:
        db.rollback()
        run = db.get(TaskRun, run_id)
        if run:
            run.status = "FAILED"
            run.error = str(exc)
            run.finished_at = utcnow()
            db.commit()
            _record_event(db, run.id, "failed", 100, f"Research orchestration failed: {exc}")
        raise
    finally:
        db.close()
