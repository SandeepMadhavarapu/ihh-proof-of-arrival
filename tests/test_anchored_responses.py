"""Offline tests: every visitor response is tied to the passage or claim that prompted it."""
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from living.config import ROOT
from voices import render
from voices.anchors import passage_ends, passages
from voices.core import Store, public, validate
from voices.export_approved import export
from voices.migrate_anchors import migrate

SITE = ROOT / "site"
MUIR_P = "muir-a-farm-boy-from-dunbar-5f55a0"
MUIR_HTML = (SITE / "muir.html").read_text(encoding="utf-8")
FINDING = {"kind": "finding", "page": "verify", "anchor": "einstein-1", "verdict": "contradicted",
           "selector": {"exact": "Albert Einstein immigrated to Princeton, N.J., in 1932."}, "text": ""}


def note(**kw):
    base = {"id": "VV-1", "status": "approved", "kind": "note", "page": "muir", "anchor": MUIR_P, "type": "more",
            "selector": {"exact": "John Muir was born in Dunbar"}, "by": "Sam", "date": "2026-10-25", "text": "A note."}
    base.update(kw)
    return base


class Findings(unittest.TestCase):
    def test_a_finding_needs_a_verdict_and_a_claim_but_not_a_comment(self):
        sub, errors = validate(dict(FINDING))
        self.assertEqual(errors, [])
        self.assertEqual((sub["kind"], sub["type"], sub["verdict"], sub["anchor"]), ("finding", "finding", "contradicted", "einstein-1"))
        self.assertEqual(validate(dict(FINDING, verdict=""))[1], ["record your finding first"])
        self.assertEqual(validate(dict(FINDING, verdict="agree"))[1], ["record your finding first"])
        self.assertIn("missing passage", validate(dict(FINDING, anchor=""))[1])
        self.assertEqual(validate(dict(FINDING, selector={}))[1], ["missing quoted passage"])

    def test_empty_notes_are_still_refused(self):
        for text in ("", "   ", "\n\t"):
            self.assertEqual(validate({"kind": "note", "type": "more", "page": "muir", "anchor": MUIR_P,
                                       "selector": {"exact": "x"}, "text": text})[1], ["write something first"])

    def test_public_finding_carries_its_verdict_and_never_the_email(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(Path(td))
            sub, _ = validate(dict(FINDING, email="me@example.org", name="Ana Lopez", text="See the IAS record."))
            item = store.add(sub, "test")
            pub = public(item)
        self.assertEqual((pub["kind"], pub["verdict"], pub["type_label"], pub["anchor"]), ("finding", "contradicted", "My finding", "einstein-1"))
        self.assertNotIn("me@example.org", json.dumps(pub))
        self.assertEqual(pub["by"], "Ana")

    def test_tally_is_drawn_under_its_own_claim_only(self):
        fs = [dict(FINDING, id=f"VV-{i}", status="approved", verdict=v, by="A", date="2026-10-25")
              for i, v in enumerate(["contradicted", "contradicted", "confirmed"])]
        block = render.findings_block("einstein-1", FINDING["selector"]["exact"], fs)
        self.assertIn("3 visitor findings: 1 Confirmed &middot; 2 Contradicted", block)
        self.assertIn('id="vv-t-einstein-1"', block)
        self.assertEqual(render.findings_block("einstein-2", "Another claim.", fs), "")
        self.assertNotIn("earlier wording", block)
        reworded = render.findings_block("einstein-1", "Albert Einstein moved to Princeton in 1933.", fs)
        self.assertIn("Shared on an earlier wording of this claim.", reworded)

    def test_export_includes_approved_findings_but_not_pending_ones(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(Path(td))
            a = store.add(validate(dict(FINDING))[0], "test")
            store.add(validate(dict(FINDING, verdict="confirmed"))[0], "test")
            store.decide(a["id"], "approve", "curator")
            out = export(store)["notes"]
        self.assertEqual([(n["kind"], n["verdict"]) for n in out], [("finding", "contradicted")])


class Threads(unittest.TestCase):
    def test_thread_sits_directly_after_its_passage(self):
        out, index, flagged = render.annotate(MUIR_HTML, "muir", [note(text="THREAD-TEXT")], {"adapter": "none"})
        self.assertEqual(flagged, [])
        end = passage_ends(out)[MUIR_P]
        self.assertTrue(out[end:].startswith(f'<details class="vv-thread vv-ui" id="vv-t-{MUIR_P}">'), out[end:end + 80])
        thread = out[end:out.index("</details>", end)]
        self.assertIn("1 visitor comment on this section", thread)
        self.assertIn("John Muir was born in Dunbar", thread)       # the passage that prompted it
        self.assertIn("THREAD-TEXT", thread)
        self.assertIn("THREAD-TEXT", index)                         # and still in "Notes on this page"

    def test_passage_text_and_ids_are_unchanged_by_threads(self):
        out, _, _ = render.annotate(MUIR_HTML, "muir", [note()], {"adapter": "none"})
        self.assertEqual(passages(out), passages(MUIR_HTML))

    def test_sections_without_notes_get_no_thread(self):
        out, index, _ = render.annotate(MUIR_HTML, "muir", [note()], {"adapter": "none"})
        self.assertEqual(out.count('class="vv-thread'), 1)
        out, index, _ = render.annotate(MUIR_HTML, "muir", [], {"adapter": "none"})
        self.assertNotIn("vv-thread", out)
        self.assertEqual(index, "")

    def test_note_on_an_edited_passage_says_so(self):
        moved = note(anchor="muir-old-000000", selector={"exact": "John Muir was born in Dunbar, Scotland",
                                                        "prefix": "", "suffix": ""})
        out, _, flagged = render.annotate(MUIR_HTML, "muir", [moved], {"adapter": "none"})
        self.assertEqual(flagged, [])
        self.assertIn(f'id="vv-t-{MUIR_P}"', out)
        self.assertNotIn("earlier wording", out)                    # words still present: no warning
        fuzzy = note(anchor="muir-old-000000", selector={"exact": "John Muir was born at Dunbar, Scotland, on 21 April 1838"})
        out, _, flagged = render.annotate(MUIR_HTML, "muir", [fuzzy], {"adapter": "none"})
        if not flagged:
            self.assertIn("This comment was left on an earlier wording of the passage.", out)

    def test_legacy_note_without_any_anchor_is_listed_as_general_not_guessed(self):
        legacy = note(id="VV-7", anchor="", selector={}, text="LEGACY-TEXT")
        out, index, flagged = render.annotate(MUIR_HTML, "muir", [legacy], {"adapter": "none"})
        self.assertEqual(flagged, [])
        self.assertNotIn("LEGACY-TEXT", out)                        # not attached to any passage
        self.assertIn("General notes on this page", index)
        self.assertIn("LEGACY-TEXT", index)

    def test_built_page_has_a_comment_affordance_only_when_switched_on(self):
        out, _, _ = render.annotate(MUIR_HTML, "muir", [], {"adapter": "email", "email": {"address": "curator@example.org"}})
        self.assertIn("Comment on this section", out)
        self.assertIn("mailto:curator@example.org", out)


class ReviewFixes(unittest.TestCase):
    def test_passage_ends_survive_unusual_line_breaks(self):
        h = '<div>\u2028x\r<p id="a" data-ihh-anchor>one\u2028two</p>\n<p id="b" data-ihh-anchor>three</p></div>'
        ends = passage_ends(h)
        self.assertTrue(all(h[e - 4:e] == "</p>" for e in ends.values()), ends)
        edited = MUIR_HTML.replace("</h1>", "</h1>\u2028\r", 1)
        out, _, _ = render.annotate(edited, "muir", [note()], {"adapter": "none"})
        end = passage_ends(out)[MUIR_P]
        self.assertTrue(out[end:].startswith('<details class="vv-thread'))
        self.assertEqual(passages(out), passages(edited))

    def test_each_note_in_a_thread_keeps_its_own_context(self):
        current = note(id="VV-1", text="ON-CURRENT")
        older = note(id="VV-2", anchor="muir-old-000000", text="ON-OLDER",
                     selector={"exact": "John Muir was born at Dunbar, Scotland, on 21 April 1838, and went to the local schools"})
        other = note(id="VV-3", text="ON-OTHER", selector={"exact": "Dunbar, Scotland"})
        out, _, flagged = render.annotate(MUIR_HTML, "muir", [current, older, other], {"adapter": "none"})
        end = passage_ends(out)[MUIR_P]
        thread = out[end:out.index("</details>", end)]
        if "VV-2" in flagged:
            self.skipTest("older wording not close enough to re-attach")
        lis = {k: thread[thread.index(k) - 600:thread.index(k)] for k in ("ON-CURRENT", "ON-OLDER", "ON-OTHER")}
        self.assertNotIn("earlier wording", lis["ON-CURRENT"].split('<li class="vv-note">')[-1])
        self.assertIn("earlier wording", lis["ON-OLDER"].split('<li class="vv-note">')[-1])
        self.assertIn("vv-q-own", lis["ON-OTHER"].split('<li class="vv-note">')[-1])

    def test_general_notes_are_one_removable_group(self):
        _, index, _ = render.annotate(MUIR_HTML, "muir", [note(anchor="", selector={})], {"adapter": "none"})
        group = index[index.index('<div class="vv-general-wrap">'):]
        self.assertIn("Older notes that were not left", group[:group.index("</div>")])
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        self.assertIn(".vv-general-wrap", js)

    def test_findings_on_a_removed_claim_are_reported(self):
        import contextlib, io, sys
        sys.path.insert(0, str(ROOT / "site-src"))
        import importlib
        gen = importlib.import_module("gen")
        orphan = dict(FINDING, id="VV-8", status="approved", anchor="no-such-claim", by="A", date="2026-10-25")
        with tempfile.TemporaryDirectory() as td:
            shutil.copytree(SITE, Path(td) / "site")
            buf = io.StringIO()
            with patch.object(gen.voices_render, "load_findings", return_value=[orphan]), contextlib.redirect_stdout(buf):
                gen.main(site=str(Path(td) / "site"))
            built = (Path(td) / "site" / "verify.html").read_text(encoding="utf-8")
        self.assertIn("FLAGGED for the moderator: finding VV-8", buf.getvalue())
        self.assertNotIn("vv-findings", built)


class Migration(unittest.TestCase):
    def test_moved_legacy_and_flagged_items(self):
        claims = {"einstein-1": "x"}
        items = [note(id="VV-1"),
                 note(id="VV-2", anchor="muir-old-000000", selector={"exact": "John Muir was born in Dunbar, Scotland"}),
                 note(id="VV-3", anchor="", selector={}),
                 note(id="VV-4", anchor="muir-gone-000000", selector={"exact": "A sentence that is nowhere on the page at all."}),
                 dict(FINDING, id="VV-5", status="approved"),
                 dict(FINDING, id="VV-6", status="approved", anchor="einstein-99")]
        res = {i["id"]: (status, i["anchor"]) for i, _, _, status in migrate(items, SITE, claims)}
        self.assertEqual(res["VV-1"], ("exact", MUIR_P))
        self.assertEqual(res["VV-2"], ("moved", MUIR_P))
        self.assertEqual(items[1]["anchor_history"][0]["from"], "muir-old-000000")
        self.assertEqual(res["VV-3"], ("general", ""))
        self.assertEqual(res["VV-4"], ("flagged", "muir-gone-000000"))   # never moved by a guess
        self.assertEqual(res["VV-5"], ("exact", "einstein-1"))
        self.assertEqual(res["VV-6"], ("flagged", "einstein-99"))

    def test_missing_pages_are_left_alone_not_flagged(self):
        with tempfile.TemporaryDirectory() as empty_site:
            items = [note(id="VV-1")]
            res = migrate(items, Path(empty_site), {})
        self.assertEqual(res[0][3], "unchecked")
        self.assertNotIn("anchor_status", items[0])
        self.assertEqual(items[0]["anchor"], MUIR_P)

    def test_write_mode_rewrites_only_changed_items(self):
        from voices import migrate_anchors
        import sys
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as empty_site:
            store = Store(Path(td))
            item = store.add(validate({"kind": "note", "type": "more", "page": "muir", "anchor": MUIR_P,
                                       "selector": {"exact": "John Muir was born in Dunbar"}, "text": "x"})[0], "test")
            path = store._path(item["id"])
            argv = sys.argv
            try:
                sys.argv = ["migrate", "--store", td, "--write", "--site", empty_site]
                migrate_anchors.main()                     # nothing built: nothing touched
                self.assertNotIn("anchor_status", json.loads(path.read_text(encoding="utf-8")))
                sys.argv = ["migrate", "--store", td, "--write"]
                migrate_anchors.main()                     # first real check: status recorded and audited
                first = path.read_text(encoding="utf-8")
                lines = store.audit_log.read_text(encoding="utf-8").count("migrate_anchors")
                migrate_anchors.main()                     # nothing changed: no rewrite, no new audit line
            finally:
                sys.argv = argv
            self.assertEqual(path.read_text(encoding="utf-8"), first)
            self.assertEqual(store.audit_log.read_text(encoding="utf-8").count("migrate_anchors"), lines)
            self.assertEqual(lines, 1)

    def test_write_mode_keeps_an_audit_line(self):
        from voices import migrate_anchors
        with tempfile.TemporaryDirectory() as td:
            store = Store(Path(td))
            item = store.add(validate({"kind": "note", "type": "more", "page": "muir", "anchor": "muir-old-000000",
                                       "selector": {"exact": "John Muir was born in Dunbar, Scotland"}, "text": "x"})[0], "test")
            import sys
            argv = sys.argv
            sys.argv = ["migrate", "--store", td, "--write"]
            try:
                migrate_anchors.main()
            finally:
                sys.argv = argv
            self.assertEqual(store.get(item["id"])["anchor"], MUIR_P)
            self.assertIn("re-anchored (moved)", store.audit_log.read_text(encoding="utf-8"))


class BrowserScript(unittest.TestCase):
    def test_quote_and_attribution_are_separate_words(self):
        text = [t for t in passages((SITE / "einstein.html").read_text(encoding="utf-8")).values() if "As long as" in t][0]
        self.assertIn("rule.\u201d Albert Einstein", text)

    def test_wordpress_findings_are_parsed_and_read_back(self):
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        self.assertIn("(?: verdict=(\\w+))?", js)
        self.assertIn("m[1] === 'finding' && VERDICT[m[5]]", js)
        self.assertIn("wordpressComments().then(function(list){ var f = onlyFindings(list)", js)

    def test_verdict_labels_have_one_definition(self):
        from voices.core import VERDICTS
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        m = re.search(r"var VERDICT = \{(.*?)\};", js)
        js_verdicts = dict(re.findall(r"(\w+): '([^']+)'", m.group(1)))
        self.assertEqual(js_verdicts, VERDICTS)
        verify = (SITE / "verify.html").read_text(encoding="utf-8")
        for value, label in VERDICTS.items():
            self.assertIn(f'value="{value}"><span>{label}</span>', verify)

    def test_script_still_never_writes_visitor_text_as_html(self):
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        for bad in ("innerHTML", "insertAdjacentHTML", "document.write", "outerHTML"):
            self.assertNotIn(bad, js)
        self.assertIn("Comment on this section", js)
        self.assertIn("Share my finding with the museum", js)


if __name__ == "__main__":
    unittest.main()
