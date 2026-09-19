from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def content_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def market_evidence(ticker: str, technicals: dict[str, Any], provider: str = "yfinance") -> dict[str, Any]:
    symbol = ticker.upper()
    uri = f"https://finance.yahoo.com/quote/{symbol}"
    payload = {
        "ticker": symbol,
        "provider": provider,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "technicals": technicals,
    }
    return {
        "evidence_type": "MARKET_DATA",
        "source_name": "Yahoo Finance via yfinance",
        "source_uri": uri,
        "observed_at": payload["observed_at"],
        "payload": payload,
        "content_hash": content_hash(payload),
        "rights_note": "Free/unofficial research adapter; upstream terms still apply; no paid fallback enabled.",
    }


def fundamentals_evidence(ticker: str, fundamentals: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "ticker": ticker.upper(),
        "provider": "yfinance",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "fundamentals": fundamentals,
    }
    return {
        "evidence_type": "FUNDAMENTALS",
        "source_name": "Yahoo Finance via yfinance",
        "source_uri": f"https://finance.yahoo.com/quote/{ticker.upper()}",
        "observed_at": payload["observed_at"],
        "payload": payload,
        "content_hash": content_hash(payload),
        "rights_note": "Best-effort free research data; validate against official filings before publication.",
    }
