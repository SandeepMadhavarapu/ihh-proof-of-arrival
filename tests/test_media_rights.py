import asyncio
import unittest
from pathlib import Path

from pipeline.media_rights import MediaRightsAgent, validate_alt
from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument


class FakeRightsLLM:
    def __init__(self, rows): self.rows=rows
    def complete_json(self, system, user, *, temperature): return {"rows": self.rows}


BASE = {
    "kind":"photograph","filename":"x.jpg","title":"","creator":"","date_created":"",
    "institution":"","stable_item_url":"https://example.test/item","download_url":"","rights_statement_source":"item page",
    "our_rights_determination":"","our_reasoning":"","required_credit":"","long_description":"","gloss":"","duplicate_or_original":"n/a",
    "date_checked":"","status":"","recommendation":""
}


def draft(text="Rights: Use permitted with credit.", url="https://example.test/item", title=""):
    d=ProfileDraft("Ada Example","ada-example",[],Path("profiles/ada-example"))
    d.sources={"S001":SourceDocument("S001",url,FetchStatus.RETRIEVED,title=title,text=text,retrieved_at="2026-10-12T00:00:00+00:00")}
    return d


class MediaRightsTests(unittest.TestCase):
    def test_unproven_subject_is_mechanically_downgraded_even_if_model_names_person(self):
        d=draft()
        row=dict(BASE, source_id="S001", rights_statement_verbatim="Rights: Use permitted with credit.", alt_text="Ada Example at a ceremony.", long_description_status="SUBJECT CONFIRMED")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertEqual(d.failure_reason, "")
        self.assertEqual(d.media_rows[0]["long_description_status"], "SUBJECT UNCONFIRMED")
        self.assertEqual(d.media_rows[0]["alt_text"], "Archival photograph; subject unconfirmed.")

    def test_exact_subject_span_allows_only_conservative_generated_alt(self):
        d=draft(text="Photograph of Ada Example. Rights: Use permitted with credit.")
        row=dict(BASE, source_id="S001", rights_statement_verbatim="Rights: Use permitted with credit.", subject_evidence_span="Photograph of Ada Example.", alt_text="Ada Example waving from a balcony.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertEqual(d.failure_reason, "")
        self.assertEqual(d.media_rows[0]["long_description_status"], "SUBJECT CONFIRMED BY RETRIEVED ITEM TEXT")
        self.assertEqual(d.media_rows[0]["alt_text"], "Archival photograph of Ada Example.")

    def test_automated_agent_never_issues_affirmative_legal_determination(self):
        d=draft(text="Public domain. Ada Example.")
        row=dict(BASE, source_id="S001", rights_statement_verbatim="Public domain.", our_rights_determination="Usable without restriction", subject_evidence_span="Ada Example")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertEqual(d.failure_reason, "")
        self.assertEqual(d.media_rows[0]["our_rights_determination"], "HUMAN RIGHTS REVIEW REQUIRED")
        self.assertEqual(d.media_rows[0]["recommendation"], "HUMAN RIGHTS REVIEW REQUIRED BEFORE PUBLICATION")

    def test_rights_must_be_exact_source_span(self):
        d=draft()
        row=dict(BASE, source_id="S001", rights_statement_verbatim="Public domain.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertIn("rights wording", d.failure_reason)

    def test_visitor_visible_metadata_must_be_retrieved_not_invented(self):
        d=draft(text="Archive item. Rights: Use permitted with credit.", title="Archive item")
        ok=dict(BASE, source_id="S001", title="Archive item", rights_statement_verbatim="Rights: Use permitted with credit.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([ok])).run(d))
        self.assertEqual(d.failure_reason, "")

        d2=draft(text="Archive item. Rights: Use permitted with credit.", title="Archive item")
        invented=dict(ok, title="Invented exhibition title", creator="Invented Curator", gloss="A dramatic historical turning point.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([invented])).run(d2))
        self.assertIn("visitor-visible title", d2.failure_reason)
        self.assertIn("visitor-visible creator", d2.failure_reason)
        self.assertIn("visitor-visible gloss", d2.failure_reason)

    def test_retrieved_source_cannot_be_silently_omitted(self):
        d=ProfileDraft("Ada Example","ada-example",[],Path("profiles/ada-example"))
        d.sources={
            "S001":SourceDocument("S001","https://example.test/one",FetchStatus.RETRIEVED,text="Rights: Use permitted."),
            "S002":SourceDocument("S002","https://example.test/two",FetchStatus.RETRIEVED,text="Second source text."),
        }
        row=dict(BASE, source_id="S001", stable_item_url="https://example.test/one", rights_statement_verbatim="Rights: Use permitted.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertIn("manifest omitted retrieved source", d.failure_reason)

    def test_invented_or_unsafe_urls_are_rejected(self):
        d=draft(text="Rights: Use permitted with credit.")
        invented=dict(BASE, source_id="S001", stable_item_url="https://invented.example/item", rights_statement_verbatim="Rights: Use permitted with credit.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([invented])).run(d))
        self.assertIn("was not found in retrieved source text", d.failure_reason)

        d2=draft()
        unsafe=dict(BASE, source_id="S001", stable_item_url="javascript:alert(1)", rights_statement_verbatim="Rights: Use permitted with credit.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([unsafe])).run(d2))
        self.assertIn("unsafe stable_item_url", d2.failure_reason)

    def test_media_filename_path_traversal_is_rejected(self):
        d=draft()
        row=dict(BASE, source_id="S001", filename="../x.jpg", rights_statement_verbatim="Rights: Use permitted with credit.")
        asyncio.run(MediaRightsAgent(FakeRightsLLM([row])).run(d))
        self.assertIn("unsafe media filename", d.failure_reason)

    def test_alt_limits(self):
        self.assertTrue(validate_alt("Archival photograph; subject unconfirmed."))
        self.assertFalse(validate_alt("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"))


if __name__ == "__main__": unittest.main()
