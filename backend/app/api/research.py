from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import ResearchTask, TaskRun
from app.schemas import ResearchTaskCreate, ResearchTaskResponse, RunResponse
from app.services.market import get_market_provider
from app.worker_jobs import run_analysis_job

router = APIRouter(prefix="/v1", tags=["research"])


@router.post("/research-tasks", response_model=ResearchTaskResponse, status_code=201)
def create_task(payload: ResearchTaskCreate, db: Session = Depends(get_db)) -> ResearchTaskResponse:
    symbol = get_market_provider().normalize_ticker(payload.ticker)
    task = ResearchTask(
        ticker=symbol,
        horizon_days=payload.horizon_days,
        capital_idr=str(payload.capital_idr),
        params_json={"market_data_mode": "FREE_ONLY", "provider": "yfinance"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return ResearchTaskResponse.model_validate(task)


@router.post("/research-tasks/{task_id}/runs", response_model=RunResponse, status_code=202)
def start_run(task_id: str, db: Session = Depends(get_db)) -> RunResponse:
    task = db.get(ResearchTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    run = TaskRun(task_id=task.id, status="QUEUED")
    db.add(run)
    db.commit()
    db.refresh(run)

    settings = get_settings()
    try:
        connection = Redis.from_url(settings.redis_url)
        queue = Queue("research", connection=connection)
        queue.enqueue(run_analysis_job, run.id, job_timeout=max(180, settings.ollama_timeout_seconds + 60))
    except Exception as exc:
        run.status = "FAILED"
        run.error = f"Unable to enqueue research job: {exc}"
        db.commit()
        raise HTTPException(status_code=503, detail=run.error) from exc

    return RunResponse(
        id=run.id,
        task_id=run.task_id,
        status=run.status,
        error=run.error,
        result=run.result_json,
        created_at=run.created_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunResponse:
    run = db.get(TaskRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(
        id=run.id,
        task_id=run.task_id,
        status=run.status,
        error=run.error,
        result=run.result_json,
        created_at=run.created_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )
