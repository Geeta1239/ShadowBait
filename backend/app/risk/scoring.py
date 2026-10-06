"""Explainable risk scoring for the current evidence and M2 findings."""
from __future__ import annotations

from typing import Any, Mapping

from app.detection.rules_config import RULES_CONFIG

SEVERITY_WEIGHTS = {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}
# These verified demo fixtures are owned by M1/M3 but still need a risk weight
# until their dedicated detection modules are connected.
DEMO_SEVERITIES = {
    "DP01": "MEDIUM",  # scanner False Urgency; M2 canonical rule is DP02
    "DP02": "HIGH",    # scanner Basket Sneaking; M2 canonical rule is DP01
    "DP03": "MEDIUM",
    "DP05": "HIGH",    # Subscription Trap
    "DP06": "MEDIUM",
    "DP07": "MEDIUM",
    "DP08": "HIGH",
}


def severity_for(finding: Mapping[str, Any]) -> str:
    """Resolve severity from the canonical M2 rule, then the scanner fixture."""
    canonical_rule = finding.get("rule_id")
    if canonical_rule in RULES_CONFIG:
        return RULES_CONFIG[canonical_rule].severity
    for key in (finding.get("pattern_id"), finding.get("scanner_pattern_id"), finding.get("id")):
        if key in DEMO_SEVERITIES:
            return DEMO_SEVERITIES[key]
        if key in RULES_CONFIG:
            return RULES_CONFIG[key].severity
    return str(finding.get("severity") or "MEDIUM").upper()


def completeness_multiplier(status: str | None) -> float:
    return 1.0 if str(status or "").upper() == "VERIFIED" else 0.5


def score_one(finding: Mapping[str, Any]) -> dict[str, Any]:
    severity = severity_for(finding)
    weight = SEVERITY_WEIGHTS.get(severity, SEVERITY_WEIGHTS["MEDIUM"])
    confidence = float(finding.get("confidence", 1.0 if finding.get("status") == "VERIFIED" else 0.5))
    confidence = max(0.0, min(1.0, confidence))
    completeness = completeness_multiplier(finding.get("status"))
    score = round(weight * confidence * completeness, 2)
    return {
        "pattern_id": finding.get("rule_id", finding.get("pattern_id", finding.get("id"))),
        "name": finding.get("name", finding.get("pattern_name")),
        "severity": severity,
        "severity_weight": weight,
        "confidence": confidence,
        "evidence_completeness": completeness,
        "score": score,
    }


def calculate_risk(report: Mapping[str, Any]) -> dict[str, Any]:
    """Calculate one explainable score per captured scanner finding.

    When M2 has classified a scanner item, its strongest M2 result is used. If
    M2 does not own that pattern yet, the verified M1 evidence remains in the
    risk calculation with its demo/rule-config severity and full evidence
    completeness. This avoids double-counting M1 and M2 for the same pattern.
    """
    scored: list[dict[str, Any]] = []
    for item in report.get("findings", []) if isinstance(report.get("findings", []), list) else []:
        m2 = item.get("m2_findings", [])
        if isinstance(m2, list) and m2:
            strongest = max(m2, key=lambda value: float(value.get("confidence", 0.0)))
            scored.append(score_one(strongest))
        else:
            scored.append(score_one(item))

    risk_score = round(sum(item["score"] for item in scored), 2)
    if risk_score >= 6:
        risk_level = "HIGH"
    elif risk_score >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "scored_findings": scored,
        "verified_findings": sum(1 for item in scored if item["evidence_completeness"] == 1.0),
        "candidate_findings": sum(1 for item in scored if item["evidence_completeness"] < 1.0),
        "high_severity_findings": sum(1 for item in scored if item["severity"] == "HIGH"),
        "medium_severity_findings": sum(1 for item in scored if item["severity"] == "MEDIUM"),
        "low_severity_findings": sum(1 for item in scored if item["severity"] == "LOW"),
    }
