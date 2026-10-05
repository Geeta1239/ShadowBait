import unittest

import _bootstrap  # noqa: F401
from app.detection.confirm_shaming_detector import detect_confirm_shaming
from app.nlp.preprocessing import segment_text

POSITIVES = [
    "No, I don't want to save money.",
    "No thanks, I prefer paying full price.",
    "I would rather miss out on this amazing deal.",
    "No, I don't want the discount.",
    "I'd rather pay more.",
    "No, I don't want to protect my account.",
    "No, I would rather miss out.",
    "No thanks, I hate saving money.",
    "I don't want this amazing deal.",
    "No, I prefer the expensive option.",
]

NEGATIVES = [
    "No thanks.", "No, cancel my order.", "I don't want to continue.", "No, go back.",
    "Decline.", "Skip this step.", "No", "Maybe later", "Save my card for next time",
    "Get 10% discount on your first order", "I don't want to receive offers by email.",
    "Protect your account with two-factor authentication.", "Now or never",
    "Continue without offer",
]


def run(text):
    return detect_confirm_shaming(segment_text(text))


class TestConfirmShaming(unittest.TestCase):
    def test_positives_detected(self):
        for text in POSITIVES:
            with self.subTest(text=text):
                self.assertEqual(len(run(text)), 1)

    def test_negatives_not_detected(self):
        for text in NEGATIVES:
            with self.subTest(text=text):
                self.assertEqual(run(text), [])

    def test_darkshop_example(self):
        m = run("No, I don't want to save money.")[0]
        self.assertEqual(m.pattern, "CONFIRM_SHAMING")
        self.assertEqual(m.rule_confidence, 0.95)
        self.assertEqual(m.evidence_text, "No, I don't want to save money.")

    def test_curly_apostrophe_and_case(self):
        self.assertEqual(len(run("NO, I DON\u2019T WANT TO SAVE MONEY!!")), 1)

    def test_confidence_in_range(self):
        for text in POSITIVES:
            self.assertTrue(0.0 <= run(text)[0].rule_confidence <= 1.0)


if __name__ == "__main__":
    unittest.main()
