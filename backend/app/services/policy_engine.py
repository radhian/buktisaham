from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings, get_settings


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    reasons: list[str]
    hard_blocked: bool = False


def decide_action(
    *,
    expected_return: float,
    bear_downside: float,
    confidence: float,
    liquidity_score: float,
    technical_score: float,
    evidence_completeness: float,
    settings: Settings | None = None,
) -> PolicyDecision:
    s = settings or get_settings()
    reasons: list[str] = []

    if evidence_completeness < 60:
        return PolicyDecision(
            action="WATCH",
            reasons=[f"Evidence completeness {evidence_completeness:.1f}% is below the 60% MVP gate."],
            hard_blocked=True,
        )

    if confidence < s.policy_min_confidence:
        return PolicyDecision(
            action="WATCH",
            reasons=[f"Confidence {confidence:.1f} is below the configured floor {s.policy_min_confidence:.1f}."],
        )

    if expected_return >= s.policy_buy_expected_return:
        reasons.append(
            f"Expected return {expected_return:.1%} meets the {s.policy_buy_expected_return:.1%} research threshold."
        )
        if bear_downside < s.policy_max_bear_downside:
            reasons.append(
                f"Bear downside {bear_downside:.1%} breaches the {s.policy_max_bear_downside:.1%} downside limit."
            )
            return PolicyDecision(action="WATCH", reasons=reasons)
        if liquidity_score < s.policy_min_liquidity:
            reasons.append(f"Liquidity score {liquidity_score:.1f} is below {s.policy_min_liquidity:.1f}.")
            return PolicyDecision(action="WATCH", reasons=reasons)
        if technical_score < s.policy_min_technical:
            reasons.append(f"Technical score {technical_score:.1f} is below {s.policy_min_technical:.1f}.")
            return PolicyDecision(action="HOLD_RESEARCH", reasons=reasons)
        reasons.append("Configured downside, liquidity, and technical gates pass.")
        return PolicyDecision(action="BUY_RESEARCH", reasons=reasons)

    if expected_return <= s.policy_sell_expected_return:
        reasons.append(
            f"Expected return {expected_return:.1%} is at or below the {s.policy_sell_expected_return:.1%} sell-research threshold."
        )
        return PolicyDecision(action="SELL_RESEARCH", reasons=reasons)

    reasons.append("Expected return is between configured buy and sell research thresholds.")
    return PolicyDecision(action="HOLD_RESEARCH", reasons=reasons)
