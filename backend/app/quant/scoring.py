from __future__ import annotations

from typing import Any


def _score_from_checks(checks: list[bool | None]) -> tuple[float, int]:
    applicable = [x for x in checks if x is not None]
    if not applicable:
        return 50.0, 0
    return 100.0 * sum(bool(x) for x in applicable) / len(applicable), len(applicable)


def score_technicals(t: dict[str, Any]) -> float:
    close = t.get("last_close")
    checks: list[bool | None] = [
        close > t["sma20"] if close is not None and t.get("sma20") is not None else None,
        close > t["sma50"] if close is not None and t.get("sma50") is not None else None,
        (t.get("return_20d") or 0) > 0 if t.get("return_20d") is not None else None,
        (t.get("return_60d") or 0) > 0 if t.get("return_60d") is not None else None,
        40 <= t["rsi14"] <= 70 if t.get("rsi14") is not None else None,
        (t.get("max_drawdown_1y") or -1) > -0.30 if t.get("max_drawdown_1y") is not None else None,
    ]
    return _score_from_checks(checks)[0]


def score_fundamentals(f: dict[str, Any]) -> tuple[float, int]:
    def n(key: str):
        value = f.get(key)
        return value if isinstance(value, (int, float)) else None

    pe, pb, roe, dte, rg, eg, pm = map(n, [
        "trailingPE", "priceToBook", "returnOnEquity", "debtToEquity", "revenueGrowth", "earningsGrowth", "profitMargins"
    ])
    checks: list[bool | None] = [
        0 < pe < 25 if pe is not None else None,
        0 < pb < 5 if pb is not None else None,
        roe > 0.10 if roe is not None else None,
        dte < 150 if dte is not None else None,
        rg > 0 if rg is not None else None,
        eg > 0 if eg is not None else None,
        pm > 0.05 if pm is not None else None,
    ]
    return _score_from_checks(checks)


def score_liquidity(t: dict[str, Any]) -> float:
    value = t.get("avg_value_traded_20d_idr")
    if value is None:
        return 40.0
    if value >= 50_000_000_000:
        return 100.0
    if value >= 10_000_000_000:
        return 85.0
    if value >= 2_000_000_000:
        return 65.0
    if value >= 500_000_000:
        return 45.0
    return 25.0


def evidence_completeness(price_rows: int, fundamental_count: int) -> float:
    price_component = 70.0 if price_rows >= 120 else 55.0 if price_rows >= 60 else 35.0
    fundamental_component = min(30.0, fundamental_count * (30.0 / 7.0))
    return min(100.0, price_component + fundamental_component)


def confidence_score(technical: float, fundamental: float, liquidity: float, completeness: float) -> float:
    return round(0.30 * technical + 0.25 * fundamental + 0.20 * liquidity + 0.25 * completeness, 2)
