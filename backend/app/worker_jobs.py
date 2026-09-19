from __future__ import annotations

from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import EvidenceItem, RecommendationVersion, ResearchTask, TaskRun
from app.services.analysis_engine import AnalysisEngine
from app.services.evidence import content_hash


def utcnow():
    return datetime.now(timezone.utc)


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
            return

        run.status = "RUNNING"
        run.started_at = utcnow()
        db.commit()

        result = AnalysisEngine().analyze(
            ticker=task.ticker,
            horizon_days=task.horizon_days,
            capital_idr=task.capital_idr,
        )

        run.status = "COMPLETED"
        run.result_json = result
        run.finished_at = utcnow()

        rec = RecommendationVersion(
            run_id=run.id,
            version=1,
            research_action=result["research_action"],
            content_hash=content_hash(result),
            payload_json=result,
        )
        db.add(rec)
        for item in result.get("evidence", []):
            db.add(
                EvidenceItem(
                    run_id=run.id,
                    evidence_type=item["evidence_type"],
                    source_name=item["source_name"],
                    source_uri=item.get("source_uri"),
                    payload_json=item.get("payload", {}),
                    content_hash=item["content_hash"],
                )
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        run = db.get(TaskRun, run_id)
        if run:
            run.status = "FAILED"
            run.error = str(exc)
            run.finished_at = utcnow()
            db.commit()
        raise
    finally:
        db.close()
