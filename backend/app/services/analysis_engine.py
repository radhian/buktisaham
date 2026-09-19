from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from app.quant import (
    build_scenarios,
    compute_technicals,
    confidence_score,
    evidence_completeness,
    score_fundamentals,
    score_liquidity,
    score_technicals,
)
from app.services.evidence import content_hash, fundamentals_evidence, market_evidence
from app.services.market import MarketDataProvider, get_market_provider
from app.services.ollama_client import OllamaClient
from app.services.policy_engine import decide_action


class AnalysisEngine:
    def __init__(
        self,
        market_provider: MarketDataProvider | None = None,
        ollama_client: OllamaClient | None = None,
    ):
        self.market = market_provider or get_market_provider()
        self.ollama = ollama_client or OllamaClient()

    def analyze(
        self,
        *,
        ticker: str,
        horizon_days: int,
        capital_idr: str,
        progress_callback: Callable[[str, int, str], None] | None = None,
    ) -> dict[str, Any]:
        def progress(stage: str, value: int, message: str) -> None:
            if progress_callback:
                progress_callback(stage, value, message)

        symbol = self.market.normalize_ticker(ticker)
        progress("collect", 12, f"Collecting free EOD market data for {symbol}")
        history = self.market.get_history(symbol, period="1y", interval="1d")
        fundamentals = self.market.get_fundamentals(symbol)
        progress("validate", 30, f"Validating freshness and evidence coverage for {symbol}")
        technicals = compute_technicals(history)
        progress("score", 48, f"Computing deterministic technical, fundamental, and liquidity scores for {symbol}")
        technical_score = round(score_technicals(technicals), 2)
        fundamental_score, fundamental_count = score_fundamentals(fundamentals)
        fundamental_score = round(fundamental_score, 2)
        liquidity_score = round(score_liquidity(technicals), 2)
        completeness = round(evidence_completeness(len(history), fundamental_count), 2)
        confidence = confidence_score(technical_score, fundamental_score, liquidity_score, completeness)
        scenario_bundle = build_scenarios(technicals, horizon_days)
        progress("scenario", 66, f"Building Bear, Base, and Bull scenarios for {symbol}")

        policy = decide_action(
            expected_return=scenario_bundle["expected_return"],
            bear_downside=scenario_bundle["bear_downside"],
            confidence=confidence,
            liquidity_score=liquidity_score,
            technical_score=technical_score,
            evidence_completeness=completeness,
        )
        progress("policy", 78, f"Applying deterministic recommendation policy for {symbol}")

        evidence = [market_evidence(symbol, technicals, provider=self.market.name)]
        if fundamentals.get("available"):
            evidence.append(fundamentals_evidence(symbol, fundamentals))

        deterministic = {
            "schema_version": "1.0",
            "ticker": symbol,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "horizon_days": horizon_days,
            "capital_idr": capital_idr,
            "market_data": {
                "provider": self.market.name,
                "mode": "FREE_ONLY",
                "paid_fallback_enabled": False,
                "source_uri": f"https://finance.yahoo.com/quote/{symbol}",
            },
            "technicals": technicals,
            "fundamentals": fundamentals,
            "scores": {
                "technical": technical_score,
                "fundamental": fundamental_score,
                "liquidity": liquidity_score,
                "evidence_completeness": completeness,
                "confidence": confidence,
            },
            "scenario_analysis": scenario_bundle,
            "research_action": policy.action,
            "policy_reasons": policy.reasons,
            "policy_hard_blocked": policy.hard_blocked,
            "evidence": evidence,
        }
        deterministic["deterministic_hash"] = content_hash(deterministic)

        ai_input = {
            "ticker": deterministic["ticker"],
            "as_of": deterministic["as_of"],
            "horizon_days": deterministic["horizon_days"],
            "research_action": deterministic["research_action"],
            "policy_reasons": deterministic["policy_reasons"],
            "scores": deterministic["scores"],
            "scenario_analysis": deterministic["scenario_analysis"],
            "technicals": deterministic["technicals"],
            "fundamentals": deterministic["fundamentals"],
        }
        progress("ai_review", 90, f"Requesting local Ollama evidence review for {symbol}")
        deterministic["ai_review"] = self.ollama.review(ai_input)
        progress("package", 97, f"Packaging the immutable evidence result for {symbol}")
        return deterministic
