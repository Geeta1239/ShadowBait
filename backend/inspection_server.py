from __future__ import annotations

import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.api.scan_orchestrator import ScanStore, validate_scan_request  # noqa: E402
from app.integration.m1_m2_adapter import classify_m1_finding  # noqa: E402


HOST = os.environ.get("INSPECTION_API_HOST", "0.0.0.0")
PORT = int(os.environ.get("INSPECTION_API_PORT", "5050"))
DEFAULT_TARGET = os.environ.get("SHADOWBAIT_TARGET_URL", "http://127.0.0.1:3000").rstrip("/")
EVIDENCE_ROOT = Path(os.environ.get("SHADOWBAIT_EVIDENCE_DIR", str(REPO_ROOT / "evidence"))).resolve()
LIVE_ROOT = EVIDENCE_ROOT / "live-scans"
LIVE_ROOT.mkdir(parents=True, exist_ok=True)
STORE = ScanStore()

FINDINGS = [
    {"id": "DP01", "name": "False Urgency", "route": "/product", "selector": "#scarcity-text", "related": "#offer-timer", "evidence": "“ONLY 2 LEFT!” appears beside a countdown timer.", "why": "Captured to prove scarcity text and a time-pressure signal are visible together.", "harm": "Pressures customers to buy before comparing options or verifying the claim.", "ethical": "Show truthful stock and a fixed, clearly stated offer end time."},
    {"id": "DP02", "name": "Basket Sneaking", "route": "/checkout", "selector": "#donation", "evidence": "Optional ₹50 donation checkbox starts checked.", "why": "Captured before interaction to preserve the original checked state.", "harm": "Adds an optional charge without an explicit affirmative choice.", "ethical": "Start optional add-ons unchecked and explain them plainly."},
    {"id": "DP03", "name": "Confirm Shaming", "route": "/checkout", "selector": "#confirm-shaming", "evidence": "“No, I don’t want to save money.”", "why": "Captured because the decline wording itself is the evidence.", "harm": "Uses guilt to steer customers toward an optional transaction.", "ethical": "Use neutral choices such as Continue without donation."},
    {"id": "DP05", "name": "Subscription Trap", "route": "/subscribe", "selector": '[data-ccpa-pattern="SUBSCRIPTION_TRAP"]', "evidence": "Automatic renewal is selected and cancellation is routed elsewhere.", "why": "Captured to compare the easy signup path with the separate cancellation flow.", "harm": "Makes recurring billing easier to start than to stop.", "ethical": "Offer cancellation with the same visibility and simplicity as sign-up."},
    {"id": "DP06", "name": "Interface Interference", "route": "/interface-interference", "selector": '[data-ccpa-pattern="INTERFACE_INTERFERENCE"]', "evidence": "Recommended plan is prominent while Basic is visually muted.", "why": "Captured to compare the visual hierarchy of the two consequential choices.", "harm": "Obscures the customer’s lower-commitment choice.", "ethical": "Give both consequential choices equal prominence and clarity."},
    {"id": "DP07", "name": "Bait and Switch", "route": "/bait-switch", "selector": "#bait-switch-status", "evidence": "₹799 selection becomes an unavailable ₹1,999 upgrade at the final step.", "why": "Captured to preserve both the selected offer and the changed final outcome.", "harm": "Wastes time and redirects purchase intent toward a more expensive item.", "ethical": "Keep the advertised outcome available or disclose changes immediately."},
    {"id": "DP08", "name": "Drip Pricing", "route": "/checkout", "selector": '[data-ccpa-pattern="DRIP_PRICING"]', "evidence": "Delivery, platform, and handling fees appear in the later checkout summary.", "why": "Captured to show the product price beside the later fee breakdown and total.", "harm": "Delays accurate price comparison until late in the journey.", "ethical": "Show the complete payable estimate beside the product price."},
]
FINDING_BY_ID = {item["id"]: item for item in FINDINGS}


def sse(handler: BaseHTTPRequestHandler, event: str, payload: dict) -> None:
    body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
    handler.wfile.write(body)
    handler.wfile.flush()


def data_url(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip("/"))
    return value.strip("-").lower() or "home"


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def launch_browser(playwright):
    options = {}
    custom_path = os.environ.get("SHADOWBAIT_CHROMIUM_PATH")
    if custom_path:
        options["executable_path"] = custom_path
    return playwright.chromium.launch(**options)


def load_report(scan_id: str) -> dict | None:
    path = LIVE_ROOT / scan_id / "report.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def record_or_disk(scan_id: str):
    record = STORE.get(scan_id)
    if record:
        return record
    report = load_report(scan_id)
    if not report:
        return None
    scan = report.get("scan", {})
    record = STORE.create(scan_id, scan.get("target", ""), [f.get("id") for f in FINDINGS])
    STORE.update(scan_id, status="COMPLETED", started_at=scan.get("started_at"), finished_at=scan.get("finished_at"), report=report)
    return STORE.get(scan_id)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print("[inspection-api] " + fmt % args, flush=True)

    def _headers(self, content_type: str = "application/json") -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_000_000:
            raise ValueError("request body must be a non-empty JSON object")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must contain valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._headers()
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/scans":
            self.send_error(404)
            return
        try:
            payload = self._read_json()
            target, pattern_ids = validate_scan_request(payload, set(FINDING_BY_ID))
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
            return

        scan_id = "live-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        record = STORE.create(scan_id, target, pattern_ids)
        Thread(target=self._run_background_scan, args=(scan_id, target, pattern_ids), daemon=True).start()
        self._json(202, {"scan_id": scan_id, "status": record.status, "target": target, "pattern_ids": pattern_ids, "status_url": f"/api/scans/{scan_id}", "report_url": f"/api/scans/{scan_id}/report"})

    def _run_background_scan(self, scan_id: str, target: str, pattern_ids: list[str]) -> None:
        try:
            self.run_scan(target, scan_id=scan_id, pattern_ids=pattern_ids)
        except Exception as exc:
            STORE.update(scan_id, status="FAILED", error=str(exc), finished_at=datetime.now(timezone.utc).isoformat())
            print(f"[inspection-api] scan {scan_id} failed: {exc}", flush=True)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"ok": True, "target": DEFAULT_TARGET, "evidence_root": repo_path(EVIDENCE_ROOT), "orchestration_api": True})
            return
        if parsed.path == "/api/scans":
            self._json(200, {"scans": [record.summary() for record in STORE.list()]})
            return
        if parsed.path.startswith("/api/scans/"):
            self._get_scan_resource(parsed.path)
            return
        if parsed.path != "/api/inspection/stream":
            self.send_error(404)
            return
        query = parse_qs(parsed.query)
        target = query.get("target", [DEFAULT_TARGET])[0].rstrip("/")
        self.send_response(200)
        self._headers("text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            self.run_scan(target, emit=lambda event, payload: sse(self, event, payload))
            self.close_connection = True
        except Exception as exc:
            try:
                sse(self, "error", {"message": str(exc)})
                self.close_connection = True
            except BrokenPipeError:
                pass

    def _get_scan_resource(self, path: str) -> None:
        parts = path.strip("/").split("/")
        if len(parts) not in {3, 4} or parts[0:2] != ["api", "scans"]:
            self.send_error(404)
            return
        scan_id = parts[2]
        record = record_or_disk(scan_id)
        if record is None:
            self._json(404, {"error": "scan not found", "scan_id": scan_id})
            return
        resource = parts[3] if len(parts) == 4 else None
        if resource is None:
            self._json(200, record.summary())
        elif resource == "report":
            self._json(200, record.report or {})
        elif resource == "findings":
            report = record.report or {}
            self._json(200, {"scan_id": scan_id, "status": record.status, "findings": report.get("findings", [])})
        elif resource == "evidence":
            report = record.report or {}
            self._json(200, {"scan_id": scan_id, "status": record.status, "evidence": [{"pattern_id": item.get("id"), "route": item.get("route"), "selector": item.get("selector"), "screenshot": item.get("screenshot_file"), "dom_html": item.get("dom_html_file"), "dom_text": item.get("dom_text_file")} for item in report.get("findings", [])]})
        else:
            self.send_error(404)

    def run_scan(self, target: str, emit=None, scan_id: str | None = None, pattern_ids: list[str] | None = None) -> dict:
        scan_id = scan_id or "live-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        pattern_ids = pattern_ids or list(FINDING_BY_ID)
        selected_findings = [FINDING_BY_ID[item] for item in pattern_ids]
        out_dir = LIVE_ROOT / scan_id
        screenshots_dir = out_dir / "screenshots"
        dom_dir = out_dir / "dom"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        dom_dir.mkdir(parents=True, exist_ok=True)
        started_at = datetime.now(timezone.utc).isoformat()
        scan_meta = {"scan_id": scan_id, "target": target, "browser": "Chromium", "viewport": {"width": 1440, "height": 1000}, "started_at": started_at, "output_root": repo_path(out_dir), "pattern_ids": pattern_ids}
        if STORE.get(scan_id):
            STORE.update(scan_id, status="RUNNING", started_at=started_at)
        if emit:
            emit("started", {**scan_meta, "total": len(selected_findings), "message": "Chromium browser started with a fresh context."})
        captured = []
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            context = browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
            page = context.new_page()
            for index, finding in enumerate(selected_findings):
                if emit:
                    emit("stage", {"completed": index, "total": len(selected_findings), "pattern_id": finding["id"], "route": finding["route"], "selector": finding["selector"], "message": f"Opening {finding['route']} and reading {finding['selector']}"})
                page.goto(target + finding["route"], wait_until="networkidle")
                locator = page.locator(finding["selector"]).first
                if locator.count() == 0:
                    raise RuntimeError(f"{finding['id']}: selector not found: {finding['selector']}")
                visible = locator.is_visible()
                text = locator.inner_text() if locator.evaluate("el => el.tagName !== 'INPUT'") else ""
                element_state = locator.evaluate("""el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect(); return { tag: el.tagName, visible: !!(r.width && r.height), checked: typeof el.checked === 'boolean' ? el.checked : null, bounding_box: { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) }, computed: { color: s.color, backgroundColor: s.backgroundColor, display: s.display } }; }""")
                if finding["id"] == "DP02":
                    text = page.locator("label[for=donation]").inner_text()
                if finding["id"] == "DP08":
                    text = page.locator(".drip-tag").inner_text()
                route_slug = slug(finding["route"])
                screenshot_path = screenshots_dir / f"{finding['id'].lower()}-{slug(finding['name'])}.png"
                screenshot = page.screenshot(path=str(screenshot_path), full_page=True)
                html_path = dom_dir / f"{route_slug}.html"
                text_path = dom_dir / f"{route_slug}-text.json"
                html_path.write_text(page.content(), encoding="utf-8")
                write_json(text_path, {"route": finding["route"], "url": page.url, "title": page.title(), "visible_text": page.locator("body").inner_text()})
                result = {**finding, "status": "VERIFIED", "visible": visible, "observed_text": text, "element_state": element_state, "screenshot": data_url(screenshot), "screenshot_file": repo_path(screenshot_path), "dom_html_file": repo_path(html_path), "dom_text_file": repo_path(text_path), "captured_at": datetime.now(timezone.utc).isoformat()}
                if finding["id"] == "DP02":
                    page.locator("#donation").uncheck()
                    after_path = screenshots_dir / "dp02-after-uncheck.png"
                    after = page.screenshot(path=str(after_path), full_page=True)
                    result["after_screenshot"] = data_url(after)
                    result["after_screenshot_file"] = repo_path(after_path)
                    result["state_transition"] = "checked=true → checked=false"
                if finding["id"] == "DP05":
                    page.goto(target + "/cancel", wait_until="networkidle")
                    related_path = screenshots_dir / "dp05-cancellation-flow.png"
                    related = page.screenshot(path=str(related_path), full_page=True)
                    result["after_screenshot"] = data_url(related)
                    result["after_screenshot_file"] = repo_path(related_path)
                    result["state_transition"] = "/subscribe → /cancel"
                m2_findings = classify_m1_finding(result)
                result["m2_status"] = "CLASSIFIED" if m2_findings else "NOT_IN_M2_SCOPE"
                result["m2_findings"] = m2_findings
                captured.append(result)
                if emit:
                    emit("finding", {"completed": index + 1, "total": len(selected_findings), "finding": result, "message": f"Captured {finding['id']} screenshot and saved evidence."})
                    emit("classification", {"completed": index + 1, "total": len(selected_findings), "pattern_id": finding["id"], "status": result["m2_status"], "findings": m2_findings, "message": f"M2 classification {result['m2_status'].lower()} for {finding['id']}."})
            context.close()
            browser.close()
        finished_at = datetime.now(timezone.utc).isoformat()
        all_m2 = [item for finding in captured for item in finding.get("m2_findings", [])]
        report = {"scan": {**scan_meta, "finished_at": finished_at}, "findings": captured, "summary": {"verified_findings": len(captured), "pages_scanned": len(set(item["route"] for item in captured)), "m2_classified_findings": len(all_m2), "m2_verified_findings": sum(1 for item in all_m2 if item.get("status") == "VERIFIED"), "m2_detection_sources": {source: sum(1 for item in all_m2 if item.get("detection_source") == source) for source in sorted({item.get("detection_source") for item in all_m2})}}}
        scan_path = out_dir / "scan.json"
        report_path = out_dir / "report.json"
        response_path = out_dir / "response.json"
        for path in (scan_path, report_path, response_path):
            write_json(path, report)
        if STORE.get(scan_id):
            STORE.update(scan_id, status="COMPLETED", finished_at=finished_at, report=report)
        if emit:
            emit("complete", {"scan_id": scan_id, "completed": len(captured), "total": len(selected_findings), "findings": captured, "summary": report["summary"], "scan_file": repo_path(scan_path), "report_file": repo_path(report_path), "response_file": repo_path(response_path), "finished_at": finished_at, "message": "Inspection complete — live evidence and M2 classifications ready and saved."})
        return report


if __name__ == "__main__":
    print(f"Inspection API listening on http://{HOST}:{PORT}; target={DEFAULT_TARGET}; evidence={EVIDENCE_ROOT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
