from app.config import get_settings
from app.services.market.base import MarketDataProvider


def get_market_provider() -> MarketDataProvider:
    settings = get_settings()
    settings.enforce_market_data_policy()
    if settings.market_data_provider == "yfinance":
        from app.services.market.yfinance_provider import YFinanceProvider

        return YFinanceProvider()
    raise RuntimeError(f"Unsupported market-data provider: {settings.market_data_provider}")


__all__ = ["get_market_provider", "MarketDataProvider"]
