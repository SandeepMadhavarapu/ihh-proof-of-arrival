"""Offline tests for Visitor Voices: Margin Notes, Verify reports, moderation and the demo."""
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from living.config import ROOT
from living.proposals import Store as LivingStore, verify_chain
from voices import bridge, render
from voices.anchors import passages, reattach, selector
from voices.core import CONFIRMATION, UNDER_13, RateLimit, Store, display_name, public, validate

SITE = ROOT / "site"
MUIR_P = "muir-a-farm-boy-from-dunbar-5f55a0"
GOOD = {"kind": "note", "type": "perspective", "page": "muir", "anchor": MUIR_P,
        "selector": {"exact": "John Muir was born in Dunbar"}, "text": "We visited Dunbar."}


def build_copy(td: Path, notes=None, voices=None) -> Path:
    """A throwaway copy of what build_site_pages needs, built with the given notes/adapter."""
    from tools import build_site_pages
    shutil.copytree(SITE, td / "site")
    shutil.copytree(ROOT / "site-data", td / "site-data")
    for d in (ROOT / "inductees").iterdir():
        if (d / "copy.html").exists():
            (td / "inductees" / d.name).mkdir(parents=True)
            shutil.copy2(d / "copy.html", td / "inductees" / d.name / "copy.html")
            shutil.copytree(d / "media" / "web", td / "inductees" / d.name / "media" / "web")
    if notes is not None:
        (td / "site-data" / "approved-notes.json").write_text(json.dumps({"notes": notes}), encoding="utf-8")
    build_site_pages.main(str(td), voices=voices)
    return td / "site"


class Anchors(unittest.TestCase):
    def test_ids_are_stable_across_rebuilds(self):
        from tools import build_profile
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "muir"
            shutil.copytree(ROOT / "inductees" / "muir", folder, ignore=shutil.ignore_patterns("sources"))
            build_profile.build(str(folder))
            first = re.findall(r'id="([^"]+)" data-ihh-anchor', (folder / "copy.html").read_text(encoding="utf-8"))
            build_profile.build(str(folder))
            second = re.findall(r'id="([^"]+)" data-ihh-anchor', (folder / "copy.html").read_text(encoding="utf-8"))
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(set(first)), "anchor ids must be unique")
        self.assertIn(MUIR_P, first)
        self.assertTrue(all(i.startswith("muir-") for i in first))

    def test_every_published_profile_has_anchored_passages(self):
        for page in json.loads((ROOT / "site-data" / "published.json").read_text(encoding="utf-8"))["published"]:
            ids = passages((SITE / f"{page}.html").read_text(encoding="utf-8"))
            self.assertGreater(len(ids), 10, page)

    def test_small_edit_reattaches_large_edit_flags(self):
        old = "John Muir was born in Dunbar, Scotland, on 21 April 1838, and attended the local schools until he was eleven."
        sel = selector(old, 0, len(old))
        small = {"muir-x-111111": old.replace("local schools", "local school"), "muir-x-222222": "Something else entirely."}
        self.assertEqual(reattach("muir-x-000000", sel, small), ("muir-x-111111", "fuzzy"))
        large = {"muir-x-333333": "Muir grew up on the Scottish coast before his family left for America.",
                 "muir-x-222222": "Something else entirely."}
        self.assertEqual(reattach("muir-x-000000", sel, large), (None, "flagged"))

    def test_unchanged_and_moved_passages(self):
        text = "In 1849 his family emigrated to the United States."
        sel = selector(text, 8, 18)
        self.assertEqual(reattach("a-1", sel, {"a-1": text}), ("a-1", "exact"))
        self.assertEqual(reattach("a-1", sel, {"a-2": "Intro. " + text}), ("a-2", "moved"))

    def test_ambiguous_match_is_flagged_not_guessed(self):
        sel = {"exact": "the family farm", "prefix": "", "suffix": ""}
        pages = {"a-1": "They left the family farm.", "a-2": "He missed the family farm."}
        self.assertEqual(reattach("gone", sel, pages), (None, "flagged"))

    def test_note_controls_and_badges_are_not_passage_text(self):
        html = ('<p id="p-1" data-ihh-anchor><span class="vv-rail vv-ui"><a class="vv-mark">2</a></span>Text here'
                ' <span class="vbadge">Verified</span></p>')
        self.assertEqual(passages(html), {"p-1": "Text here"})


class Submissions(unittest.TestCase):
    def test_valid_note(self):
        sub, errors = validate(dict(GOOD, email="kid@example.org", name="Priya Example"))
        self.assertEqual(errors, [])
        self.assertEqual(public(dict(sub, id="VV-0001", created_at="2026-10-24T00:00:00+00:00"))["by"], "Priya")

    def test_honeypot(self):
        self.assertEqual(validate(dict(GOOD, website="http://spam.example")), (None, ["spam"]))

    def test_limits_and_required_fields(self):
        self.assertIn("keep it under 1000 characters", validate(dict(GOOD, text="x" * 1001))[1])
        self.assertIn("write something first", validate(dict(GOOD, text="   "))[1])
        self.assertIn("choose what kind of note this is", validate(dict(GOOD, type="html"))[1])
        self.assertTrue(validate(dict(GOOD, page="../etc"))[1])

    def test_rate_limit(self):
        t = [0.0]
        rl = RateLimit(n=3, window=600, clock=lambda: t[0])
        self.assertEqual([rl.allow("a") for _ in range(4)], [True, True, True, False])
        self.assertTrue(rl.allow("b"), "limits are per client")
        t[0] = 601
        self.assertTrue(rl.allow("a"), "the window slides")

    def test_public_view_never_carries_email_or_source(self):
        sub, _ = validate(dict(GOOD, type="more", source="https://example.org/x", email="a@b.org",
                               text="Write to me at a@b.org"))
        pub = public(dict(sub, id="VV-0001", created_at="2026-10-24T00:00:00+00:00"))
        self.assertNotIn("a@b.org", json.dumps(pub))
        self.assertNotIn("example.org", json.dumps(pub))
        self.assertEqual(display_name("someone@example.org"), "A visitor")
        self.assertEqual(display_name(""), "A visitor")

    def test_wording(self):
        self.assertEqual(CONFIRMATION, "Thanks — a curator reviews every note before it appears.")
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        self.assertIn(CONFIRMATION, js)
        self.assertIn("If you are under 13", UNDER_13)
        self.assertIn("If you are under 13", js)


class Rendering(unittest.TestCase):
    def test_injection_is_escaped_and_nothing_is_a_link(self):
        frag = (SITE / "muir.html").read_text(encoding="utf-8")
        note = {"id": "VV-1", "status": "approved", "page": "muir", "anchor": MUIR_P, "type": "more",
                "selector": {"exact": "John Muir was born in Dunbar"}, "by": "<b>x</b>", "date": "2026-10-24",
                "text": '<script>alert(1)</script> <img src=x onerror=alert(2)> see https://evil.example or mail me@x.org'}
        out, index, flagged = render.annotate(frag, "muir", [note], {"adapter": "none"})
        self.assertEqual(flagged, [])
        self.assertNotIn("<script>alert(1)", index)
        self.assertNotIn("<img src=x", index)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", index)
        self.assertNotIn('href="https://evil', index)
        self.assertNotIn("me@x.org", index)
        self.assertIn('href="#vv-' + MUIR_P, out)

    def test_script_never_writes_visitor_text_as_html(self):
        js = (SITE / "assets" / "margin-notes.js").read_text(encoding="utf-8")
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("insertAdjacentHTML", js)
        self.assertNotIn("document.write", js)

    def test_unapproved_notes_never_appear_in_the_built_site(self):
        base = {"page": "muir", "anchor": MUIR_P, "type": "perspective", "kind": "note",
                "selector": {"exact": "John Muir was born in Dunbar"}, "by": "Sam", "date": "2026-10-24"}
        notes = [dict(base, id="VV-1", status="approved", text="APPROVED-NOTE-TEXT"),
                 dict(base, id="VV-2", status="pending", text="PENDING-NOTE-TEXT"),
                 dict(base, id="VV-3", status="rejected", text="REJECTED-NOTE-TEXT"),
                 dict(base, id="VV-4", text="NO-STATUS-NOTE-TEXT")]
        with tempfile.TemporaryDirectory() as td:
            site = build_copy(Path(td), notes)
            built = "".join(p.read_text(encoding="utf-8") for p in site.glob("*.html"))
            muir = (site / "muir.html").read_text(encoding="utf-8")
        self.assertIn("APPROVED-NOTE-TEXT", muir)
        for word in ("PENDING-NOTE-TEXT", "REJECTED-NOTE-TEXT", "NO-STATUS-NOTE-TEXT"):
            self.assertNotIn(word, built)
        self.assertIn('class="vv-index"', muir)

    def test_flagged_note_is_left_out(self):
        note = {"id": "VV-9", "status": "approved", "page": "muir", "anchor": "muir-gone-000000", "type": "question",
                "selector": {"exact": "A sentence that was deleted from the page long ago entirely."}, "text": "FLAGGED-TEXT"}
        _, index, flagged = render.annotate((SITE / "muir.html").read_text(encoding="utf-8"), "muir", [note], {"adapter": "none"})
        self.assertEqual(flagged, ["VV-9"])
        self.assertNotIn("FLAGGED-TEXT", index)


class Production(unittest.TestCase):
    def test_demo_adapter_is_never_in_the_production_build(self):
        for page in SITE.rglob("*"):
            if page.suffix in (".html", ".js", ".css", ".xml", ".txt"):
                text = page.read_text(encoding="utf-8")
                for word in ('data-ihh-notes="demo"', "/voices/", "vv-demo-banner", "demo-adapter", "IHHVoicesAdapters.demo",
                             "_shot.html"):
                    self.assertNotIn(word, text, f"{page.name} carries {word}")
        self.assertFalse((SITE / "assets" / "demo-adapter.js").exists())
        self.assertFalse((SITE / "_shot.html").exists())

    def test_production_config_refuses_demo(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "site-data").mkdir()
            (Path(td) / "site-data" / "visitor-voices.json").write_text('{"adapter": "demo"}', encoding="utf-8")
            with self.assertRaises(SystemExit):
                render.load_config(td)

    def test_switched_off_pages_carry_no_controls(self):
        cfg = render.load_config(str(ROOT))
        if cfg["adapter"] != "none":
            self.skipTest("notes are switched on in site-data/visitor-voices.json")
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("vv-nojs", text, page.name)
            self.assertNotIn("margin-notes.js", text, page.name)

    def test_verify_page_stays_public_and_in_the_nav(self):
        for page in SITE.glob("*.html"):
            if page.name != "404.html":
                self.assertIn('href="verify.html"', page.read_text(encoding="utf-8"), page.name)
        self.assertIn("verify.html", (SITE / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertIn("updateCiteNote", (SITE / "assets" / "site.js").read_text(encoding="utf-8"))
        self.assertIn(".cite-note", (SITE / "assets" / "site.css").read_text(encoding="utf-8"))


class Demo(unittest.TestCase):
    def setUp(self):
        from voices import demo_server
        self.ds = demo_server
        self.td = tempfile.TemporaryDirectory()
        td = Path(self.td.name)
        site = build_copy(td, voices={"adapter": "demo"})
        demo_server._load_gen().main(site=str(site), voices={"adapter": "demo"})
        self.patches = [patch.object(demo_server, "SITE", site),
                        patch.object(demo_server, "store", lambda: Store(td / "moderation")),
                        patch.object(demo_server, "living", lambda: LivingStore(td / "living")),
                        patch.object(demo_server, "LIMIT", RateLimit(n=5))]
        for p in self.patches:
            p.start()
        self.site, self.root = site, td

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.td.cleanup()

    def test_nojs_link_opens_a_prefilled_form(self):
        muir = (self.site / "muir.html").read_text(encoding="utf-8")
        href = f'/voices/form?page=muir&amp;passage={MUIR_P}'
        self.assertIn(f'href="{href}"', muir)
        form = self.ds.nojs_form({"page": ["muir"], "passage": [MUIR_P]})
        self.assertIn(f'name="anchor" value="{MUIR_P}"', form)
        self.assertIn("John Muir was born in Dunbar", form)
        self.assertIn('method="post" action="/voices/form"', form)
        self.assertIn("If you are under 13", form)
        verify = (self.site / "verify.html").read_text(encoding="utf-8")
        self.assertIn('href="/voices/form?page=verify&amp;passage=m1"', verify)
        self.assertIn('id="vv-tell-form" method="post" action="/voices/form"', verify)

    def test_submit_moderate_display_and_audit(self):
        code, msg = self.ds.receive(dict(GOOD), "127.0.0.1")
        self.assertEqual((code, msg), (200, CONFIRMATION))
        self.assertEqual(self.ds.approved_notes("muir"), [], "pending notes are not shown")
        item = self.ds.store().all()[0]
        self.ds.store().decide(item["id"], "approve", "Tester")
        shown = self.ds.approved_notes("muir")
        self.assertEqual([n["anchor"] for n in shown], [MUIR_P])
        self.assertNotIn("email", shown[0])
        ok, why = verify_chain(self.ds.store().audit_log)
        self.assertTrue(ok, why)
        log = self.ds.store().audit_log
        lines = log.read_text(encoding="utf-8").splitlines()
        log.write_text("\n".join([lines[0].replace("visitor", "someone")] + lines[1:]) + "\n", encoding="utf-8")
        self.assertFalse(verify_chain(log)[0], "an edited audit line breaks the chain")

    def test_spam_and_flooding_store_nothing(self):
        self.assertEqual(self.ds.receive(dict(GOOD, website="x"), "1.1.1.1"), (200, CONFIRMATION))
        self.assertEqual(self.ds.store().all(), [])
        codes = [self.ds.receive(dict(GOOD), "2.2.2.2")[0] for _ in range(6)]
        self.assertEqual(codes, [200] * 5 + [429])

    def test_claim_with_source_becomes_a_living_museum_tip_not_copy(self):
        copy_before = {p: p.read_bytes() for p in (ROOT / "inductees").glob("*/copy.md")}
        report = {"kind": "claim", "type": "wrong", "page": "verify", "anchor": "m1",
                  "text": "VISITOR-WORDS It became a park in 1919.", "source": "https://www.nps.gov/articles/lee-story-proclamation.htm"}
        self.assertEqual(self.ds.receive(report, "127.0.0.1")[0], 200)
        tips = LivingStore(self.root / "living").all()
        self.assertEqual(len(tips), 1)
        tip = tips[0]
        self.assertEqual((tip.kind, tip.slug, tip.sentence, tip.claim), ("tip", "muir", "", ""))
        self.assertEqual([(e.url, e.span) for e in tip.evidence], [(report["source"], "")])
        self.assertIn("VISITOR-WORDS", tip.finder["visitor_text"])
        self.assertEqual(self.ds.store().all()[0]["living_proposal"], tip.id)
        # The publisher refuses it, and the verifier never runs on it.
        from living.publisher import PublishError, publish
        with self.assertRaises(PublishError):
            publish(tip.id, LivingStore(self.root / "living"))
        from living import verifier
        with patch.object(verifier, "verify") as v, patch.object(verifier, "make_judge", lambda: None):
            verifier.verify_pending(LivingStore(self.root / "living"), dry_run=True)
        v.assert_not_called()
        self.assertEqual(copy_before, {p: p.read_bytes() for p in (ROOT / "inductees").glob("*/copy.md")})

    def test_note_without_source_or_question_is_not_a_tip(self):
        self.assertFalse(bridge.eligible({"source": "", "type": "wrong", "kind": "note"}))
        self.assertFalse(bridge.eligible({"source": "a book", "type": "question", "kind": "note"}))
        self.assertTrue(bridge.eligible({"source": "a book", "type": "more", "kind": "note"}))


class Contrast(unittest.TestCase):
    @staticmethod
    def ratio(a, b):
        def lum(h):
            c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
            return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        hi, lo = sorted((lum(a), lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    def test_aa_in_light_and_dark(self):
        css = (SITE / "assets" / "margin-notes.css").read_text(encoding="utf-8")
        light = dict(re.findall(r"--vv-(\w+):(#[0-9a-f]{6})", css.split("@media")[0]))
        dark = dict(light, **dict(re.findall(r"--vv-(\w+):(#[0-9a-f]{6})", css.split("@media (prefers-color-scheme:dark)")[1].split("}}")[0])))
        for name, t in (("light", light), ("dark", dark)):
            for fg, bg, need in (("ink", "p", 4.5), ("mut", "p", 4.5), ("acc", "p", 4.5), ("on", "acc", 4.5),
                                 ("ink", "p2", 4.5), ("ink", "kid", 4.5), ("rule", "p", 3.0), ("mut", "p2", 4.5)):
                self.assertGreaterEqual(self.ratio(t[fg], t[bg]), need, f"{name}: {fg} on {bg}")


if __name__ == "__main__":
    unittest.main()
