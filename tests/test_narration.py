"""Listen (tools/narration.py): every narrated line is traced to the verified profile, planted
errors are caught, the media match their recorded hashes, and the pages and WordPress blocks are
labelled, captioned and script-free."""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import narration as N  # noqa: E402

SITE = ROOT / "site"
HANDOVER = ROOT / "handover"


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags(text):
    p = Tags()
    p.feed(text)
    return p.tags


def listen_section(page):
    m = re.search(r'<section class="listen".*?</section>', page, re.S)
    return m.group(0) if m else ""


class Scripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts, cls.manifest = N.check()

    def test_all_ten_pass(self):
        self.assertEqual(sorted(d["slug"] for d in self.scripts), sorted(N.slugs()))
        for d in self.scripts:
            self.assertTrue(260 <= N.count(d["guide"]) <= 300, d["slug"])
            self.assertTrue(120 <= N.count(d["short"]) <= 150, d["slug"])

    def _planted(self, slug, mutate):
        d = copy.deepcopy(next(x for x in self.scripts if x["slug"] == slug))
        mutate(d)
        with self.assertRaises(N.CheckError):
            N.check_script(d)

    def _line(self, d, pred, part="guide"):
        return next(l for l in d[part] if pred(l))

    def test_wrong_year(self):
        self._planted("einstein", lambda d: self._line(d, lambda l: "1905" in l["line"]).update(
            line=self._line(d, lambda l: "1905" in l["line"])["line"].replace("1905", "1904")))

    def test_new_name(self):
        def m(d):
            l = self._line(d, lambda l: l["kind"] == "fact")
            l["line"] = l["line"].rstrip(".") + ", with Thomas Edison."
        self._planted("lamarr", m)

    def test_new_claim_word(self):
        def m(d):
            l = self._line(d, lambda l: l["line"].startswith("Hollywood made him a star"))
            l["line"] = "Hollywood made him the greatest star."
        self._planted("hope", m)

    def test_altered_quote(self):
        def m(d):
            l = self._line(d, lambda l: l["kind"] == "quote")
            l["line"] = l["line"].replace("liberty", "freedom")
        self._planted("einstein", m)

    def test_quote_without_intro(self):
        def m(d):
            i = next(i for i, l in enumerate(d["guide"]) if l["kind"] == "quote")
            del d["guide"][i - 1]
        self._planted("muir", m)

    def test_first_person(self):
        def m(d):
            l = self._line(d, lambda l: l["kind"] == "fact")
            l["line"] = "I " + l["line"][0].lower() + l["line"][1:]
        self._planted("berlin", m)

    def test_transition_with_a_date(self):
        self._planted("cruz", lambda d: d["short"][-1].update(line="Read the full story of 1961, with every source, on this page."))

    def test_question_naming_someone(self):
        self._planted("pei", lambda d: d["guide"][-1].update(line="What would Louis Kahn have built in a new home?"))

    def test_wrong_copy_md_line(self):
        def m(d):
            l = self._line(d, lambda l: l["kind"] == "fact")
            l["copy_md_line"] = 3
        self._planted("naismith", m)

    def test_mentions_ai(self):
        self._planted("strauss", lambda d: d["short"].insert(0, {"line": "This story was generated.", "kind": "transition",
                                                                    "copy_md_line": 0, "copy_md_sentence": ""}))

    def test_word_count(self):
        self._planted("albright", lambda d: d["short"].pop(0) and d["short"].pop(0) and d["short"].pop(0))

    def test_guide_must_end_with_question(self):
        self._planted("hope", lambda d: d["guide"].pop())

    def test_initials_are_not_first_person(self):
        pei = next(x for x in self.scripts if x["slug"] == "pei")
        self.assertTrue(any("I. M. Pei" in l["line"] for l in pei["short"]))


class Media(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts, cls.manifest = N.check()

    def test_manifest_covers_every_script(self):
        self.assertIsNotNone(self.manifest, "run tools/narration_audio.py")
        for d in self.scripts:
            for part in N.RANGES:
                m = self.manifest["files"][f"{d['slug']}-{part}"]
                self.assertEqual(m["script_sha256"], N.script_sha(d[part]))
                self.assertEqual(len(m["lines"]), len(d[part]))
                lo, hi = (100, 140) if part == "guide" else (40, 70)
                self.assertTrue(lo <= m["duration_s"] <= hi, f"{d['slug']}-{part}: {m['duration_s']} s")
            self.assertLessEqual(self.manifest["files"][f"{d['slug']}-short"]["video"]["bytes"], 4_000_000)

    def test_stale_script_is_caught(self):
        scripts = copy.deepcopy(self.scripts)
        scripts[0]["short"][0]["line"] += " "
        with self.assertRaises(N.CheckError):
            N.check_media(scripts, self.manifest)

    def test_tampered_audio_is_caught(self):
        manifest = copy.deepcopy(self.manifest)
        key = next(iter(manifest["files"]))
        manifest["files"][key]["audio"]["sha256"] = "0" * 64
        with self.assertRaises(N.CheckError):
            N.check_media(self.scripts, manifest)

    def test_video_images_are_cleared_for_reuse(self):
        for d in self.scripts:
            for img in self.manifest["files"][f"{d['slug']}-short"]["video"]["images"]:
                self.assertTrue(img["credit"], img)
                self.assertNotIn("quarter-reverse", img["file"])  # rights still to confirm
                self.assertNotIn("highsmith", img["file"])        # rights still to confirm

    def test_captions_match_the_lines(self):
        for d in self.scripts:
            for part in N.RANGES:
                text = (SITE / "media" / d["slug"] / "listen" / f"{d['slug']}-{part}.vtt").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("WEBVTT\n"))
                n = len(re.findall(r"-->", text))
                self.assertEqual(n, len(N.cues(d[part], self.manifest["files"][f"{d['slug']}-{part}"]["lines"])))
                self.assertGreaterEqual(n, len(d[part]))

    def test_voice_is_recorded_with_its_licence(self):
        v = N.voice_meta()
        self.assertEqual(v["dataset"]["license_span"], "License: CC BY 4.0")
        self.assertRegex(v["model"]["sha256"], r"^[0-9a-f]{64}$")


class Rendered(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts, cls.manifest = N.check()

    def test_every_profile_has_one_labelled_listen_section(self):
        for d in self.scripts:
            page = (SITE / f"{d['slug']}.html").read_text(encoding="utf-8")
            self.assertEqual(page.count('class="listen"'), 1, d["slug"])
            sec = listen_section(page)
            self.assertIn(N.E(N.label(d["name"])), sec)
            t = tags(sec)
            audio = [a for tag, a in t if tag == "audio"]
            video = [a for tag, a in t if tag == "video"]
            tracks = [a for tag, a in t if tag == "track"]
            self.assertEqual((len(audio), len(video), len(tracks)), (2, 1, 3))
            for a in audio + video:
                self.assertNotIn("autoplay", a)
                self.assertEqual(a.get("preload"), "none")
            for tr in tracks:
                self.assertEqual(tr.get("kind"), "captions")
                self.assertTrue((SITE / tr["src"]).is_file(), tr["src"])
            for tag, a in t:
                if tag == "source":
                    self.assertTrue((SITE / a["src"]).is_file(), a["src"])
                    self.assertTrue(a["src"].startswith(f"media/{d['slug']}/listen/"))

    def test_transcript_carries_every_line(self):
        for d in self.scripts:
            sec = listen_section((SITE / f"{d['slug']}.html").read_text(encoding="utf-8"))
            for part in N.RANGES:
                for l in d[part]:
                    self.assertIn(N.E(l["line"]), sec)

    def test_source_links_point_at_passages(self):
        for d in self.scripts:
            page = (SITE / f"{d['slug']}.html").read_text(encoding="utf-8")
            links = re.findall(r'class="ls-src" href="#([^"]+)"', page)
            self.assertGreater(len(links), 0, d["slug"])
            for i in links:
                self.assertIn(f'id="{i}"', page)

    def test_listen_comes_before_look_closer(self):
        for d in self.scripts:
            page = (SITE / f"{d['slug']}.html").read_text(encoding="utf-8")
            if 'class="look-closer"' in page:
                self.assertLess(page.index('class="listen"'), page.index('class="look-closer"'))

    def test_wordpress_blocks(self):
        for d in self.scripts:
            block = (HANDOVER / d["slug"] / f"listen-{d['slug']}.html").read_text(encoding="utf-8")
            self.assertNotIn("<script", block)
            self.assertIn('class="ihh-listen"', block)
            self.assertIn(N.E(N.label(d["name"])), block)
            for tag, a in tags(block):
                if tag in ("source", "track"):
                    self.assertTrue((HANDOVER / d["slug"] / a["src"]).is_file(), a["src"])

    def test_script_text_never_mentions_ai(self):
        for d in self.scripts:
            for part in N.RANGES:
                self.assertIsNone(N.BANNED.search(N.script_text(d[part])))


if __name__ == "__main__":
    unittest.main()
