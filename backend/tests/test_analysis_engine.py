import pandas as pd

from app.services.analysis_engine import AnalysisEngine
from app.services.market.base import MarketDataProvider, MarketQuote


class FakeMarket(MarketDataProvider):
    name = "yfinance"

    def normalize_ticker(self, ticker: str) -> str:
        return ticker.upper() if ticker.upper().endswith(".JK") else ticker.upper() + ".JK"

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        idx = pd.date_range("2025-01-01", periods=260, freq="B")
        return pd.DataFrame(
            {
                "close": [1000 + i * 1.5 for i in range(260)],
                "volume": [10_000_000] * 260,
            },
            index=idx,
        )

    def get_quote(self, ticker: str):
        return MarketQuote(self.normalize_ticker(ticker), self.name, "IDR", 1388.5, 1387, 0.001, None, "x")

    def get_fundamentals(self, ticker: str):
        return {
            "available": True,
            "ticker": self.normalize_ticker(ticker),
            "trailingPE": 15,
            "priceToBook": 2,
            "returnOnEquity": 0.18,
            "debtToEquity": 60,
            "revenueGrowth": 0.08,
            "earningsGrowth": 0.10,
            "profitMargins": 0.15,
        }


class FakeOllama:
    def review(self, analysis):
        return {"status": "ok", "provider": "ollama", "model": "test", "summary": "deterministic review"}


def test_analysis_never_delegates_action_to_ai():
    result = AnalysisEngine(FakeMarket(), FakeOllama()).analyze(
        ticker="BBCA", horizon_days=90, capital_idr="100000000"
    )
    assert result["ticker"] == "BBCA.JK"
    assert result["market_data"]["mode"] == "FREE_ONLY"
    assert result["market_data"]["paid_fallback_enabled"] is False
    assert result["research_action"] in {"BUY_RESEARCH", "HOLD_RESEARCH", "SELL_RESEARCH", "WATCH"}
    assert result["ai_review"]["summary"] == "deterministic review"
    assert result["deterministic_hash"].startswith("sha256:")
