"""Bridge Member 1 scanner reports into the Member 2 detection contract.

Member 1 owns browser evidence (route, selector, visible text, screenshot and
state). Member 2 owns language classification. This adapter normalizes the
scanner's report shape, sends only text to the M2 rule engine, and then merges
the scanner evidence back onto each M2 finding.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

# Allow ``python backend/app/integration/m1_m2_adapter.py`` as well as package imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.detection.evidence_engine import attach_scanner_evidence
from app.detection.rule_engine import analyze_text


# M2 currently implements these language-level patterns. The scanner may report
# more patterns, but those are handled by M1/M3 and will simply produce no M2
# classification here.
SUPPORTED_M2_RULE_IDS = {"DP02", "DP03"}
SUPPORTED_M2_PATTERNS = {"FALSE_URGENCY", "CONFIRM_SHAMING"}


def _first(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first present, non-None value among aliases."""
    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value
    return default


def normalize_m1_finding(finding: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize current and legacy M1 finding field names.

    Current scanner names are ``pattern_id``, ``page_url`` and
    ``evidence_text``. The live inspection API uses ``id``, ``route`` and
    ``observed_text``. Supporting both lets saved reports from either scanner
    version flow through the same M2 contract.
    """
    scanner_pattern_id = _first(finding, "pattern_id", "id")
    scanner_pattern_name = _first(finding, "pattern_name", "name")
    page = _first(finding, "page_url", "page", "route", default="")
    selector = _first(finding, "selector")
    evidence_text = _first(finding, "evidence_text", "observed_text", "text", default="")
    screenshot = _first(finding, "screenshot", "screenshot_file", "image")

    # Keep the complete M1 state available to downstream consumers without
    # forcing M2 to understand scanner-specific fields.
    return {
        "scanner_pattern_id": scanner_pattern_id,
        "scanner_pattern_name": scanner_pattern_name,
        "page": page,
        "selector": selector,
        "text": evidence_text or "",
        "screenshot": screenshot,
        "element_state": _first(finding, "element_state", default={}),
        "scanner_status": _first(finding, "status", default="CAPTURED"),
        "scanner_finding": dict(finding),
    }


def _iter_findings(report: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    """Yield findings from a normal report or a single-finding payload."""
    findings = report.get("findings", [])
    if isinstance(findings, list):
        yield from (item for item in findings if isinstance(item, Mapping))
    elif isinstance(findings, Mapping):
        yield findings


def _is_supported_m2_result(result: Mapping[str, Any]) -> bool:
    return result.get("rule_id") in SUPPORTED_M2_RULE_IDS or result.get("pattern") in SUPPORTED_M2_PATTERNS


def classify_m1_finding(raw_finding: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Classify one scanner finding and return evidence-backed M2 results."""
    evidence = normalize_m1_finding(raw_finding)
    if not evidence["text"]:
        return []

    m2_findings = analyze_text(evidence["text"], page=evidence["page"])
    # The M2 engine works sentence-by-sentence. A single scanner finding may
    # contain several sentences of the same pattern, so keep one strongest
    # classification per canonical rule while retaining distinct rules.
    best_by_rule: Dict[str, Dict[str, Any]] = {}
    for m2_finding in m2_findings:
        if not _is_supported_m2_result(m2_finding):
            continue
        rule_id = str(m2_finding["rule_id"])
        previous = best_by_rule.get(rule_id)
        if previous is None or m2_finding.get("confidence", 0) > previous.get("confidence", 0):
            best_by_rule[rule_id] = m2_finding

    results: List[Dict[str, Any]] = []
    for m2_finding in best_by_rule.values():
        merged = attach_scanner_evidence(
            m2_finding,
            selector=evidence["selector"],
            page=evidence["page"],
            screenshot=evidence["screenshot"],
        )
        # Preserve the complete scanner evidence text for the UI card.
        merged["evidence"]["text"] = evidence["text"]
        # M2's canonical rule ID remains in rule_id; these fields identify the
        # original M1 DOM fixture and state.
        merged["scanner_pattern_id"] = evidence["scanner_pattern_id"]
        merged["scanner_pattern_name"] = evidence["scanner_pattern_name"]
        merged["scanner_status"] = evidence["scanner_status"]
        merged["element_state"] = evidence["element_state"]
        results.append(merged)
    return results


def process_m1_report(report_path: str | Path) -> List[Dict[str, Any]]:
    """Read an M1 report and return evidence-backed M2 findings.

    Findings that do not contain usable text are skipped. Findings belonging to
    M1/M3-only patterns are allowed through the text engine but are omitted when
    M2 produces no supported classification. A returned result is VERIFIED only
    when text, selector and screenshot are all present; otherwise the shared
    evidence engine leaves it as a candidate.
    """
    report_path = Path(report_path)
    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    results: List[Dict[str, Any]] = []
    for raw_finding in _iter_findings(report):
        results.extend(classify_m1_finding(raw_finding))

    return results


if __name__ == "__main__":
    report = "evidence/member1-step2/member1-step2-report.json"
    print(json.dumps(process_m1_report(report), indent=2, ensure_ascii=False))
