import asyncio
import unittest
from pathlib import Path

from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument, Verdict
from pipeline.verifier import VerifierAgent, extract_sentences


class FakeVerifierLLM:
    def __init__(self, rows):
        self.rows = rows
        self.temperatures = []
    def complete_json(self, system, user, *, temperature):
        self.temperatures.append(temperature)
        return {"sentences": self.rows}


class RemediationLLM:
    def __init__(self, original, revised):
        self.original = original
        self.revised = revised
        self.calls = 0

    def complete_json(self, system, user, *, temperature):
        self.calls += 1
        self.assert_temp = temperature
        if "corrective editor" in system:
            return {"copy_markdown": self.revised}
        sentences = extract_sentences(self.original if self.calls == 1 else self.revised)
        rows = []
        for i, sentence in enumerate(sentences, 1):
            if sentence == "Ada won the Nobel Prize.":
                rows.append({
                    "index": i, "requires_evidence": True, "provenance": "PARAPHRASE",
                    "verdict": "UNSUPPORTED", "evidence_source_id": "", "evidence_span": "",
                    "reason": "No source support.", "suggested_rewrite": ""
                })
            elif sentence in {"Ada arrived in 1900.", "I arrived in 1900."}:
                rows.append({
                    "index": i, "requires_evidence": True, "provenance": "RECORD",
                    "verdict": "CONFIRMED", "evidence_source_id": "S001", "evidence_span": sentence,
                    "reason": "Exact span.", "suggested_rewrite": ""
                })
            else:
                rows.append({
                    "index": i, "requires_evidence": False, "provenance": "UNRESOLVED",
                    "verdict": "UNSUPPORTED", "evidence_source_id": "", "evidence_span": "",
                    "reason": "Editorial prompt.", "suggested_rewrite": ""
                })
        return {"sentences": rows}


class VerifierGateTests(unittest.TestCase):
    def _draft(self, sentence):
        d = ProfileDraft("Ada Example", "ada-example", [], Path("profiles/ada-example"))
        d.copy_markdown = f"# Ada Example\n\n**Opening line (sits above the photograph):**\n{sentence}\n"
        d.sources = {"S001": SourceDocument("S001", "https://example.test/source", FetchStatus.RETRIEVED, text="Ada arrived in 1900. The archive records the event.")}
        return d

    def test_planted_unsupported_claim_fails_gate(self):
        d = self._draft("Ada won the Nobel Prize.")
        llm = FakeVerifierLLM([{
            "index": 1, "requires_evidence": True, "provenance": "PARAPHRASE",
            "verdict": "UNSUPPORTED", "evidence_source_id": "", "evidence_span": "",
            "reason": "No retrieved source says this.", "suggested_rewrite": ""
        }])
        asyncio.run(VerifierAgent(llm).run(d))
        self.assertFalse(d.verification_report.gate_passed)
        self.assertEqual(d.claims[0].verdict, Verdict.UNSUPPORTED)
        self.assertEqual(llm.temperatures, [0.0, 0.0])

    def test_supported_claim_passes_with_exact_span(self):
        d = self._draft("Ada arrived in 1900.")
        llm = FakeVerifierLLM([{
            "index": 1, "requires_evidence": True, "provenance": "RECORD",
            "verdict": "CONFIRMED", "evidence_source_id": "S001", "evidence_span": "Ada arrived in 1900.",
            "reason": "Exact archive statement.", "suggested_rewrite": ""
        }])
        asyncio.run(VerifierAgent(llm).run(d))
        self.assertTrue(d.verification_report.gate_passed)
        self.assertEqual(d.claims[0].verdict, Verdict.CONFIRMED)

    def test_fake_exact_span_downgrades_confirmed(self):
        d = self._draft("Ada arrived in 1900.")
        llm = FakeVerifierLLM([{
            "index": 1, "requires_evidence": True, "provenance": "RECORD",
            "verdict": "CONFIRMED", "evidence_source_id": "S001", "evidence_span": "Ada arrived in 1899.",
            "reason": "claimed support", "suggested_rewrite": ""
        }])
        asyncio.run(VerifierAgent(llm).run(d))
        self.assertFalse(d.verification_report.gate_passed)
        self.assertEqual(d.claims[0].verdict, Verdict.UNSUPPORTED)
        self.assertIn("exact evidence span", d.claims[0].verifier_reason)

    def test_remediation_rewrites_rejected_claim_then_reaudits(self):
        original = '# Ada Example\n\n**Status:** REQUIRES HUMAN SIGN-OFF\n\n**Opening line (sits above the photograph):**\nAda arrived in 1900.\n\n**Credit (sits immediately beneath the photograph):**\nNo verified anchor photograph is supplied.\n\n**Standfirst:**\nAda arrived in 1900.\n\n---\n\n## One\nAda arrived in 1900.\n\n## Two\nAda won the Nobel Prize.\n\n## Three\nAda arrived in 1900.\n\n## Four\nAda arrived in 1900.\n\n## Five\nAda arrived in 1900.\n\n---\n\n**First-person quotation (one, as reported by Fixture Archive):**\n> I arrived in 1900.\n\n---\n\n## Five discussion questions\n1. What does the source establish?\n2. What remains unknown?\n3. What should a reviewer check?\n4. What evidence would change the account?\n5. What should be documented next?\n## Two activities\n**1. Trace the claim.** Match the claim to the source.\n**2. Mark the boundary.** List what remains unknown.\n'
        revised = '# Ada Example\n\n**Status:** REQUIRES HUMAN SIGN-OFF\n\n**Opening line (sits above the photograph):**\nAda arrived in 1900.\n\n**Credit (sits immediately beneath the photograph):**\nNo verified anchor photograph is supplied.\n\n**Standfirst:**\nAda arrived in 1900.\n\n---\n\n## One\nAda arrived in 1900.\n\n## Two\nAda arrived in 1900.\n\n## Three\nAda arrived in 1900.\n\n## Four\nAda arrived in 1900.\n\n## Five\nAda arrived in 1900.\n\n---\n\n**First-person quotation (one, as reported by Fixture Archive):**\n> I arrived in 1900.\n\n---\n\n## Five discussion questions\n1. What does the source establish?\n2. What remains unknown?\n3. What should a reviewer check?\n4. What evidence would change the account?\n5. What should be documented next?\n## Two activities\n**1. Trace the claim.** Match the claim to the source.\n**2. Mark the boundary.** List what remains unknown.\n'
        d = ProfileDraft("Ada Example", "ada-example", [], Path("profiles/ada-example"))
        d.copy_markdown = original
        d.sources = {"S001": SourceDocument("S001", "https://example.test/source", FetchStatus.RETRIEVED, text="Ada arrived in 1900. I arrived in 1900.")}
        llm = RemediationLLM(original, revised)
        asyncio.run(VerifierAgent(llm, max_remediation_rounds=1).run(d))
        self.assertTrue(d.verification_report.gate_passed)
        self.assertEqual(d.copy_markdown, revised)
        self.assertEqual(len(d.verification_report.removed_or_rewritten), 1)
        self.assertEqual(llm.calls, 3)

    def test_factual_question_cannot_bypass_evidence_by_being_marked_editorial(self):
        d = self._draft("Why did Ada arrive in 1900?")
        llm = FakeVerifierLLM([{
            "index": 1, "requires_evidence": False, "provenance": "UNRESOLVED",
            "verdict": "UNSUPPORTED", "evidence_source_id": "", "evidence_span": "",
            "reason": "incorrectly labelled editorial", "suggested_rewrite": ""
        }])
        asyncio.run(VerifierAgent(llm, max_remediation_rounds=0).run(d))
        self.assertFalse(d.verification_report.gate_passed)
        self.assertEqual(d.claims[0].verdict, Verdict.UNSUPPORTED)


if __name__ == "__main__":
    unittest.main()
