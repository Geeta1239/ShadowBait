from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.environ.get("SHADOWBAIT_URL", "http://127.0.0.1:3000").rstrip("/")
EVIDENCE_ROOT = Path(os.environ.get("SHADOWBAIT_EVIDENCE_DIR", str(REPO_ROOT / "evidence"))).resolve()
RUN_ID = os.environ.get(
    "SHADOWBAIT_SCAN_ID",
    "SCAN-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
)
SCAN_ROOT = EVIDENCE_ROOT / "scans" / RUN_ID
SCREENSHOTS_DIR = SCAN_ROOT / "screenshots"
DOM_DIR = SCAN_ROOT / "dom"
REPORT_DIR = EVIDENCE_ROOT / "reports" / RUN_ID
for directory in (SCREENSHOTS_DIR, DOM_DIR, REPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def repo_path(path: Path) -> str:
    """Return a portable path for JSON while preserving external override paths."""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def slug(value: str) -> str:
    value = value.strip("/") or "home"
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "page"


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def box(locator) -> dict[str, float] | None:
    value = locator.bounding_box()
    if not value:
        return None
    return {key: round(float(number), 2) for key, number in value.items()}


def element_state(page, selector: str) -> dict[str, Any]:
    locator = page.locator(selector).first
    if locator.count() == 0:
        return {"selector": selector, "present": False}
    tag_name = locator.evaluate("el => el.tagName")
    input_like = tag_name in {"INPUT", "TEXTAREA", "SELECT"}
    input_type = locator.get_attribute("type")
    return {
        "selector": selector,
        "present": True,
        "visible": locator.is_visible(),
        "enabled": locator.is_enabled(),
        "tag": tag_name,
        "text": locator.inner_text() if not input_like else "",
        "value": locator.input_value() if input_like else None,
        "checked": locator.is_checked() if input_type in {"checkbox", "radio"} else None,
        "aria_label": locator.get_attribute("aria-label"),
        "data_ccpa_pattern": locator.get_attribute("data-ccpa-pattern"),
        "data_status": locator.get_attribute("data-status"),
        "bounding_box": box(locator),
        "computed": locator.evaluate("""el => {
            const s = getComputedStyle(el);
            return { color: s.color, backgroundColor: s.backgroundColor, display: s.display };
        }"""),
    }


def save_page(page, name: str) -> str:
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return repo_path(path)


def save_dom(page, name: str, selectors: list[str]) -> dict[str, str]:
    html_path = DOM_DIR / f"{name}.html"
    text_path = DOM_DIR / f"{name}-text.json"
    elements_path = DOM_DIR / f"{name}-elements.json"
    html_path.write_text(page.content(), encoding="utf-8")
    write_json(text_path, {"url": page.url, "title": page.title(), "visible_text": page.locator("body").inner_text()})
    write_json(elements_path, {"url": page.url, "selectors": [element_state(page, selector) for selector in selectors]})
    return {"html": repo_path(html_path), "text": repo_path(text_path), "elements": repo_path(elements_path)}


report: dict[str, Any] = {
    "scan": {
        "scan_id": RUN_ID,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "browser": "Chromium",
        "viewport": {"width": 1440, "height": 1000},
        "theme": "light",
        "member": "Member 1",
        "step": "Step 2/3 — inspect website and collect evidence",
        "output_root": repo_path(SCAN_ROOT),
    },
    "pages": [],
    "findings": [],
    "checks": [],
}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path="/usr/bin/chromium")
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
    page = context.new_page()

    def visit(route: str, selectors: list[str], screenshot_name: str) -> dict[str, Any]:
        page.goto(BASE_URL + route, wait_until="networkidle")
        dom = save_dom(page, screenshot_name, selectors)
        screenshot = save_page(page, screenshot_name)
        record = {
            "route": route,
            "url": page.url,
            "title": page.title(),
            "heading": page.locator("h1").first.inner_text() if page.locator("h1").count() else None,
            "screenshot": screenshot,
            "dom": dom,
            "selectors": [element_state(page, selector) for selector in selectors],
        }
        report["pages"].append(record)
        return record

    visit("/", ["#scarcity-text", "#offer-timer"], "shop-root")
    visit("/product", ["#scarcity-text", "#offer-timer", '[data-ccpa-pattern="FALSE_URGENCY"]'], "dp01-false-urgency-product")
    urgency = {
        "pattern_id": "DP01",
        "pattern_name": "False Urgency",
        "status": "VERIFIED",
        "page_url": "/product",
        "selector": "#scarcity-text",
        "related_selector": "#offer-timer",
        "evidence_text": page.locator("#scarcity-text").inner_text(),
        "timer_before": page.locator("#offer-timer").inner_text(),
        "screenshot": repo_path(SCREENSHOTS_DIR / "dp01-false-urgency-product.png"),
        "customer_harm": "Pressures people to buy before comparing options or verifying the claim.",
        "ethical_fix": "Show truthful stock and a fixed, clearly stated offer end time.",
    }
    page.wait_for_timeout(1200)
    urgency["timer_after"] = page.locator("#offer-timer").inner_text()
    urgency["timer_changed"] = urgency["timer_before"] != urgency["timer_after"]
    report["findings"].append(urgency)

    visit("/checkout", ["#donation", "#confirm-shaming", "#total-price", '[data-ccpa-pattern*="DRIP_PRICING"]'], "dp02-dp03-dp08-checkout-before")
    donation = page.locator("#donation")
    total_before = page.locator("#total-price").inner_text()
    checkout_shot = repo_path(SCREENSHOTS_DIR / "dp02-dp03-dp08-checkout-before.png")
    report["findings"].extend([
        {"pattern_id": "DP02", "pattern_name": "Basket Sneaking", "status": "VERIFIED", "page_url": "/checkout", "selector": "#donation", "evidence_text": page.locator("label[for=donation]").inner_text(), "element_state": {"checked": donation.is_checked(), "visible": donation.is_visible()}, "total_before": total_before, "screenshot": checkout_shot, "customer_harm": "Raises the payable amount without an explicit affirmative choice.", "ethical_fix": "Start optional add-ons unchecked and explain them plainly."},
        {"pattern_id": "DP03", "pattern_name": "Confirm Shaming", "status": "VERIFIED", "page_url": "/checkout", "selector": "#confirm-shaming", "evidence_text": page.locator("#confirm-shaming").inner_text(), "element_state": {"visible": page.locator("#confirm-shaming").is_visible(), "enabled": page.locator("#confirm-shaming").is_enabled()}, "screenshot": checkout_shot, "customer_harm": "Uses guilt to steer a consumer into an optional transaction.", "ethical_fix": "Use neutral choices such as Continue without donation."},
        {"pattern_id": "DP08", "pattern_name": "Drip Pricing", "status": "VERIFIED", "page_url": "/checkout", "selector": '[data-ccpa-pattern="DRIP_PRICING"]', "evidence_text": page.locator(".drip-tag").inner_text(), "fees": {label: page.locator(f".order-line:has-text('{label}') strong").inner_text() for label in ["Delivery", "Platform fee", "Handling fee"]}, "total": total_before, "screenshot": checkout_shot, "customer_harm": "Prevents accurate price comparison until late in the purchase journey.", "ethical_fix": "Show the complete payable estimate beside the product price."},
    ])
    donation.uncheck()
    after_shot = save_page(page, "dp02-basket-sneaking-after-uncheck")
    report["checks"].append({"name": "Basket Sneaking state changes after explicit uncheck", "passed": not donation.is_checked(), "screenshot": after_shot})
    report["checks"].append({"name": "Checkout total changes after removing donation", "passed": page.locator("#total-price").inner_text() != total_before})

    visit("/subscribe", ['[data-ccpa-pattern="SUBSCRIPTION_TRAP"]', 'input[type="checkbox"]', 'button:has-text("START FREE TRIAL")'], "dp05-subscription-trap-start")
    report["findings"].append({"pattern_id": "DP05", "pattern_name": "Subscription Trap", "status": "VERIFIED", "page_url": "/subscribe", "selector": '[data-ccpa-pattern="SUBSCRIPTION_TRAP"]', "evidence_text": page.locator(".fixture-callout").inner_text(), "renewal_checked": page.locator('input[type="checkbox"]').is_checked(), "start_button": page.get_by_role("button", name="START FREE TRIAL").inner_text(), "screenshot": repo_path(SCREENSHOTS_DIR / "dp05-subscription-trap-start.png"), "customer_harm": "Makes it harder to stop recurring charges than to start them.", "ethical_fix": "Offer cancellation with the same visibility and simplicity as sign-up."})
    visit("/cancel", [".cancel-card", ".cancel-step"], "dp05-subscription-trap-cancel")
    report["checks"].append({"name": "Subscription cancellation has multiple visible steps", "passed": page.locator(".cancel-step").count() == 3})

    visit("/interface-interference", ['[data-ccpa-pattern="INTERFACE_INTERFERENCE"]', ".preferred", ".muted-choice"], "dp06-interface-interference")
    report["findings"].append({"pattern_id": "DP06", "pattern_name": "Interface Interference", "status": "VERIFIED", "page_url": "/interface-interference", "selector": '[data-ccpa-pattern="INTERFACE_INTERFERENCE"]', "evidence_text": page.locator(".evidence-note").inner_text(), "preferred_button": page.locator(".preferred .primary-cta").inner_text(), "alternative_button": page.locator(".muted-choice .muted-link").inner_text(), "screenshot": repo_path(SCREENSHOTS_DIR / "dp06-interface-interference.png"), "customer_harm": "Obscures the consumer’s lower-commitment choice through visual hierarchy.", "ethical_fix": "Give both consequential choices equal prominence and clarity."})

    visit("/bait-switch", ['[data-ccpa-pattern="BAIT_AND_SWITCH"]', "#bait-switch-status"], "dp07-bait-and-switch")
    report["findings"].append({"pattern_id": "DP07", "pattern_name": "Bait and Switch", "status": "VERIFIED", "page_url": "/bait-switch", "selector": "#bait-switch-status", "evidence_text": page.locator("#bait-switch-status").inner_text(), "selected_offer": page.locator(".switch-row").first.inner_text(), "screenshot": repo_path(SCREENSHOTS_DIR / "dp07-bait-and-switch.png"), "customer_harm": "Wastes time and redirects purchase intent toward a more expensive item.", "ethical_fix": "Keep the advertised outcome available or disclose changes immediately."})

    visit("/ccpa-lab", [".pattern-card", ".status-verified"], "ccpa-lab-seven-verified")
    lab_verified = page.locator(".status-verified").count()
    report["checks"].append({"name": "CCPA Lab contains seven verified cards", "passed": lab_verified == 7, "observed": lab_verified})
    visit("/diff", [".diff-index-row", ".diff-index-row em.verified", ".diff-score"], "interactive-diff-seven-verified")
    diff_verified = page.locator(".diff-index-row em.verified").count()
    report["checks"].append({"name": "Interactive Diff contains seven verified categories", "passed": diff_verified == 7, "observed": diff_verified})

    dark_context = browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="dark")
    dark_context.add_init_script("window.localStorage.setItem('shadowbait-theme', 'dark')")
    dark_page = dark_context.new_page()
    dark_page.goto(BASE_URL + "/product", wait_until="networkidle")
    dark_screenshot = save_page(dark_page, "dp01-false-urgency-product-dark")
    report["checks"].append({"name": "Dark mode preserves visible False Urgency evidence", "passed": dark_page.locator("html[data-theme=dark]").count() == 1 and dark_page.locator("#scarcity-text").is_visible(), "screenshot": dark_screenshot})
    dark_context.close()
    context.close()
    browser.close()

report["scan"]["finished_at"] = datetime.now(timezone.utc).isoformat()
report["summary"] = {
    "verified_findings": len(report["findings"]),
    "verified_pattern_ids": [finding["pattern_id"] for finding in report["findings"]],
    "pages_scanned": len(report["pages"]),
    "checks_passed": sum(1 for check in report["checks"] if check["passed"]),
    "checks_total": len(report["checks"]),
}

scan_json_path = SCAN_ROOT / "scan.json"
response_json_path = REPORT_DIR / "response.json"
latest_response_path = EVIDENCE_ROOT / "reports" / "response.json"
write_json(scan_json_path, report)
write_json(response_json_path, report)
write_json(latest_response_path, report)

print(json.dumps(report["summary"], indent=2))
print(f"scan_dir={SCAN_ROOT}")
print(f"scan_json={scan_json_path}")
print(f"response_json={response_json_path}")
