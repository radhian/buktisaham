import pytest

from app.config import Settings
from app.services.market.yfinance_provider import YFinanceProvider


def test_idx_ticker_normalization():
    p = YFinanceProvider()
    assert p.normalize_ticker("bbca") == "BBCA.JK"
    assert p.normalize_ticker("TLKM.JK") == "TLKM.JK"


def test_free_only_policy_rejects_paid_provider():
    s = Settings(
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379/0",
        free_only_market_data=True,
        market_data_provider="paid_vendor",
    )
    with pytest.raises(RuntimeError):
        s.enforce_market_data_policy()
