from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.risk.scoring import calculate_risk, score_one


def test_verified_high_finding_uses_full_weight():
    scored = score_one({"id": "DP02", "name": "Basket Sneaking", "status": "VERIFIED"})
    assert scored["severity"] == "HIGH"
    assert scored["confidence"] == 1.0
    assert scored["score"] == 3.0


def test_candidate_is_discounted_by_completeness_multiplier():
    scored = score_one({"rule_id": "DP03", "name": "Confirm Shaming", "status": "CANDIDATE", "confidence": 0.8})
    assert scored["severity"] == "MEDIUM"
    assert scored["evidence_completeness"] == 0.5
    assert scored["score"] == 0.8


def test_report_uses_strongest_m2_result_without_double_counting():
    report = {
        "findings": [
            {
                "id": "DP01",
                "status": "VERIFIED",
                "m2_findings": [
                    {"rule_id": "DP02", "name": "False Urgency", "status": "VERIFIED", "confidence": 0.95},
                    {"rule_id": "DP02", "name": "False Urgency", "status": "VERIFIED", "confidence": 0.70},
                ],
            },
            {"id": "DP02", "name": "Basket Sneaking", "status": "VERIFIED", "m2_findings": []},
        ]
    }
    risk = calculate_risk(report)
    assert risk["risk_score"] == 4.9
    assert risk["risk_level"] == "MEDIUM"
    assert len(risk["scored_findings"]) == 2
    assert risk["high_severity_findings"] == 1


def test_full_demo_risk_reaches_high_threshold():
    report = {"findings": [{"id": "DP02", "name": "Basket Sneaking", "status": "VERIFIED", "m2_findings": []}] * 2}
    risk = calculate_risk(report)
    assert risk["risk_score"] == 6.0
    assert risk["risk_level"] == "HIGH"
