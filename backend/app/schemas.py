from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ResearchTaskCreate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    thesis: str = Field(
        default="Evaluate Indonesian equities using deterministic evidence, scenario analysis, and risk controls.",
        max_length=1200,
    )
    ticker: str | None = Field(default=None, min_length=1, max_length=32)
    tickers: list[str] = Field(default_factory=list, max_length=10)
    horizon_days: int = Field(default=90, ge=5, le=730)
    capital_idr: Decimal = Field(default=Decimal("100000000"), gt=0)
    cadence: Literal["manual", "daily", "weekly", "monthly"] = "manual"
    analysis_modules: list[str] = Field(
        default_factory=lambda: ["technical", "fundamental", "liquidity", "scenario", "evidence", "ai_review"]
    )

    @field_validator("ticker")
    @classmethod
    def normalize_input(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else value

    @field_validator("tickers")
    @classmethod
    def normalize_tickers(cls, values: list[str]) -> list[str]:
        return [value.strip().upper() for value in values if value.strip()]

    @model_validator(mode="after")
    def validate_universe(self):
        values = self.tickers or ([self.ticker] if self.ticker else [])
        unique: list[str] = []
        for value in values:
            if value and value not in unique:
                unique.append(value)
        if not unique:
            raise ValueError("At least one Indonesian stock ticker is required")
        if len(unique) > 10:
            raise ValueError("A task can contain at most 10 tickers in this MVP")
        self.tickers = unique
        self.ticker = unique[0]
        self.name = (self.name or f"{unique[0]} research task").strip()
        if not self.name:
            raise ValueError("Task name is required")
        allowed_modules = {"technical", "fundamental", "liquidity", "scenario", "evidence", "ai_review"}
        invalid = sorted(set(self.analysis_modules) - allowed_modules)
        if invalid:
            raise ValueError(f"Unsupported analysis modules: {', '.join(invalid)}")
        return self


class ResearchTaskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    thesis: str | None = Field(default=None, max_length=1200)
    tickers: list[str] | None = Field(default=None, min_length=1, max_length=10)
    horizon_days: int | None = Field(default=None, ge=5, le=730)
    capital_idr: Decimal | None = Field(default=None, gt=0)
    cadence: Literal["manual", "daily", "weekly", "monthly"] | None = None
    analysis_modules: list[str] | None = None

    @field_validator("tickers")
    @classmethod
    def normalize_tickers(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized: list[str] = []
        for value in values:
            item = value.strip().upper()
            if item and item not in normalized:
                normalized.append(item)
        if not normalized:
            raise ValueError("At least one Indonesian stock ticker is required")
        return normalized


class ResearchTaskResponse(BaseModel):
    id: str
    ticker: str
    tickers: list[str]
    name: str
    thesis: str
    horizon_days: int
    capital_idr: str
    cadence: str
    status: str
    analysis_modules: list[str]
    config_version: int
    config_hash: str
    latest_run: dict[str, Any] | None = None
    created_at: datetime


class RunEventResponse(BaseModel):
    stage: str
    progress: int
    message: str
    created_at: datetime


class RunResponse(BaseModel):
    id: str
    task_id: str
    status: str
    error: str | None = None
    result: dict[str, Any] | None = None
    stage: str = "queued"
    progress: int = 0
    message: str = "Queued"
    events: list[RunEventResponse] = Field(default_factory=list)
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class QuoteResponse(BaseModel):
    ticker: str
    provider: str
    currency: str | None = None
    last_price: float
    previous_close: float | None = None
    change_pct: float | None = None
    market_time: datetime | None = None
    source_uri: str


class AiReviewRequest(BaseModel):
    analysis: dict[str, Any]
