import unittest

import _bootstrap  # noqa: F401
from app.detection.pattern_detector import DETECTORS
from app.detection.rule_engine import get_rules_config
from app.detection.rules_config import RULES_CONFIG

# Exactly as specified in the official plan, section 4.
OFFICIAL = {
    "DP01": ("Basket Sneaking", "DOM", "HIGH"),
    "DP02": ("False Urgency", "NLP + DOM", "MEDIUM"),
    "DP03": ("Confirm Shaming", "NLP", "MEDIUM"),
    "DP04": ("Drip Pricing", "PRICE_FLOW", "HIGH"),
    "DP05": ("Misleading Discount", "PRICE_ANALYSIS", "MEDIUM"),
}


class TestRulesConfig(unittest.TestCase):
    def test_matches_official_plan(self):
        self.assertEqual(set(RULES_CONFIG), set(OFFICIAL))
        for rule_id, (name, method, severity) in OFFICIAL.items():
            cfg = RULES_CONFIG[rule_id]
            self.assertEqual((cfg.name, cfg.method, cfg.severity), (name, method, severity), rule_id)

    def test_every_rule_has_recommendation(self):
        for cfg in RULES_CONFIG.values():
            self.assertTrue(cfg.recommendation)

    def test_m2_only_detects_dp02_and_dp03(self):
        self.assertEqual({r for r, c in RULES_CONFIG.items() if c.m2_detects}, {"DP02", "DP03"})
        self.assertEqual(set(DETECTORS), {"DP02", "DP03"})

    def test_get_rules_config_returns_five_dicts(self):
        rules = get_rules_config()
        self.assertEqual([r["rule_id"] for r in rules], ["DP01", "DP02", "DP03", "DP04", "DP05"])


if __name__ == "__main__":
    unittest.main()
