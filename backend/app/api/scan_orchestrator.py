"""Small orchestration primitives shared by the scan HTTP API.

This module intentionally has no web-framework dependency.  The prototype's
inspection server can use it today, while a future FastAPI service can reuse the
same request/response contract without changing scanner evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Mapping
from urllib.parse import urlparse


@dataclass
class ScanRecord:
    scan_id: str
    target: str
    pattern_ids: list[str]
    status: str = "QUEUED"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None
    report: dict[str, Any] | None = None

    def summary(self) -> dict[str, Any]:
        report_summary = (self.report or {}).get("summary", {})
        return {
            "scan_id": self.scan_id,
            "target": self.target,
            "pattern_ids": self.pattern_ids,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "summary": report_summary,
        }


class ScanStore:
    """Thread-safe process-local scan registry.

    JSON reports remain the durable source of evidence.  The registry only
    tracks lifecycle state so the POST/GET API can report progress while a
    background browser scan is running.  A restarted process can still load a
    completed report from disk in the HTTP server.
    """

    def __init__(self) -> None:
        self._records: dict[str, ScanRecord] = {}
        self._lock = Lock()

    def create(self, scan_id: str, target: str, pattern_ids: list[str]) -> ScanRecord:
        record = ScanRecord(scan_id=scan_id, target=target, pattern_ids=pattern_ids)
        with self._lock:
            self._records[scan_id] = record
        return record

    def get(self, scan_id: str) -> ScanRecord | None:
        with self._lock:
            return self._records.get(scan_id)

    def update(self, scan_id: str, **changes: Any) -> ScanRecord | None:
        with self._lock:
            record = self._records.get(scan_id)
            if record is None:
                return None
            for key, value in changes.items():
                setattr(record, key, value)
            return record

    def list(self) -> list[ScanRecord]:
        with self._lock:
            return list(reversed(list(self._records.values())))


def validate_scan_request(payload: Mapping[str, Any], known_pattern_ids: set[str]) -> tuple[str, list[str]]:
    """Validate POST /api/scans input and return target plus selected patterns."""
    target = str(payload.get("url") or payload.get("target") or "").strip().rstrip("/")
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an absolute http:// or https:// URL")

    requested = payload.get("pattern_ids", payload.get("patterns"))
    if requested is None:
        pattern_ids = sorted(known_pattern_ids)
    elif not isinstance(requested, list) or not all(isinstance(item, str) for item in requested):
        raise ValueError("pattern_ids must be a list of strings")
    else:
        pattern_ids = list(dict.fromkeys(requested))
        unknown = sorted(set(pattern_ids) - known_pattern_ids)
        if unknown:
            raise ValueError(f"unknown pattern_ids: {', '.join(unknown)}")
        if not pattern_ids:
            raise ValueError("pattern_ids must contain at least one known pattern")
    return target, pattern_ids
