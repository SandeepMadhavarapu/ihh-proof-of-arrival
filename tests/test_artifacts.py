"""Look closer (tools/artifacts.py): every annotation is checked against its quoted evidence, a
planted error is caught, the section works without JavaScript, and the pages and the WordPress
blocks are what the generator writes."""
import copy
import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import artifacts  # noqa: E402

SITE = ROOT / "site"
HANDOVER = ROOT / "handover"


class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.scripts, self.imgs = set(), [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href", "").startswith("#"):
            self.hrefs.append(a["href"][1:])
        if tag == "script":
            self.scripts += 1
        if tag == "img":
            self.imgs.append(a)


def parse(text):
    p = Ids()
    p.feed(text)
    return p


class Checker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arts = artifacts.check()

    def test_research_passes(self):
        self.assertGreaterEqual(len(self.arts), 4)
        for a in self.arts:
            self.assertTrue(4 <= len(a["hotspots"]) <= 7, a["id"])
            self.assertLessEqual(len(a["alt"]), 125, a["id"])
            self.assertTrue(a["rights"]["exact_span"])
            self.assertTrue(Path(artifacts.IMAGES, a["image"]).is_file())

    def _planted(self, mutate):
        arts = copy.deepcopy(self.arts)
        mutate(arts)
        with self.assertRaises(artifacts.CheckError):
            artifacts.check(arts)

    def test_wrong_date_is_caught(self):
        def m(arts):
            ein = next(a for a in arts if a["slug"] == "einstein")
            h = next(h for h in ein["hotspots"] if "1879" in h["text"])
            h["text"] = h["text"].replace("1879", "1878")
        self._planted(m)

    def test_wrong_name_is_caught(self):
        def m(arts):
            arts[0]["hotspots"][0]["text"] += " It was witnessed by Thomas Edison."
        self._planted(m)

    def test_invented_span_is_caught(self):
        def m(arts):
            arts[0]["hotspots"][0]["evidence"][0]["exact_span"] = "a sentence that appears in no source at all"
        self._planted(m)

    def test_missing_rights_is_caught(self):
        def m(arts):
            arts[1]["rights"] = {}
        self._planted(m)

    def test_long_alt_is_caught(self):
        def m(arts):
            arts[2]["alt"] = "x" * 126
        self._planted(m)

    def test_region_outside_image_is_caught(self):
        def m(arts):
            arts[3]["hotspots"][0]["region"]["x"] = 95
            arts[3]["hotspots"][0]["region"]["w"] = 20
        self._planted(m)


class Rendered(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arts = artifacts.load()

    def test_every_marker_links_to_a_note_and_back(self):
        for a in self.arts:
            page = (SITE / f"{a['slug']}.html").read_text(encoding="utf-8")
            self.assertIn(f'id="lc-{a["id"]}"', page)
            p = parse(page)
            for h in a["hotspots"]:
                self.assertIn(f"lc-{a['id']}-{h['n']}", p.ids)
                self.assertIn(f"lc-{a['id']}-m{h['n']}", p.ids)
                self.assertIn(f"lc-{a['id']}-{h['n']}", p.hrefs)
                self.assertIn(f"lc-{a['id']}-m{h['n']}", p.hrefs)
            for target in p.hrefs:
                if target.startswith("lc-"):
                    self.assertIn(target, p.ids, f"{a['slug']}: dangling #{target}")

    def test_notes_are_plain_text_without_javascript(self):
        # every note's words are in the HTML itself, not injected by a script
        for a in self.arts:
            page = (SITE / f"{a['slug']}.html").read_text(encoding="utf-8")
            for h in a["hotspots"]:
                self.assertIn(artifacts.E(h["text"]), page)
            self.assertIn(artifacts.LABEL, page)

    def test_images_present_with_alt(self):
        for a in self.arts:
            self.assertTrue((SITE / "media" / "artifacts" / a["image"]).is_file())
            page = (SITE / f"{a['slug']}.html").read_text(encoding="utf-8")
            imgs = [i for i in parse(page).imgs if i.get("src") == f"media/artifacts/{a['image']}"]
            self.assertEqual(len(imgs), 1)
            self.assertEqual(imgs[0]["alt"], a["alt"])

    def test_only_profiles_with_an_artifact_get_a_section(self):
        with_art = {a["slug"] for a in self.arts}
        for page in SITE.glob("*.html"):
            has = 'class="look-closer"' in page.read_text(encoding="utf-8")
            self.assertEqual(has, page.stem in with_art, page.name)

    def test_index_page_lists_every_artifact(self):
        page = (SITE / "artifacts.html").read_text(encoding="utf-8")
        self.assertIn('<a href="artifacts.html" aria-current="page">Look closer</a>', page)
        for a in self.arts:
            self.assertIn(f'href="{a["slug"]}.html#lc-{a["id"]}"', page)

    def test_every_page_links_to_look_closer(self):
        for page in SITE.glob("*.html"):
            self.assertIn('href="artifacts.html"', page.read_text(encoding="utf-8"), page.name)

    def test_wordpress_blocks_have_no_script(self):
        for a in self.arts:
            block = (HANDOVER / a["slug"] / f"look-closer-{a['id']}.html").read_text(encoding="utf-8")
            p = parse(block)
            self.assertEqual(p.scripts, 0)
            self.assertNotIn("lc-zoom", block)
            self.assertIn('class="ihh-look"', block)
            self.assertTrue((HANDOVER / a["slug"] / "media" / "artifacts" / a["image"]).is_file())
            self.assertEqual(block, artifacts.wp_block(a, f"media/artifacts/{a['image']}"))

    def test_conflict_with_profile_is_recorded_not_hidden(self):
        ein = next(a for a in self.arts if a["slug"] == "einstein")
        self.assertTrue(ein["conflicts"], "the 1935 Bermuda entry vs the 1933 arrival must stay recorded")


if __name__ == "__main__":
    unittest.main()
