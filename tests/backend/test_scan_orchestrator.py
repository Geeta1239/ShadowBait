from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.api.scan_orchestrator import ScanStore, validate_scan_request


KNOWN = {"DP01", "DP02", "DP03"}


def test_validate_default_request_selects_all_known_patterns():
    target, pattern_ids = validate_scan_request({"url": "http://127.0.0.1:3000"}, KNOWN)
    assert target == "http://127.0.0.1:3000"
    assert pattern_ids == sorted(KNOWN)


def test_validate_request_deduplicates_requested_patterns():
    target, pattern_ids = validate_scan_request(
        {"target": "https://example.test/", "pattern_ids": ["DP03", "DP03", "DP01"]},
        KNOWN,
    )
    assert target == "https://example.test"
    assert pattern_ids == ["DP03", "DP01"]


def test_validate_request_rejects_invalid_url_and_unknown_pattern():
    try:
        validate_scan_request({"url": "localhost:3000"}, KNOWN)
    except ValueError as exc:
        assert "absolute http" in str(exc)
    else:
        raise AssertionError("invalid URL should be rejected")

    try:
        validate_scan_request({"url": "http://localhost:3000", "pattern_ids": ["DP99"]}, KNOWN)
    except ValueError as exc:
        assert "DP99" in str(exc)
    else:
        raise AssertionError("unknown pattern should be rejected")


def test_scan_store_tracks_lifecycle_and_summary():
    store = ScanStore()
    record = store.create("live-test", "http://localhost:3000", ["DP01"])
    assert record.status == "QUEUED"
    store.update("live-test", status="COMPLETED", report={"summary": {"verified_findings": 1}})
    loaded = store.get("live-test")
    assert loaded is not None
    assert loaded.summary()["status"] == "COMPLETED"
    assert loaded.summary()["summary"]["verified_findings"] == 1
