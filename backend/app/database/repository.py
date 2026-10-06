"""SQLite persistence for ShadowBait scan history and evidence."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Mapping


class ScanDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._lock, self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    target_url TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    overall_risk REAL,
                    risk_level TEXT,
                    pattern_ids_json TEXT NOT NULL DEFAULT '[]',
                    report_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    pattern_id TEXT NOT NULL,
                    route TEXT,
                    selector TEXT,
                    text TEXT,
                    screenshot_path TEXT,
                    element_state_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    pattern_id TEXT NOT NULL,
                    name TEXT,
                    severity TEXT,
                    confidence REAL,
                    status TEXT,
                    detection_source TEXT,
                    explanation TEXT,
                    recommendation TEXT,
                    evidence_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_evidence_scan_id ON evidence(scan_id);
                CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
                """
            )

    def create_scan(self, scan_id: str, target_url: str, pattern_ids: list[str], status: str = "QUEUED") -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as db:
            db.execute(
                """INSERT OR REPLACE INTO scans
                   (id, target_url, status, pattern_ids_json, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (scan_id, target_url, status, json.dumps(pattern_ids), now),
            )

    def update_scan(self, scan_id: str, **changes: Any) -> None:
        allowed = {"target_url", "started_at", "finished_at", "status", "overall_risk", "risk_level", "pattern_ids_json", "report_json", "error"}
        fields = [(key, value) for key, value in changes.items() if key in allowed]
        if not fields:
            return
        assignments = ", ".join(f"{key} = ?" for key, _ in fields)
        values = [value for _, value in fields] + [scan_id]
        with self._lock, self._connect() as db:
            db.execute(f"UPDATE scans SET {assignments} WHERE id = ?", values)

    def save_report(self, report: Mapping[str, Any]) -> None:
        scan = dict(report.get("scan", {}))
        scan_id = str(scan["scan_id"])
        findings = report.get("findings", [])
        summary = dict(report.get("summary", {}))
        self.create_scan(scan_id, str(scan.get("target", "")), list(scan.get("pattern_ids", [])), status="COMPLETED")
        with self._lock, self._connect() as db:
            db.execute(
                """UPDATE scans SET started_at=?, finished_at=?, status=?, report_json=?
                   WHERE id=?""",
                (
                    scan.get("started_at"),
                    scan.get("finished_at"),
                    "COMPLETED",
                    json.dumps(report, ensure_ascii=False),
                    scan_id,
                ),
            )
            db.execute("DELETE FROM evidence WHERE scan_id = ?", (scan_id,))
            db.execute("DELETE FROM findings WHERE scan_id = ?", (scan_id,))
            for item in findings if isinstance(findings, list) else []:
                db.execute(
                    """INSERT INTO evidence
                       (scan_id, pattern_id, route, selector, text, screenshot_path, element_state_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        scan_id,
                        str(item.get("id", item.get("pattern_id", ""))),
                        item.get("route"),
                        item.get("selector"),
                        item.get("observed_text", item.get("evidence_text", "")),
                        item.get("screenshot_file", item.get("screenshot")),
                        json.dumps(item.get("element_state", {}), ensure_ascii=False),
                    ),
                )
                for finding in item.get("m2_findings", []) if isinstance(item.get("m2_findings", []), list) else []:
                    db.execute(
                        """INSERT INTO findings
                           (scan_id, pattern_id, name, severity, confidence, status,
                            detection_source, explanation, recommendation, evidence_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            scan_id,
                            finding.get("rule_id", finding.get("pattern", "")),
                            finding.get("name", finding.get("pattern")),
                            finding.get("severity"),
                            finding.get("confidence"),
                            finding.get("status"),
                            finding.get("detection_source"),
                            finding.get("explanation"),
                            finding.get("recommendation"),
                            json.dumps(finding.get("evidence", {}), ensure_ascii=False),
                        ),
                    )

    def get_scan(self, scan_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["pattern_ids"] = json.loads(result.pop("pattern_ids_json") or "[]")
        report_json = result.pop("report_json")
        result.pop("created_at", None)
        result.pop("error", None) if result.get("error") is None else None
        result["summary"] = (json.loads(report_json).get("summary", {}) if report_json else {})
        return result

    def list_scans(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT id FROM scans ORDER BY created_at DESC").fetchall()
        return [item for row in rows if (item := self.get_scan(row["id"])) is not None]
