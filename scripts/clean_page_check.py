"""False-positive integration check for the ethical comparison page.

The test verifies both layers that matter for baseline accuracy:
1. M1-style forbidden dark-pattern selectors are absent from /clean-page.
2. The production M2 rule engine classifies the clean page text as zero findings.

Run with the demo website active, for example:
  SHADOWBAIT_URL=http://127.0.0.1:3000 python scripts/clean_page_check.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))
from app.detection.rule_engine import analyze_text  # noqa: E402

BASE_URL = os.environ.get("SHADOWBAIT_URL", "http://127.0.0.1:3000").rstrip("/")
CHROMIUM_PATH = os.environ.get("SHADOWBAIT_CHROMIUM_PATH")
FORBIDDEN = [
    "#scarcity-text", "#offer-timer", "#donation", "#confirm-shaming",
    '[data-ccpa-pattern="SUBSCRIPTION_TRAP"]',
    '[data-ccpa-pattern="INTERFACE_INTERFERENCE"]',
    '[data-ccpa-pattern="BAIT_AND_SWITCH"]',
    '[data-ccpa-pattern="DRIP_PRICING"]',
]

with sync_playwright() as playwright:
    launch_options = {"executable_path": CHROMIUM_PATH} if CHROMIUM_PATH else {}
    browser = playwright.chromium.launch(**launch_options)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(BASE_URL + "/clean-page", wait_until="networkidle")
    observed_selectors = {selector: page.locator(selector).count() for selector in FORBIDDEN}
    body_text = page.locator("body").inner_text()
    m2_findings = analyze_text(body_text, page="/clean-page", classifier=None)
    browser.close()

forbidden_found = {selector: count for selector, count in observed_selectors.items() if count}
result = {
    "route": "/clean-page",
    "expected_verified_findings": 0,
    "observed_forbidden_selectors": forbidden_found,
    "m2_findings": m2_findings,
    "false_positives": len(forbidden_found) + len(m2_findings),
    "passed": not forbidden_found and not m2_findings,
}
print(json.dumps(result, indent=2, ensure_ascii=False))
if forbidden_found or m2_findings:
    raise SystemExit("clean-page false-positive test failed")
