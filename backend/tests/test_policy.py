from app.config import Settings
from app.services.policy_engine import decide_action


def settings():
    return Settings(
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379/0",
        market_data_provider="yfinance",
        free_only_market_data=True,
    )


def test_buy_research_requires_all_gates():
    decision = decide_action(
        expected_return=0.20,
        bear_downside=-0.20,
        confidence=70,
        liquidity_score=80,
        technical_score=70,
        evidence_completeness=90,
        settings=settings(),
    )
    assert decision.action == "BUY_RESEARCH"


def test_incomplete_evidence_abstains():
    decision = decide_action(
        expected_return=0.25,
        bear_downside=-0.10,
        confidence=80,
        liquidity_score=90,
        technical_score=90,
        evidence_completeness=40,
        settings=settings(),
    )
    assert decision.action == "WATCH"
    assert decision.hard_blocked is True
