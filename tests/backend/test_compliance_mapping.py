from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.compliance.mapping import attach_compliance, mapping_for, summarize_compliance


def test_basket_sneaking_mapping_contains_human_review_fields():
    mapping = mapping_for("DP02", {"status": "VERIFIED"})
    assert mapping["category"] == "Basket Sneaking"
    assert mapping["status"] == "VERIFIED"
    assert mapping["principle"]
    assert mapping["harm"]
    assert mapping["recommendation"]
    assert "not a legal" not in mapping["recommendation"].lower()


def test_attach_compliance_preserves_finding_and_adds_mapping():
    finding = attach_compliance({"id": "DP03", "name": "Confirm Shaming", "status": "VERIFIED"})
    assert finding["id"] == "DP03"
    assert finding["compliance"]["category"] == "Confirm Shaming"
    assert finding["compliance"]["scope"] == "technical mapping for human review"


def test_summary_counts_mappings_and_discloses_scope():
    summary = summarize_compliance([
        {"id": "DP01", "status": "VERIFIED"},
        {"id": "DP02", "status": "CANDIDATE"},
    ])
    assert summary["mapped_findings"] == 2
    assert summary["verified_mappings"] == 1
    assert "False Urgency" in summary["categories"]
    assert "not a legal determination" in summary["scope"]
