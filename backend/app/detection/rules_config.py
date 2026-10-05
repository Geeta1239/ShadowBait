"""Central, configurable rule definitions DP01-DP05 (from the official plan, section 4).

M2 DETECTS:    DP02 (False Urgency, NLP side) and DP03 (Confirm Shaming).
M2 CONFIGURES: DP01, DP04, DP05 - listed here so the engine, the contract and the
               recommendations are consistent, but their detection belongs to M1 / M3.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

PATTERN_FALSE_URGENCY = "FALSE_URGENCY"
PATTERN_CONFIRM_SHAMING = "CONFIRM_SHAMING"
PATTERN_NONE = "NONE"


@dataclass(frozen=True)
class RuleConfig:
    rule_id: str
    name: str
    method: str            # DOM | NLP + DOM | NLP | PRICE_FLOW | PRICE_ANALYSIS
    severity: str          # HIGH | MEDIUM | LOW  (fixed per rule, as in the plan)
    pattern: str           # model-level label
    description: str
    recommendation: str
    detector_owner: str    # which member writes the detection logic
    m2_detects: bool       # True only where M2 implements the detection


RULES_CONFIG: Dict[str, RuleConfig] = {
    "DP01": RuleConfig(
        "DP01", "Basket Sneaking", "DOM", "HIGH", "BASKET_SNEAKING",
        "Optional extras (e.g. a donation) added to the basket without the user's action.",
        "Leave optional checkbox unchecked.",
        detector_owner="M1", m2_detects=False),
    "DP02": RuleConfig(
        "DP02", "False Urgency", "NLP + DOM", "MEDIUM", PATTERN_FALSE_URGENCY,
        "Scarcity or time-pressure messaging (countdowns, 'only N left') that pressures a purchase.",
        "Use neutral, factual availability information and avoid fabricated or "
        "pressure-inducing scarcity or countdown messaging.",
        detector_owner="M2 (language) + M1 (DOM timers)", m2_detects=True),
    "DP03": RuleConfig(
        "DP03", "Confirm Shaming", "NLP", "MEDIUM", PATTERN_CONFIRM_SHAMING,
        "Decline option worded to make the user feel guilty or foolish for refusing.",
        "Provide a neutral decline option without guilt-inducing or manipulative "
        "language (for example, 'Continue without offer').",
        detector_owner="M2", m2_detects=True),
    "DP04": RuleConfig(
        "DP04", "Drip Pricing", "PRICE_FLOW", "HIGH", "DRIP_PRICING",
        "Mandatory fees revealed only during checkout, after the initial price was shown.",
        "Show all mandatory fees in the price displayed at the start of the flow.",
        detector_owner="M3", m2_detects=False),
    "DP05": RuleConfig(
        "DP05", "Misleading Discount", "PRICE_ANALYSIS", "MEDIUM", "MISLEADING_DISCOUNT",
        "Discount shown against an unverifiable or inflated reference price.",
        "Use a verifiable reference price and display discounts accurately.",
        detector_owner="M3", m2_detects=False),
}


def get_rule(rule_id: str) -> RuleConfig:
    return RULES_CONFIG[rule_id]


def list_rules() -> List[RuleConfig]:
    return list(RULES_CONFIG.values())
