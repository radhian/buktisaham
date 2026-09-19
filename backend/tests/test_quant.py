import pandas as pd

from app.quant.indicators import compute_technicals
from app.quant.scenarios import build_scenarios
from app.quant.scoring import confidence_score, evidence_completeness, score_liquidity, score_technicals


def sample_frame(rows=260):
    idx = pd.date_range("2025-01-01", periods=rows, freq="B")
    close = pd.Series([1000 + i * 2 for i in range(rows)], index=idx, dtype=float)
    volume = pd.Series([5_000_000 for _ in range(rows)], index=idx, dtype=float)
    return pd.DataFrame({"close": close, "volume": volume})


def test_technicals_and_scenarios_are_deterministic():
    tech = compute_technicals(sample_frame())
    assert tech["last_close"] == 1518.0
    assert tech["sma20"] is not None
    assert tech["return_60d"] > 0
    scenarios = build_scenarios(tech, 90)
    assert round(sum(x["probability"] for x in scenarios["scenarios"]), 10) == 1.0
    assert scenarios["scenarios"][0]["target_price"] < scenarios["scenarios"][2]["target_price"]


def test_scores_are_bounded():
    tech = compute_technicals(sample_frame())
    tscore = score_technicals(tech)
    lscore = score_liquidity(tech)
    complete = evidence_completeness(260, 5)
    confidence = confidence_score(tscore, 60, lscore, complete)
    assert 0 <= tscore <= 100
    assert 0 <= lscore <= 100
    assert 0 <= complete <= 100
    assert 0 <= confidence <= 100
