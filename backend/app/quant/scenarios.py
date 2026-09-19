from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def build_scenarios(technicals: dict[str, Any], horizon_days: int) -> dict[str, Any]:
    price = float(technicals["last_close"])
    r20 = technicals.get("return_20d") or 0.0
    r60 = technicals.get("return_60d") or r20
    vol = technicals.get("annualized_volatility") or 0.30

    horizon_scale = _clamp(horizon_days / 90.0, 0.25, 2.0)
    base_return = _clamp((0.45 * r20 + 0.55 * r60) * horizon_scale, -0.25, 0.35)
    dispersion = _clamp(vol * ((horizon_days / 252.0) ** 0.5), 0.06, 0.35)
    bear_return = _clamp(base_return - 1.10 * dispersion, -0.55, 0.20)
    bull_return = _clamp(base_return + 1.10 * dispersion, -0.05, 0.65)

    scenarios = [
        {"name": "BEAR", "probability": 0.25, "return": bear_return, "target_price": price * (1 + bear_return)},
        {"name": "BASE", "probability": 0.50, "return": base_return, "target_price": price * (1 + base_return)},
        {"name": "BULL", "probability": 0.25, "return": bull_return, "target_price": price * (1 + bull_return)},
    ]
    expected_return = sum(x["probability"] * x["return"] for x in scenarios)
    return {
        "horizon_days": horizon_days,
        "scenarios": scenarios,
        "expected_return": expected_return,
        "bear_downside": bear_return,
    }
