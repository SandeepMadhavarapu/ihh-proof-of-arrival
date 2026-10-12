import asyncio
import unittest
from pathlib import Path

from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument, Verdict
from pipeline.verifier import VerifierAgent


class FakeVerifierLLM:
    def __init__(self, rows):
        self.rows = rows
        self.temperatures = []
    def complete_json(self, system, user, *, temperature):
        self.temperatures.append(temperature)
        return {"sentences": self.rows}


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
        self.assertEqual(llm.temperatures, [0.0])

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


if __name__ == "__main__":
    unittest.main()
