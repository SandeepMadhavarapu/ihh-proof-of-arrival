"""Option B: the Verification Desk is a corrections log with no public tally against one site,
and the full findings for IHH's editors live only in a private, never-committed memo."""
import importlib.util
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def load_gen():
    spec = importlib.util.spec_from_file_location("ihh_gen", ROOT / "site-src" / "gen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CorrectionsLog(unittest.TestCase):
    def setUp(self):
        self.verify = (SITE / "verify.html").read_text(encoding="utf-8")

    def test_no_public_tally_against_the_live_site(self):
        for phrase in ("published on the live IHH site", "did not survive", "live-site claims",
                       "sponsor&rsquo;s own mistakes", "Published on immigranthallofhonor.org"):
            self.assertNotIn(phrase, self.verify)
        home = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("published on a real museum website today", home)

    def test_claim_tags_and_locations_do_not_name_the_site(self):
        for where in re.findall(r'<p class="cl-where">(.*?)</p>', self.verify, re.S):
            self.assertNotIn("immigranthallofhonor.org", where)
        self.assertNotIn('cl-tag live">Published on', self.verify)

    def test_memo_is_complete_and_private(self):
        gen = load_gen()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memo.md"
            gen.write_memo(str(path))
            memo = path.read_text(encoding="utf-8")
        self.assertIn("Never publish this file", memo)
        self.assertEqual(len(re.findall(r"^### ", memo, re.M)), 14)
        self.assertEqual(len(re.findall(r"^Page: https://immigranthallofhonor\.org/inductees/", memo, re.M)), 4)
        # written only under private/, which git ignores, and never referenced from the site
        self.assertEqual(Path(gen.MEMO_PATH).parent.name, "private")
        tracked = subprocess.run(["git", "ls-files", "--", "*CORRECTIONS-MEMO*"], cwd=ROOT,
                                 capture_output=True, text=True).stdout.strip()
        self.assertEqual(tracked, "", "the corrections memo must never be committed")
        ignored = subprocess.run(["git", "check-ignore", "-q", "private/CORRECTIONS-MEMO-FOR-IHH.md"], cwd=ROOT)
        self.assertEqual(ignored.returncode, 0, "private/ must be git-ignored")
        for page in SITE.rglob("*"):
            if page.is_file() and page.suffix in {".html", ".js", ".css", ".xml", ".txt", ".json"}:
                self.assertNotIn("CORRECTIONS-MEMO", page.read_text(encoding="utf-8", errors="ignore"), page)

if __name__ == "__main__":
    unittest.main()
