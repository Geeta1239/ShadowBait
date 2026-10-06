from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.database.repository import ScanDatabase


def test_database_persists_scan_evidence_and_findings(tmp_path: Path):
    database = ScanDatabase(tmp_path / "shadowbait.sqlite3")
    report = {
        "scan": {
            "scan_id": "live-db-test",
            "target": "http://localhost:3000",
            "pattern_ids": ["DP01"],
            "started_at": "2026-10-06T10:00:00+00:00",
            "finished_at": "2026-10-06T10:00:05+00:00",
        },
        "findings": [
            {
                "id": "DP01",
                "route": "/product",
                "selector": "#scarcity-text",
                "observed_text": "Only 2 left!",
                "screenshot_file": "evidence/live-scans/live-db-test/screenshots/dp01.png",
                "element_state": {"visible": True},
                "m2_findings": [
                    {
                        "rule_id": "DP02",
                        "name": "False Urgency",
                        "severity": "MEDIUM",
                        "confidence": 0.95,
                        "status": "VERIFIED",
                        "detection_source": "rules",
                        "explanation": "Scarcity wording creates pressure.",
                        "recommendation": "Show truthful stock.",
                        "evidence": {"selector": "#scarcity-text"},
                    }
                ],
            }
        ],
        "summary": {"verified_findings": 1, "pages_scanned": 1},
    }

    database.create_scan("live-db-test", "http://localhost:3000", ["DP01"])
    database.update_scan("live-db-test", status="RUNNING", started_at=report["scan"]["started_at"])
    database.save_report(report)

    scan = database.get_scan("live-db-test")
    assert scan is not None
    assert scan["status"] == "COMPLETED"
    assert scan["summary"]["verified_findings"] == 1
    assert database.list_scans()[0]["id"] == "live-db-test"

    import sqlite3

    with sqlite3.connect(tmp_path / "shadowbait.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == 1
