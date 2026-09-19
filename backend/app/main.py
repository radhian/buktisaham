from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai_router, health_router, market_router, research_router
from app.config import get_settings
from app.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.enforce_market_data_policy()
    init_db()
    yield


app = FastAPI(
    title="BuktiSaham API",
    version="0.2.1",
    description="Task-based Indonesian equity research orchestration using free stock data and local Ollama review.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(market_router)
app.include_router(research_router)
app.include_router(ai_router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": "0.2.0",
        "product_mode": "TASK_ORCHESTRATION",
        "docs": "/docs",
        "market_data_policy": "FREE_ONLY",
        "ai_provider": "ollama-local",
    }
