from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from redis import Redis
from rq import Queue
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import ResearchTask, RunEvent, TaskConfigVersion, TaskRun
from app.schemas import ResearchTaskCreate, ResearchTaskResponse, ResearchTaskUpdate, RunResponse
from app.services.evidence import content_hash
from app.services.market import get_market_provider
from app.worker_jobs import run_analysis_job

router = APIRouter(prefix="/v1", tags=["research"])


def _fallback_config(task: ResearchTask) -> dict[str, Any]:
    params = dict(task.params_json or {})
    tickers = params.get("tickers") or [task.ticker]
    return {
        "name": params.get("name") or f"{task.ticker} research task",
        "thesis": params.get("thesis")
        or "Evaluate Indonesian equities using deterministic evidence, scenario analysis, and risk controls.",
        "tickers": tickers,
        "horizon_days": task.horizon_days,
        "capital_idr": task.capital_idr,
        "cadence": params.get("cadence", "manual"),
        "analysis_modules": params.get(
            "analysis_modules",
            ["technical", "fundamental", "liquidity", "scenario", "evidence", "ai_review"],
        ),
        "status": params.get("status", "active"),
        "market_data_mode": "FREE_ONLY",
        "provider": "yfinance",
    }


def _latest_config(db: Session, task: ResearchTask) -> tuple[dict[str, Any], int, str]:
    version = (
        db.query(TaskConfigVersion)
        .filter(TaskConfigVersion.task_id == task.id)
        .order_by(TaskConfigVersion.version.desc())
        .first()
    )
    if version:
        return dict(version.config_json), version.version, version.config_hash
    config = _fallback_config(task)
    return config, 1, content_hash(config)


def _publish_config(db: Session, task: ResearchTask, config: dict[str, Any]) -> TaskConfigVersion:
    latest_number = (
        db.query(func.max(TaskConfigVersion.version))
        .filter(TaskConfigVersion.task_id == task.id)
        .scalar()
        or 0
    )
    version = TaskConfigVersion(
        task_id=task.id,
        version=latest_number + 1,
        config_hash=content_hash(config),
        config_json=config,
    )
    db.add(version)
    return version


def _validated_config(payload: ResearchTaskCreate) -> dict[str, Any]:
    provider = get_market_provider()
    tickers = [provider.normalize_ticker(ticker) for ticker in payload.tickers]
    return {
        "name": payload.name,
        "thesis": payload.thesis,
        "tickers": tickers,
        "horizon_days": payload.horizon_days,
        "capital_idr": str(payload.capital_idr),
        "cadence": payload.cadence,
        "analysis_modules": payload.analysis_modules,
        "status": "active",
        "market_data_mode": "FREE_ONLY",
        "provider": "yfinance",
    }


def _event_state(db: Session, run_id: str) -> tuple[str, int, str, list[dict[str, Any]]]:
    rows = (
        db.query(RunEvent)
        .filter(RunEvent.run_id == run_id)
        .order_by(RunEvent.created_at.asc())
        .all()
    )
    events = [
        {"stage": row.stage, "progress": row.progress, "message": row.message, "created_at": row.created_at}
        for row in rows
    ]
    if not rows:
        return "queued", 0, "Queued", events
    latest = rows[-1]
    return latest.stage, latest.progress, latest.message, events


def _serialize_run(db: Session, run: TaskRun, *, include_events: bool = True) -> RunResponse:
    stage, progress, message, events = _event_state(db, run.id)
    return RunResponse(
        id=run.id,
        task_id=run.task_id,
        status=run.status,
        error=run.error,
        result=run.result_json,
        stage=stage,
        progress=progress,
        message=message,
        events=events if include_events else [],
        created_at=run.created_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


def _serialize_task(db: Session, task: ResearchTask) -> ResearchTaskResponse:
    config, version, config_hash = _latest_config(db, task)
    latest_run = (
        db.query(TaskRun).filter(TaskRun.task_id == task.id).order_by(TaskRun.created_at.desc()).first()
    )
    return ResearchTaskResponse(
        id=task.id,
        ticker=task.ticker,
        tickers=list(config.get("tickers") or [task.ticker]),
        name=str(config.get("name") or f"{task.ticker} research task"),
        thesis=str(config.get("thesis") or ""),
        horizon_days=int(config.get("horizon_days", task.horizon_days)),
        capital_idr=str(config.get("capital_idr", task.capital_idr)),
        cadence=str(config.get("cadence", "manual")),
        status=str(config.get("status", "active")),
        analysis_modules=list(config.get("analysis_modules") or []),
        config_version=version,
        config_hash=config_hash,
        latest_run=(
            _serialize_run(db, latest_run, include_events=False).model_dump(mode="json") if latest_run else None
        ),
        created_at=task.created_at,
    )


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    tasks = [_serialize_task(db, task) for task in db.query(ResearchTask).order_by(ResearchTask.created_at.desc()).all()]
    active_tasks = [task for task in tasks if task.status != "archived"]
    runs = db.query(TaskRun).order_by(TaskRun.created_at.desc()).limit(12).all()
    serialized_runs = [_serialize_run(db, run, include_events=False) for run in runs]
    return {
        "task_count": len(active_tasks),
        "active_run_count": sum(run.status in {"QUEUED", "RUNNING"} for run in serialized_runs),
        "completed_run_count": db.query(TaskRun).filter(TaskRun.status.in_(["COMPLETED", "PARTIAL"])).count(),
        "failed_run_count": db.query(TaskRun).filter(TaskRun.status == "FAILED").count(),
        "tasks": [task.model_dump(mode="json") for task in active_tasks[:6]],
        "recent_runs": [run.model_dump(mode="json") for run in serialized_runs],
    }


@router.get("/research-tasks", response_model=list[ResearchTaskResponse])
def list_tasks(db: Session = Depends(get_db)) -> list[ResearchTaskResponse]:
    tasks = db.query(ResearchTask).order_by(ResearchTask.created_at.desc()).all()
    return [result for task in tasks if (result := _serialize_task(db, task)).status != "archived"]


@router.post("/research-tasks", response_model=ResearchTaskResponse, status_code=201)
def create_task(payload: ResearchTaskCreate, db: Session = Depends(get_db)) -> ResearchTaskResponse:
    config = _validated_config(payload)
    task = ResearchTask(
        ticker=config["tickers"][0],
        horizon_days=config["horizon_days"],
        capital_idr=config["capital_idr"],
        params_json=config,
    )
    db.add(task)
    db.flush()
    _publish_config(db, task, config)
    db.commit()
    db.refresh(task)
    return _serialize_task(db, task)


@router.get("/research-tasks/{task_id}", response_model=ResearchTaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)) -> ResearchTaskResponse:
    task = db.get(ResearchTask, task_id)
    if not task or _fallback_config(task).get("status") == "archived":
        raise HTTPException(status_code=404, detail="Research task not found")
    return _serialize_task(db, task)


@router.patch("/research-tasks/{task_id}", response_model=ResearchTaskResponse)
def update_task(
    task_id: str, payload: ResearchTaskUpdate, db: Session = Depends(get_db)
) -> ResearchTaskResponse:
    task = db.get(ResearchTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    current, _, _ = _latest_config(db, task)
    merged = {**current, **payload.model_dump(exclude_none=True)}
    merged.pop("status", None)
    merged.pop("market_data_mode", None)
    merged.pop("provider", None)
    validated = ResearchTaskCreate(**merged)
    config = _validated_config(validated)
    task.ticker = config["tickers"][0]
    task.horizon_days = config["horizon_days"]
    task.capital_idr = config["capital_idr"]
    task.params_json = config
    _publish_config(db, task, config)
    db.commit()
    db.refresh(task)
    return _serialize_task(db, task)


@router.delete("/research-tasks/{task_id}")
def archive_task(task_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    task = db.get(ResearchTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    active = (
        db.query(TaskRun)
        .filter(TaskRun.task_id == task.id, TaskRun.status.in_(["QUEUED", "RUNNING"]))
        .first()
    )
    if active:
        raise HTTPException(status_code=409, detail="Wait for the active run to finish before archiving")
    config, _, _ = _latest_config(db, task)
    config = {**config, "status": "archived"}
    task.params_json = config
    _publish_config(db, task, config)
    db.commit()
    return {"id": task_id, "status": "archived"}


@router.post("/research-tasks/{task_id}/runs", response_model=RunResponse, status_code=202)
def start_run(task_id: str, db: Session = Depends(get_db)) -> RunResponse:
    task = db.get(ResearchTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    active = (
        db.query(TaskRun)
        .filter(TaskRun.task_id == task.id, TaskRun.status.in_(["QUEUED", "RUNNING"]))
        .order_by(TaskRun.created_at.desc())
        .first()
    )
    if active:
        raise HTTPException(status_code=409, detail=f"Task already has an active run: {active.id}")

    config, version, config_hash = _latest_config(db, task)
    snapshot = {"config_version": version, "config_hash": config_hash, "config": config}
    run = TaskRun(task_id=task.id, status="QUEUED", result_json={"config_snapshot": snapshot})
    db.add(run)
    db.flush()
    db.add(RunEvent(run_id=run.id, stage="queued", progress=3, message="Research run queued"))
    db.commit()
    db.refresh(run)

    settings = get_settings()
    try:
        connection = Redis.from_url(settings.redis_url)
        queue = Queue("research", connection=connection)
        symbols = list(config.get("tickers") or [task.ticker])
        timeout = max(240, len(symbols) * (settings.ollama_timeout_seconds + 90))
        queue.enqueue(run_analysis_job, run.id, job_timeout=timeout)
    except Exception as exc:
        run.status = "FAILED"
        run.error = f"Unable to enqueue research job: {exc}"
        db.add(RunEvent(run_id=run.id, stage="failed", progress=100, message=run.error))
        db.commit()
        raise HTTPException(status_code=503, detail=run.error) from exc

    return _serialize_run(db, run)


@router.get("/research-tasks/{task_id}/runs", response_model=list[RunResponse])
def list_task_runs(task_id: str, db: Session = Depends(get_db)) -> list[RunResponse]:
    if not db.get(ResearchTask, task_id):
        raise HTTPException(status_code=404, detail="Research task not found")
    runs = db.query(TaskRun).filter(TaskRun.task_id == task_id).order_by(TaskRun.created_at.desc()).all()
    return [_serialize_run(db, run, include_events=False) for run in runs]


@router.get("/runs", response_model=list[RunResponse])
def list_runs(
    task_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[RunResponse]:
    query = db.query(TaskRun)
    if task_id:
        query = query.filter(TaskRun.task_id == task_id)
    runs = query.order_by(TaskRun.created_at.desc()).limit(limit).all()
    return [_serialize_run(db, run, include_events=False) for run in runs]


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunResponse:
    run = db.get(TaskRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _serialize_run(db, run)
