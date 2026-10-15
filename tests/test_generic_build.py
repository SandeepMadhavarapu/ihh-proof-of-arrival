import csv
import tempfile
import unittest
from pathlib import Path

from pipeline.generic_build import build_profile
from pipeline.media_rights import MANIFEST_COLUMNS
from pipeline.security import SecurityValidationError


COPY='''# Example Person

**Status:** REQUIRES HUMAN SIGN-OFF

**Opening line (sits above the photograph):**
Example Person reached Example City in 1900.

**Credit (sits immediately beneath the photograph):**
No verified anchor photograph supplied in this test fixture.

**Standfirst:**
The source records one event in 1900.

---

## One
The source records one event in 1900.

## Two
The source records one event in 1900.

## Three
The source records one event in 1900.

## Four
The source records one event in 1900.

## Five
The source records one event in 1900.

---

**First-person quotation (one, as reported by Fixture Archive):**
> I arrived in 1900.

---

## Five discussion questions
1. What does the source establish?
2. What does it not establish?
3. Why does source wording matter?
4. What should a museum verify next?
5. What evidence would change the account?
## Two activities
**1. Trace the claim.** Find the supporting sentence in the source.
**2. Mark the boundary.** List what the source does not establish.
'''


def write_profile(root: Path, *, url="https://example.test/source", filename="(text source - no file)", kind="record") -> Path:
    p = root / "profiles" / "example-person"
    p.mkdir(parents=True)
    (p/'copy.md').write_text(COPY, encoding='utf-8')
    with (p/'media-manifest.csv').open('w', newline='', encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=MANIFEST_COLUMNS); w.writeheader(); w.writerow({
            **{k:'' for k in MANIFEST_COLUMNS}, "item_no":"1","kind":kind,"filename":filename,
            "title":"Fixture record","institution":"Fixture Archive","stable_item_url":url,
            "rights_statement_verbatim":"NOT LOCATED IN RETRIEVED SOURCE TEXT","status":"OPENED","gloss":"Test source"
        })
    return p


class GenericBuildTests(unittest.TestCase):
    def test_generic_output_has_no_albright_hardcodes_and_keeps_archival_style(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir()
            p=write_profile(root)
            build_profile(p, root)
            out=(p/'copy.html').read_text(encoding='utf-8')
            self.assertIn('Example Person',out)
            self.assertIn('REQUIRES HUMAN SIGN-OFF',out)
            self.assertIn('PROVENANCE REGISTER', out)
            self.assertIn('EVIDENCE-GATED PROFILE', out)
            for forbidden in ['Madeleine Albright','445648831','Prague Winter','981110_oath']:
                self.assertNotIn(forbidden,out)
            self.assertNotIn('<script',out.lower())
            self.assertNotRegex(out,r'\bsrc=["\']https?://')

    def test_builder_rejects_nested_or_external_profile_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir()
            nested=root/'profiles'/'bucket'/'example-person'; nested.mkdir(parents=True)
            (nested/'copy.md').write_text(COPY, encoding='utf-8')
            (nested/'media-manifest.csv').write_text(','.join(MANIFEST_COLUMNS)+'\n', encoding='utf-8')
            with self.assertRaises(SecurityValidationError):
                build_profile(nested, root)

    def test_unsafe_source_href_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir()
            p=write_profile(root, url='javascript:alert(1)')
            with self.assertRaises(SecurityValidationError):
                build_profile(p, root)

    def test_media_path_traversal_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir()
            p=write_profile(root, filename='../portrait.jpg', kind='photograph')
            with self.assertRaises(SecurityValidationError):
                build_profile(p, root)


if __name__ == "__main__": unittest.main()
