"""Option B: the Verification Desk is a corrections log with no public tally against one site,
and the full findings for IHH's editors live only in a private handover memo."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MEMO = ROOT / "handover" / "CORRECTIONS-MEMO-FOR-IHH.md"


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
        memo = MEMO.read_text(encoding="utf-8")
        self.assertIn("Never publish this file", memo)
        self.assertEqual(len(re.findall(r"^### ", memo, re.M)), 14)
        self.assertEqual(len(re.findall(r"^Page: https://immigranthallofhonor\.org/inductees/", memo, re.M)), 4)
        for page in SITE.rglob("*"):
            if page.is_file() and page.suffix in {".html", ".js", ".css", ".xml", ".txt", ".json"}:
                self.assertNotIn("CORRECTIONS-MEMO", page.read_text(encoding="utf-8", errors="ignore"), page)


if __name__ == "__main__":
    unittest.main()
