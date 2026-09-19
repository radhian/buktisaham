from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class MarketQuote:
    ticker: str
    provider: str
    currency: str | None
    last_price: float
    previous_close: float | None
    change_pct: float | None
    market_time: datetime | None
    source_uri: str


class MarketDataError(RuntimeError):
    pass


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    def normalize_ticker(self, ticker: str) -> str: ...

    @abstractmethod
    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame: ...

    @abstractmethod
    def get_quote(self, ticker: str) -> MarketQuote: ...

    @abstractmethod
    def get_fundamentals(self, ticker: str) -> dict[str, Any]: ...
