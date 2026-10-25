"""Offline tests: interviews and media from other institutions, and their permission rules."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from living.config import ROOT
from tools import media_sources as ms

SITE = ROOT / "site"
GOOD = {"id": "x-clip", "title": "A clip", "kind": "video", "institution": "A museum",
        "url": "https://museum.example/item/1", "permission": "pending"}


def write(td, slug, sources):
    d = Path(td) / "site-data" / "sources"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.json").write_text(json.dumps({"sources": sources}), encoding="utf-8")
    return td


class Format(unittest.TestCase):
    def test_seed_files_are_valid_and_every_entry_is_a_marked_placeholder(self):
        files = sorted((ROOT / "site-data" / "sources").glob("*.json"))
        self.assertGreaterEqual(len(files), 2)
        for f in files:
            for s in ms.load(str(ROOT), f.stem):
                if s.get("placeholder") is True:
                    self.assertIn("TODO", s["title"], f.name)
                    self.assertEqual(s["url"], "TODO", f"{f.name}: placeholders must not carry a real-looking URL")

    def test_mistakes_are_refused_with_the_reason(self):
        cases = {
            "unknown field": dict(GOOD, permision="granted"),
            "permission must be": dict(GOOD, permission="yes"),
            "kind must be": dict(GOOD, kind="podcast"),
            "url must be": dict(GOOD, url="http://museum.example/item"),
            "still says TODO": dict(GOOD, title="TODO: a title"),
            "embed_url must be": dict(GOOD, permission="granted", embed_url="https://evil.example/player"),
            "date must be": dict(GOOD, date="March 1940"),
            "'institution' is required": {k: v for k, v in GOOD.items() if k != "institution"},
        }
        for why, entry in cases.items():
            with tempfile.TemporaryDirectory() as td:
                write(td, "x", [entry])
                with self.assertRaises(ms.SourceError, msg=why) as ctx:
                    ms.load(td, "x")
                self.assertIn(why, str(ctx.exception))

    def test_wrong_types_get_a_clear_error_not_a_crash(self):
        for entry, field in ((dict(GOOD, date=1940), "'date' must be text"), (dict(GOOD, id=12), "'id' must be text"),
                             (dict(GOOD, creator=None), "'creator' must be text"),
                             (dict(GOOD, placeholder="yes"), "placeholder must be true or false")):
            with tempfile.TemporaryDirectory() as td:
                write(td, "x", [entry])
                with self.assertRaises(ms.SourceError) as ctx:
                    ms.load(td, "x")
                self.assertIn(field, str(ctx.exception))

    def test_duplicate_ids_are_refused(self):
        with tempfile.TemporaryDirectory() as td:
            write(td, "x", [GOOD, GOOD])
            with self.assertRaises(ms.SourceError):
                ms.load(td, "x")

    def test_no_file_means_no_sources(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(ms.load(td, "nobody"), [])
            self.assertIn("No outside interviews or media", ms.render(td, "nobody"))


class Permission(unittest.TestCase):
    def render_one(self, **kw):
        with tempfile.TemporaryDirectory() as td:
            write(td, "x", [dict(GOOD, **kw)])
            return ms.render(td, "x")

    def test_pending_and_link_only_only_link_out(self):
        for perm in ("pending", "link-only"):
            out = self.render_one(permission=perm, embed_url="https://www.youtube-nocookie.com/embed/abc")
            self.assertNotIn("data-embed", out, perm)
            self.assertNotIn("<iframe", out, perm)
            self.assertNotIn("youtube-nocookie", out, perm)
            self.assertIn('href="https://museum.example/item/1"', out, perm)
            self.assertIn("A museum", out)

    def test_granted_loads_nothing_until_play(self):
        out = self.render_one(permission="granted", embed_url="https://www.youtube-nocookie.com/embed/abc")
        self.assertIn('data-embed="https://www.youtube-nocookie.com/embed/abc"', out)
        self.assertIn("Play the recording", out)
        self.assertNotIn("<iframe", out)
        self.assertNotRegex(out, r'\bsrc="https://www\.youtube')

    def test_granted_without_a_player_is_still_a_link(self):
        out = self.render_one(permission="granted")
        self.assertNotIn("data-embed", out)
        self.assertIn("Shown with permission of A museum", out)

    def test_attribution_is_escaped(self):
        out = self.render_one(creator="<b>Dr X</b>", creator_role="historian", date="1940")
        self.assertIn("&lt;b&gt;Dr X&lt;/b&gt; (historian) &middot; A museum &middot; 1940", out)


class Package(unittest.TestCase):
    def test_wordpress_block_links_out_and_has_no_script(self):
        block = (ROOT / "inductees" / "einstein" / "copy.html").read_text(encoding="utf-8")
        part = block[block.index(ms.WP_START):block.index(ms.WP_END)]
        self.assertIn("Interviews and media from other institutions", part)
        self.assertIn('href="https://history.aip.org/catalog/icos/24126.html"', part)
        self.assertNotIn("<script", block)
        self.assertNotIn("data-embed", block)
        self.assertNotIn("TODO", part)

    def test_wordpress_block_never_embeds_even_when_granted(self):
        with tempfile.TemporaryDirectory() as td:
            write(td, "x", [dict(GOOD, permission="granted", embed_url="https://www.youtube-nocookie.com/embed/abc")])
            html_out, md, css = ms.render_wp(td, "x")
        self.assertNotIn("youtube-nocookie", html_out)
        self.assertIn('href="https://museum.example/item/1"', html_out)
        self.assertIn("https://museum.example/item/1", md)

    def test_no_sources_means_no_package_section(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(ms.render_wp(td, "nobody"), ("", "", ""))

    def test_site_page_shows_the_section_once(self):
        page = (SITE / "einstein.html").read_text(encoding="utf-8")
        self.assertEqual(page.count("Interviews and media from other institutions</h2>"), 1)
        self.assertNotIn(ms.WP_START, page)

    def test_real_sources_are_link_only_until_permission_is_on_file(self):
        for f in (ROOT / "site-data" / "sources").glob("*.json"):
            for s in ms.load(str(ROOT), f.stem):
                if s.get("placeholder") is not True:
                    self.assertEqual(s["permission"], "link-only", f"{f.name}: {s['id']}")


class BuiltSite(unittest.TestCase):
    def test_every_published_profile_has_the_section(self):
        for page in json.loads((ROOT / "site-data" / "published.json").read_text(encoding="utf-8"))["published"]:
            text = (SITE / f"{page}.html").read_text(encoding="utf-8")
            self.assertIn('id="interviews-and-media"', text, page)

    def test_built_pages_make_no_request_to_a_player_host(self):
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("<iframe", text, page.name)
            for host in ms.EMBED_HOSTS:
                self.assertNotRegex(text, r'\bsrc="https://' + re.escape(host), page.name)

    def test_placeholders_never_reach_the_published_pages(self):
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("ms-placeholder", text, page.name)
            self.assertNotIn("Placeholder &mdash; not a real source", text, page.name)

    def test_placeholders_are_drawn_and_labelled_in_a_preview_build(self):
        preview = ms.render(str(ROOT), "cruz", preview=True)
        self.assertIn("Placeholder &mdash; not a real source", preview)
        self.assertIn("ms-placeholder", preview)
        self.assertNotIn("ms-placeholder", ms.render(str(ROOT), "cruz"))


if __name__ == "__main__":
    unittest.main()
