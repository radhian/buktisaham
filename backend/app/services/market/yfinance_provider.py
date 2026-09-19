from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
from app.services.market.base import MarketDataError, MarketDataProvider, MarketQuote


def _yf():
    import yfinance as yf
    return yf


class YFinanceProvider(MarketDataProvider):
    """Free-only MVP provider using Yahoo Finance public/unofficial endpoints via yfinance.

    This adapter intentionally has no paid fallback. Production/redistribution use must be
    separately reviewed against upstream terms and applicable data rights.
    """

    name = "yfinance"

    def normalize_ticker(self, ticker: str) -> str:
        value = ticker.strip().upper()
        if not value:
            raise MarketDataError("Ticker is required")
        if "." not in value:
            value = f"{value}.JK"
        return value

    @staticmethod
    def _source_uri(ticker: str) -> str:
        return f"https://finance.yahoo.com/quote/{ticker}"

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        symbol = self.normalize_ticker(ticker)
        try:
            frame = _yf().Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
        except Exception as exc:  # upstream client can throw many transport/parser exceptions
            raise MarketDataError(f"Unable to fetch free market data for {symbol}: {exc}") from exc
        if frame is None or frame.empty:
            raise MarketDataError(f"No free market data returned for {symbol}")
        frame = frame.copy()
        frame.columns = [str(c).lower().replace(" ", "_") for c in frame.columns]
        required = {"close", "volume"}
        missing = required.difference(frame.columns)
        if missing:
            raise MarketDataError(f"Market data for {symbol} is missing columns: {sorted(missing)}")
        return frame

    def get_quote(self, ticker: str) -> MarketQuote:
        symbol = self.normalize_ticker(ticker)
        frame = self.get_history(symbol, period="10d", interval="1d")
        closes = frame["close"].dropna()
        if closes.empty:
            raise MarketDataError(f"No usable close price returned for {symbol}")
        last = float(closes.iloc[-1])
        previous = float(closes.iloc[-2]) if len(closes) > 1 else None
        change = ((last / previous) - 1.0) if previous not in (None, 0.0) else None
        idx = closes.index[-1]
        if hasattr(idx, "to_pydatetime"):
            dt = idx.to_pydatetime()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = datetime.now(timezone.utc)
        currency = None
        try:
            currency = _yf().Ticker(symbol).fast_info.get("currency")
        except Exception:
            pass
        return MarketQuote(
            ticker=symbol,
            provider=self.name,
            currency=currency or "IDR",
            last_price=last,
            previous_close=previous,
            change_pct=change,
            market_time=dt,
            source_uri=self._source_uri(symbol),
        )

    def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        symbol = self.normalize_ticker(ticker)
        keys = [
            "longName",
            "sector",
            "industry",
            "marketCap",
            "trailingPE",
            "forwardPE",
            "priceToBook",
            "returnOnEquity",
            "debtToEquity",
            "revenueGrowth",
            "earningsGrowth",
            "profitMargins",
            "dividendYield",
            "currency",
        ]
        try:
            info = _yf().Ticker(symbol).get_info()
        except Exception:
            return {"ticker": symbol, "provider": self.name, "available": False}
        result = {k: info.get(k) for k in keys}
        result.update({"ticker": symbol, "provider": self.name, "available": True})
        return result
