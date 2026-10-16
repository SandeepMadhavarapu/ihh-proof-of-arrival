import asyncio
import unittest
from pathlib import Path

from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument, Verdict
from pipeline.verifier import VerifierAgent


class ConfirmingLLM:
    def __init__(self, span, provenance="PARAPHRASE"):
        self.span = span
        self.provenance = provenance

    def complete_json(self, *args, **kwargs):
        return {"sentences": [{
            "index": 1, "requires_evidence": True,
            "provenance": self.provenance, "verdict": "CONFIRMED",
            "evidence_source_id": "S001", "evidence_span": self.span,
            "reason": "Deliberately trusting fake verifier; mechanical gate must check this.",
        }]}


class EvidenceQualityTests(unittest.TestCase):
    def audit(self, sentence, span, source=None, provenance="PARAPHRASE"):
        draft = ProfileDraft("Madeleine Albright", "madeleine-albright", [],
                             Path("profiles/madeleine-albright"))
        draft.copy_markdown = sentence
        draft.sources = {"S001": SourceDocument(
            "S001", "https://example.test/fixture", FetchStatus.RETRIEVED,
            text=source if source is not None else span,
        )}
        asyncio.run(VerifierAgent(ConfirmingLLM(span, provenance),
                                  max_remediation_rounds=0).run(draft))
        return draft.verification_report

    def test_trivial_span_fabrication_fails_gate(self):
        report = self.audit(
            "Albright secretly won the Nobel Prize in 1962.", "The",
            "The archive records Madeleine Albright serving as Secretary of State.",
        )
        self.assertFalse(report.gate_passed)
        self.assertEqual(report.claims[0].verdict, Verdict.UNSUPPORTED)
        self.assertIn("24 characters and 4 words", report.claims[0].verifier_reason)

    def test_supported_claim_with_context_passes_gate(self):
        report = self.audit(
            "Madeleine Albright served as Secretary of State.",
            "Madeleine Albright served as Secretary of State from 1997 to 2001.",
        )
        self.assertTrue(report.gate_passed)
        self.assertEqual(report.claims[0].verdict, Verdict.CONFIRMED)

    def test_character_and_word_limits_are_both_required(self):
        for span in ("Albright read books now", "Albright international diplomacy",
                     " " * 30 + "The"):
            with self.subTest(span=span):
                report = self.audit(span.strip(), span)
                self.assertFalse(report.gate_passed)
                self.assertIn("24 characters and 4 words", report.claims[0].verifier_reason)
        span = "Albright wrote books now"  # Synthetic boundary fixture: 24 chars, 4 words.
        self.assertEqual(len(span), 24)
        self.assertTrue(self.audit(span, span).gate_passed)

    def test_unrelated_long_span_and_stopword_overlap_fail(self):
        for sentence, span in (
            ("Albright secretly won the Nobel Prize in 1962.",
             "The archive records Madeleine Albright serving as Secretary of State."),
            ("There were those that gathered.", "There were those that departed."),
            ("Ada won in May.", "Ada won in May while the archive recorded arrivals."),
            ("Albright won the Nobel Prize.", "Albright Albright Albright Albright"),
        ):
            with self.subTest(sentence=sentence, span=span):
                report = self.audit(sentence, span)
                self.assertFalse(report.gate_passed)
                self.assertIn("2 significant tokens", report.claims[0].verifier_reason)

    def test_overlap_is_case_insensitive(self):
        self.assertTrue(self.audit(
            "MADELEINE ALBRIGHT served as secretary.",
            "Madeleine Albright served as Secretary of State.",
        ).gate_passed)

    def test_non_substring_still_fails_even_with_long_matching_tokens(self):
        report = self.audit(
            "Madeleine Albright won the Nobel Prize.",
            "Madeleine Albright won the Nobel Prize.",
            "Madeleine Albright served as Secretary of State.",
        )
        self.assertFalse(report.gate_passed)
        self.assertIn("exact evidence span", report.claims[0].verifier_reason)

    def test_quotation_containment_still_required_after_quality_checks(self):
        span = "Madeleine Albright served as Secretary of State."
        report = self.audit("Madeleine Albright served as President.", span,
                            provenance="QUOTATION")
        self.assertFalse(report.gate_passed)
        self.assertIn("quotation text is not contained", report.claims[0].verifier_reason)
        self.assertTrue(self.audit(span, span, provenance="QUOTATION").gate_passed)


if __name__ == "__main__":
    unittest.main()
