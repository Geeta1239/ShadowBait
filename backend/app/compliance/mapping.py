"""Central compliance-oriented mapping for the controlled ShadowBait fixtures.

This is a technical mapping to privacy-choice and consumer-autonomy principles,
not a legal determination that a page violates CCPA/CPRA.
"""
from __future__ import annotations

from typing import Any, Mapping

COMPLIANCE_MAP: dict[str, dict[str, str]] = {
    "DP01": {
        "category": "False Urgency",
        "principle": "Clear and balanced privacy or purchase choices",
        "description": "Scarcity or countdown signals pressure a decision before the user can evaluate the choice.",
        "harm": "Pressures the user to act quickly instead of making an informed choice.",
        "recommendation": "Use truthful availability information and a fixed, clearly stated end time.",
    },
    "DP02": {
        "category": "Basket Sneaking",
        "principle": "Affirmative and intentional choice",
        "description": "An optional add-on is selected before the user affirmatively chooses it.",
        "harm": "Can add cost or consent without a clear affirmative action.",
        "recommendation": "Leave optional add-ons unchecked and explain them in neutral language.",
    },
    "DP03": {
        "category": "Confirm Shaming",
        "principle": "Understandable and non-manipulative language",
        "description": "The decline option uses guilt or shame to influence the user’s choice.",
        "harm": "Steers the user toward an optional action through emotional pressure.",
        "recommendation": "Use short, neutral choices such as ‘Continue without donation.’",
    },
    "DP05": {
        "category": "Subscription Trap",
        "principle": "Symmetrical start and stop choices",
        "description": "Starting a recurring service is easier or more visible than cancelling it.",
        "harm": "Makes it harder to stop recurring charges than to begin them.",
        "recommendation": "Offer cancellation with the same visibility and simplicity as sign-up.",
    },
    "DP06": {
        "category": "Interface Interference",
        "principle": "Balanced presentation of consequential choices",
        "description": "Visual hierarchy makes one consequential option prominent while muting another.",
        "harm": "Obscures the lower-commitment or privacy-protective alternative.",
        "recommendation": "Give consequential alternatives comparable contrast, size, and clarity.",
    },
    "DP07": {
        "category": "Bait and Switch",
        "principle": "Accurate and consistent choice outcome",
        "description": "The selected offer changes or becomes unavailable at a later step.",
        "harm": "Wastes the user’s time and redirects the decision toward a more expensive outcome.",
        "recommendation": "Keep the advertised outcome available or disclose any change immediately.",
    },
    "DP08": {
        "category": "Drip Pricing",
        "principle": "Clear and complete price disclosure",
        "description": "Mandatory fees appear later instead of with the initial price.",
        "harm": "Prevents an accurate comparison until late in the transaction.",
        "recommendation": "Show the complete payable estimate beside the initial price.",
    },
}


def mapping_for(pattern_id: str | None, finding: Mapping[str, Any] | None = None) -> dict[str, Any]:
    key = str(pattern_id or "")
    base = dict(COMPLIANCE_MAP.get(key, {
        "category": str((finding or {}).get("name") or "Unmapped pattern"),
        "principle": "Human-readable and balanced choice",
        "description": "This finding has not yet been assigned a project compliance mapping.",
        "harm": "Requires human review before a compliance conclusion.",
        "recommendation": "Review the interface and provide a clear, neutral alternative.",
    }))
    status = str((finding or {}).get("status") or (finding or {}).get("scanner_status") or "CANDIDATE").upper()
    base.update({
        "pattern_id": key,
        "status": status if status in {"VERIFIED", "CANDIDATE", "SIMULATED", "EXCLUDED"} else "CANDIDATE",
        "scope": "technical mapping for human review",
        "source": "project CCPA/CPRA dark-pattern principles mapping",
    })
    return base


def attach_compliance(finding: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(finding)
    pattern_id = result.get("id") or result.get("pattern_id") or result.get("scanner_pattern_id") or result.get("rule_id")
    result["compliance"] = mapping_for(str(pattern_id) if pattern_id else None, result)
    return result


def summarize_compliance(findings: list[Mapping[str, Any]]) -> dict[str, Any]:
    mappings = [item.get("compliance") or mapping_for(str(item.get("id") or item.get("pattern_id")), item) for item in findings]
    return {
        "mapped_findings": len(mappings),
        "verified_mappings": sum(1 for item in mappings if item.get("status") == "VERIFIED"),
        "categories": sorted({str(item.get("category")) for item in mappings}),
        "principles": sorted({str(item.get("principle")) for item in mappings}),
        "scope": "technical mapping for human review; not a legal determination",
    }
