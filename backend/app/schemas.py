from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ResearchTaskCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=32)
    horizon_days: int = Field(default=90, ge=5, le=730)
    capital_idr: Decimal = Field(default=Decimal("100000000"), gt=0)

    @field_validator("ticker")
    @classmethod
    def normalize_input(cls, value: str) -> str:
        return value.strip().upper()


class ResearchTaskResponse(BaseModel):
    id: str
    ticker: str
    horizon_days: int
    capital_idr: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RunResponse(BaseModel):
    id: str
    task_id: str
    status: str
    error: str | None = None
    result: dict[str, Any] | None = None
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
