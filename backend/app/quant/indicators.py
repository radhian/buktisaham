from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def _safe_float(value: Any) -> float | None:
    try:
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (TypeError, ValueError):
        return None


def rsi(series: pd.Series, period: int = 14) -> float | None:
    series = series.dropna().astype(float)
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gains = delta.clip(lower=0).rolling(period).mean()
    losses = (-delta.clip(upper=0)).rolling(period).mean()
    loss = losses.iloc[-1]
    gain = gains.iloc[-1]
    if pd.isna(loss) or pd.isna(gain):
        return None
    if loss == 0:
        return 100.0
    rs = gain / loss
    return float(100 - (100 / (1 + rs)))


def max_drawdown(series: pd.Series) -> float | None:
    prices = series.dropna().astype(float)
    if len(prices) < 2:
        return None
    running_max = prices.cummax()
    dd = (prices / running_max) - 1.0
    return _safe_float(dd.min())


def compute_technicals(frame: pd.DataFrame) -> dict[str, float | None]:
    close = frame["close"].dropna().astype(float)
    volume = frame["volume"].fillna(0).astype(float)
    if len(close) < 5:
        raise ValueError("At least five observations are required")

    returns = close.pct_change().dropna()

    def sma(window: int) -> float | None:
        return _safe_float(close.rolling(window).mean().iloc[-1]) if len(close) >= window else None

    def period_return(days: int) -> float | None:
        if len(close) <= days:
            return None
        prior = close.iloc[-(days + 1)]
        return _safe_float((close.iloc[-1] / prior) - 1.0) if prior else None

    annualized_vol = _safe_float(returns.std(ddof=1) * np.sqrt(252)) if len(returns) > 2 else None
    avg_volume_20 = _safe_float(volume.tail(20).mean()) if not volume.empty else None
    last_close = _safe_float(close.iloc[-1])
    avg_value_traded_20 = (
        last_close * avg_volume_20 if last_close is not None and avg_volume_20 is not None else None
    )

    return {
        "last_close": last_close,
        "sma20": sma(20),
        "sma50": sma(50),
        "sma200": sma(200),
        "rsi14": rsi(close, 14),
        "return_20d": period_return(20),
        "return_60d": period_return(60),
        "return_252d": period_return(252),
        "annualized_volatility": annualized_vol,
        "max_drawdown_1y": max_drawdown(close.tail(252)),
        "avg_volume_20d": avg_volume_20,
        "avg_value_traded_20d_idr": avg_value_traded_20,
    }
