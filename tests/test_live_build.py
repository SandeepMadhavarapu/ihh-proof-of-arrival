"""The public demonstration build (tools/build_live.py): labelled, never indexed, notes kept in
the visitor's own browser, and nothing of it leaking into site/ or the WordPress handover."""
import hashlib
import importlib
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(folder: Path) -> dict:
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file()}


class LiveBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "live"
        cls.before = digest(ROOT / "site")
        build_live = importlib.import_module("tools.build_live")
        build_live.build(str(cls.out))
        cls.after = digest(ROOT / "site")
        cls.pages = {p.name: p.read_text(encoding="utf-8") for p in cls.out.glob("*.html")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_site_folder_is_untouched(self):
        self.assertEqual(self.before, self.after)

    def test_every_page_is_labelled_and_not_indexed(self):
        self.assertGreaterEqual(len(self.pages), 22)
        for name, s in self.pages.items():
            self.assertIn('<meta name="robots" content="noindex,nofollow">', s, name)
            self.assertIn("Not the official IHH website", s, name)
            self.assertIn('href="https://immigranthallofhonor.org/"', s, name)
            self.assertEqual(s.count('class="live-banner"'), 1, name)

    def test_notes_use_the_preview_adapter_only(self):
        for name, s in self.pages.items():
            if "assets/margin-notes.js" in s:
                self.assertLess(s.index("assets/preview-adapter.js"), s.index("assets/margin-notes.js"), name)
            self.assertNotIn('data-ihh-notes="wordpress"', s, name)
            self.assertNotIn('data-ihh-notes="demo"', s, name)
        self.assertIn('data-ihh-notes="preview"', self.pages["muir.html"])
        self.assertIn('data-ihh-notes="preview"', self.pages["verify.html"])
        self.assertTrue((self.out / "assets" / "preview-adapter.js").is_file())
        self.assertFalse((self.out / "assets" / "demo-adapter.js").exists())

    def test_preview_adapter_sends_nothing_anywhere(self):
        js = (ROOT / "voices" / "preview_adapter.js").read_text(encoding="utf-8") + \
             (ROOT / "voices" / "curator_preview.js").read_text(encoding="utf-8")
        for call in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "mailto:", ".src ="):
            self.assertNotIn(call, js)

    def test_curator_preview_is_not_in_the_navigation(self):
        self.assertIn("curator-preview.html", self.pages)
        for name, s in self.pages.items():
            nav = re.findall(r"<nav\b.*?</nav>", s, re.S)
            self.assertFalse(any("curator-preview" in n for n in nav), name)

    def test_no_external_runtime_resources(self):
        for name, s in self.pages.items():
            self.assertFalse(re.search(r'<script[^>]+src="(?:https?:)?//', s), name)

    def test_preview_never_reaches_site_or_handover(self):
        for folder in (ROOT / "site", ROOT / "handover"):
            for p in folder.rglob("*"):
                if p.is_file() and p.suffix in {".html", ".js", ".md", ".css"}:
                    t = p.read_text(encoding="utf-8", errors="ignore")
                    self.assertNotIn("preview-adapter", t, p)
                    self.assertNotIn("live-banner", t, p)


if __name__ == "__main__":
    unittest.main()
