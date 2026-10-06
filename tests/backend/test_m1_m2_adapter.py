import json

import _bootstrap  # noqa: F401
from app.integration.m1_m2_adapter import normalize_m1_finding, process_m1_report


def test_normalize_current_scanner_shape():
    normalized = normalize_m1_finding(
        {
            "pattern_id": "DP01",
            "pattern_name": "False Urgency",
            "page_url": "/product",
            "selector": "#scarcity-text",
            "evidence_text": "ONLY 2 LEFT!",
            "screenshot": "evidence/scans/scan/screenshots/dp01.png",
        }
    )
    assert normalized["scanner_pattern_id"] == "DP01"
    assert normalized["page"] == "/product"
    assert normalized["text"] == "ONLY 2 LEFT!"


def test_normalize_live_inspection_shape():
    normalized = normalize_m1_finding(
        {
            "id": "DP03",
            "name": "Confirm Shaming",
            "route": "/checkout",
            "selector": "#confirm-shaming",
            "observed_text": "No, I don't want to save money.",
            "screenshot_file": "evidence/live-scans/scan/dp03.png",
        }
    )
    assert normalized["scanner_pattern_id"] == "DP03"
    assert normalized["scanner_pattern_name"] == "Confirm Shaming"
    assert normalized["page"] == "/checkout"
    assert normalized["text"] == "No, I don't want to save money."
    assert normalized["screenshot"].endswith("dp03.png")


def test_processes_all_supported_m2_patterns_and_attaches_evidence(tmp_path):
    report_path = tmp_path / "m1-report.json"
    report_path.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "pattern_id": "DP01",
                        "pattern_name": "False Urgency",
                        "page_url": "/product",
                        "selector": "#scarcity-text",
                        "evidence_text": "Only 2 left! Hurry!",
                        "screenshot": "screenshots/dp01.png",
                    },
                    {
                        "pattern_id": "DP03",
                        "pattern_name": "Confirm Shaming",
                        "page_url": "/checkout",
                        "selector": "#confirm-shaming",
                        "evidence_text": "No, I don't want to save money.",
                        "screenshot": "screenshots/dp03.png",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    results = process_m1_report(report_path)

    assert [result["rule_id"] for result in results] == ["DP02", "DP03"]
    assert [result["scanner_pattern_id"] for result in results] == ["DP01", "DP03"]
    assert all(result["status"] == "VERIFIED" for result in results)
    assert results[0]["evidence"] == {
        "text": "Only 2 left! Hurry!",
        "selector": "#scarcity-text",
        "page": "/product",
        "screenshot": "screenshots/dp01.png",
    }


def test_missing_screenshot_remains_candidate(tmp_path):
    report_path = tmp_path / "m1-report.json"
    report_path.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "pattern_id": "DP03",
                        "pattern_name": "Confirm Shaming",
                        "page_url": "/checkout",
                        "selector": "#confirm-shaming",
                        "evidence_text": "No, I don't want to save money.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    results = process_m1_report(report_path)

    assert len(results) == 1
    assert results[0]["status"] == "CANDIDATE"
    assert results[0]["evidence"]["screenshot"] is None


def test_m1_only_patterns_do_not_create_false_m2_findings(tmp_path):
    report_path = tmp_path / "m1-report.json"
    report_path.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "pattern_id": "DP02",
                        "pattern_name": "Basket Sneaking",
                        "page_url": "/checkout",
                        "selector": "#donation",
                        "evidence_text": "Optional donation is selected.",
                        "screenshot": "screenshots/dp02.png",
                    },
                    {
                        "pattern_id": "DP08",
                        "pattern_name": "Drip Pricing",
                        "page_url": "/checkout",
                        "selector": "[data-ccpa-pattern=DRIP_PRICING]",
                        "evidence_text": "Delivery and handling fees appear at checkout.",
                        "screenshot": "screenshots/dp08.png",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    assert process_m1_report(report_path) == []
