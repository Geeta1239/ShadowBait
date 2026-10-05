import json
import unittest

import _bootstrap  # noqa: F401
from app.detection.evidence_engine import attach_scanner_evidence
from app.detection.rule_engine import analyze_text

DARKSHOP = """
Premium Wireless Headphones

₹4,999
₹799
84% OFF

🔥 ONLY 2 LEFT!
Offer ends in 08:32

BUY NOW

Headphones ₹799
Add ₹50 donation

No, I don't want to save money.

Delivery ₹99
Platform fee ₹49
Handling fee ₹20
TOTAL ₹967
"""

CONTRACT_KEYS = {"rule_id", "name", "severity", "confidence", "status", "evidence", "recommendation"}
EVIDENCE_KEYS = {"text", "selector", "page", "screenshot"}


class TestRuleEngine(unittest.TestCase):
    def test_darkshop_findings(self):
        findings = analyze_text(DARKSHOP, page="product")
        pairs = {(f["rule_id"], f["evidence"]["text"]) for f in findings}
        self.assertIn(("DP02", "🔥 ONLY 2 LEFT!"), pairs)
        self.assertIn(("DP02", "Offer ends in 08:32"), pairs)
        self.assertIn(("DP03", "No, I don't want to save money."), pairs)
        self.assertEqual(len(findings), 3)   # nothing for donation, discount or fees

    def test_contract_shape(self):
        for f in analyze_text(DARKSHOP):
            self.assertTrue(CONTRACT_KEYS.issubset(f))
            self.assertEqual(set(f["evidence"]), EVIDENCE_KEYS)
            self.assertRegex(f["rule_id"], r"^DP0[1-5]$")
            self.assertTrue(f["recommendation"])
            self.assertTrue(f["explanation"])
            self.assertTrue(0.0 <= f["confidence"] <= 1.0)

    def test_severity_is_fixed_from_config(self):
        for f in analyze_text("Only 2 left!\nHurry!\nLimited time offer.\nNo, I don't want to save money."):
            self.assertEqual(f["severity"], "MEDIUM")

    def test_names_and_patterns(self):
        by_id = {f["rule_id"]: f for f in analyze_text(DARKSHOP)}
        self.assertEqual(by_id["DP02"]["name"], "False Urgency")
        self.assertEqual(by_id["DP02"]["pattern"], "FALSE_URGENCY")
        self.assertEqual(by_id["DP03"]["name"], "Confirm Shaming")
        self.assertEqual(by_id["DP03"]["pattern"], "CONFIRM_SHAMING")

    def test_status_is_candidate_and_scanner_fields_empty(self):
        f = analyze_text("Only 2 left!", page="product")[0]
        self.assertEqual(f["status"], "CANDIDATE")
        self.assertEqual(f["evidence"]["page"], "product")
        self.assertIsNone(f["evidence"]["selector"])
        self.assertIsNone(f["evidence"]["screenshot"])

    def test_scanner_evidence_makes_finding_verified(self):
        f = analyze_text("No, I don't want to save money.")[0]
        partial = attach_scanner_evidence(f, selector="#decline")
        self.assertEqual(partial["status"], "CANDIDATE")        # no screenshot yet
        full = attach_scanner_evidence(f, selector="#decline", page="checkout", screenshot="checkout.png")
        self.assertEqual(full["status"], "VERIFIED")
        self.assertEqual(full["evidence"]["selector"], "#decline")
        self.assertEqual(f["status"], "CANDIDATE")              # original not mutated

    def test_json_serialisable(self):
        json.dumps(analyze_text(DARKSHOP), ensure_ascii=False)

    def test_clean_text_has_no_findings(self):
        self.assertEqual(analyze_text("Product is available.\nNo thanks.\nFree delivery available."), [])

    def test_empty_and_none(self):
        self.assertEqual(analyze_text(""), [])
        self.assertEqual(analyze_text(None), [])

    def test_accepts_list_of_snippets(self):
        self.assertEqual(len(analyze_text(["Only 2 left!", "No thanks."])), 1)

    def test_duplicate_evidence_reported_once(self):
        self.assertEqual(len(analyze_text("Only 2 left!\nONLY 2 LEFT!!\nonly 2 left")), 1)


if __name__ == "__main__":
    unittest.main()
