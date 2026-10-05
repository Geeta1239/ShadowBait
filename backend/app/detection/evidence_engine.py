"""Builds the contract's evidence object and merges scanner-supplied evidence.

M2 only knows the TEXT. selector / page / screenshot come from M1 (scanner) or M3.
Rule (plan, Phase 4): no evidence = not a verified finding.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .models import STATUS_VERIFIED


def build_evidence(text: str, page: Optional[str] = None, selector: Optional[str] = None,
                   screenshot: Optional[str] = None) -> Dict[str, Optional[str]]:
    return {"text": text, "selector": selector, "page": page, "screenshot": screenshot}


def attach_scanner_evidence(finding: Dict[str, Any], *, selector: Optional[str] = None,
                            page: Optional[str] = None,
                            screenshot: Optional[str] = None) -> Dict[str, Any]:
    """Return a copy of a finding dict with scanner evidence filled in.

    Status becomes VERIFIED only when text, selector AND screenshot are all present.
    """
    out = dict(finding)
    ev = dict(out.get("evidence") or {})
    if selector is not None:
        ev["selector"] = selector
    if page is not None:
        ev["page"] = page
    if screenshot is not None:
        ev["screenshot"] = screenshot
    out["evidence"] = ev
    if ev.get("text") and ev.get("selector") and ev.get("screenshot"):
        out["status"] = STATUS_VERIFIED
    return out
