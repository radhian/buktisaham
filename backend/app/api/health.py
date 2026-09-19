from __future__ import annotations

from fastapi import APIRouter
from redis import Redis
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    db_status = "ok"
    redis_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unavailable: {exc}"
    try:
        Redis.from_url(settings.redis_url).ping()
    except Exception as exc:
        redis_status = f"unavailable: {exc}"

    return {
        "status": "ok" if db_status == redis_status == "ok" else "degraded",
        "app": settings.app_name,
        "environment": settings.app_env,
        "market_data": {
            "provider": settings.market_data_provider,
            "free_only": settings.free_only_market_data,
            "paid_fallback_enabled": False,
        },
        "database": db_status,
        "redis": redis_status,
        "ollama": OllamaClient(settings).health(),
    }
