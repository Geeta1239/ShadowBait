import json
import sys
from pathlib import Path

# Add backend/ to Python import path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.detection.rule_engine import analyze_text


def process_m1_report(report_path):
    """
    Read M1 scanner output and send textual evidence to M2.
    """

    report_path = Path(report_path)

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    results = []

    for finding in report.get("findings", []):

        pattern_id = finding.get("pattern_id")
        pattern_name = finding.get("pattern_name")
        page = finding.get("page_url", "")
        selector = finding.get("selector")
        evidence_text = finding.get("evidence_text", "")
        screenshot = finding.get("screenshot")

        # M2 is currently responsible for language-based patterns.
        if pattern_id not in ["DP03"]:
            continue

        if not evidence_text:
            continue

        # Send M1 text to M2
        m2_findings = analyze_text(
            evidence_text,
            page=page
        )

        for m2 in m2_findings:

            # Attach M1 evidence to M2 result
            m2["evidence"] = {
                "text": evidence_text,
                "selector": selector,
                "page": page,
                "screenshot": screenshot
            }

            # M1 has provided actual evidence,
            # so this detection can be considered verified.
            m2["status"] = "VERIFIED"

            # Keep the original M1 pattern ID
            m2["rule_id"] = pattern_id

            results.append(m2)

    return results


if __name__ == "__main__":

    report = "evidence/member1-step2/member1-step2-report.json"

    findings = process_m1_report(report)

    print(json.dumps(findings, indent=2))