from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing JSON file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected a JSON object in {path}")
    return value


def resolve_artifact(path_value: str, evidence_root: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def newest_scan(root: Path) -> Path:
    candidates = [path for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")]
    if not candidates:
        fail(f"no scan directories found in {root}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def run_scan(url: str, evidence_root: Path) -> Path:
    env = os.environ.copy()
    env["SHADOWBAIT_URL"] = url
    env["SHADOWBAIT_EVIDENCE_DIR"] = str(evidence_root)
    command = [sys.executable, str(REPO_ROOT / "scripts" / "member1_inspection.py")]
    print("Running:", " ".join(command), f"against {url}")
    completed = subprocess.run(command, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr.rstrip())
        fail(f"scanner exited with code {completed.returncode}")
    for line in completed.stdout.splitlines():
        if line.startswith("scan_dir="):
            return Path(line.split("=", 1)[1].strip())
    return newest_scan(evidence_root / "scans")


def verify(scan_dir: Path, evidence_root: Path, expected_findings: int | None, expected_pages: int | None) -> None:
    scan_dir = scan_dir.resolve()
    scan_json_path = scan_dir / "scan.json"
    response_json_path = evidence_root / "reports" / scan_dir.name / "response.json"
    if not response_json_path.is_file():
        response_json_path = evidence_root / "reports" / "response.json"

    scan = load_json(scan_json_path)
    response = load_json(response_json_path)
    scan_meta = scan.get("scan", {})
    summary = scan.get("summary", {})
    findings = scan.get("findings", [])
    pages = scan.get("pages", [])
    screenshot_dir = scan_dir / "screenshots"
    dom_dir = scan_dir / "dom"

    if not screenshot_dir.is_dir():
        fail(f"missing screenshots directory: {screenshot_dir}")
    screenshots = sorted(path for path in screenshot_dir.glob("*.png") if path.is_file())
    if not screenshots:
        fail(f"no PNG screenshots found in {screenshot_dir}")
    empty_screenshots = [str(path) for path in screenshots if path.stat().st_size == 0]
    if empty_screenshots:
        fail(f"empty screenshot files: {empty_screenshots}")

    if not dom_dir.is_dir():
        fail(f"missing DOM directory: {dom_dir}")
    dom_files = [path for path in dom_dir.iterdir() if path.is_file()]
    if not dom_files:
        fail(f"no DOM files found in {dom_dir}")

    if not isinstance(findings, list) or not findings:
        fail("scan.json contains no findings")
    if not isinstance(pages, list) or not pages:
        fail("scan.json contains no pages")
    if expected_findings is not None and len(findings) != expected_findings:
        fail(f"expected {expected_findings} findings, found {len(findings)}")
    if expected_pages is not None and len(pages) != expected_pages:
        fail(f"expected {expected_pages} pages, found {len(pages)}")

    referenced_screenshots: list[str] = []
    for page in pages:
        screenshot = page.get("screenshot")
        if screenshot:
            referenced_screenshots.append(screenshot)
        dom = page.get("dom", {})
        for key in ("html", "text", "elements"):
            if dom.get(key) and not resolve_artifact(dom[key], evidence_root).is_file():
                fail(f"page references missing DOM artifact: {dom[key]}")
    for finding in findings:
        screenshot = finding.get("screenshot")
        if screenshot:
            referenced_screenshots.append(screenshot)
    missing_references = [path for path in referenced_screenshots if not resolve_artifact(path, evidence_root).is_file()]
    if missing_references:
        fail(f"JSON references missing screenshots: {missing_references}")

    response_summary = response.get("summary")
    if response_summary != summary:
        fail("response.json summary does not match scan.json summary")
    if summary.get("verified_findings") != len(findings):
        fail("summary verified_findings does not match findings length")
    if summary.get("pages_scanned") != len(pages):
        fail("summary pages_scanned does not match pages length")

    print("PASS: scan output is complete")
    print(f"  scan_id: {scan_meta.get('scan_id', scan_dir.name)}")
    print(f"  screenshots: {len(screenshots)} non-empty PNG files")
    print(f"  DOM files: {len(dom_files)}")
    print(f"  findings: {len(findings)}")
    print(f"  pages: {len(pages)}")
    print(f"  scan.json: {scan_json_path}")
    print(f"  response.json: {response_json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify ShadowBait scan artifacts.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_ROOT, help="Evidence root; defaults to ./evidence")
    parser.add_argument("--scan-dir", type=Path, help="Specific scan directory to verify")
    parser.add_argument("--run-scan", action="store_true", help="Run a fresh scan before verifying outputs")
    parser.add_argument("--url", default=os.environ.get("SHADOWBAIT_URL", "http://127.0.0.1:3000"), help="Demo-site URL used with --run-scan")
    parser.add_argument("--expected-findings", type=int, default=7)
    parser.add_argument("--expected-pages", type=int, default=9)
    args = parser.parse_args()

    evidence_root = args.evidence_dir.resolve()
    if args.run_scan:
        scan_dir = run_scan(args.url, evidence_root)
    elif args.scan_dir:
        scan_dir = args.scan_dir.resolve()
    else:
        scan_dir = newest_scan(evidence_root / "scans")
    verify(scan_dir, evidence_root, args.expected_findings, args.expected_pages)


if __name__ == "__main__":
    main()
