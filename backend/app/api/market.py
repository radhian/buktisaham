from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import QuoteResponse
from app.services.market import get_market_provider
from app.services.market.base import MarketDataError

router = APIRouter(prefix="/v1/market", tags=["market"])


@router.get("/{ticker}/quote", response_model=QuoteResponse)
def quote(ticker: str) -> QuoteResponse:
    try:
        q = get_market_provider().get_quote(ticker)
        return QuoteResponse(**q.__dict__)
    except MarketDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
