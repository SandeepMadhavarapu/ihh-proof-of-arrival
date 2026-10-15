import unittest
from pathlib import Path

from pipeline.schema import Claim, ProfileDraft, Provenance, Verdict


class SchemaTests(unittest.TestCase):
    def test_claim_serializes_enum_values(self):
        c = Claim("C1", "A fact.", Provenance.RECORD, verdict=Verdict.CONFIRMED)
        self.assertEqual(c.to_dict()["provenance"], "RECORD")
        self.assertEqual(c.to_dict()["verdict"], "CONFIRMED")

    def test_profile_defaults_to_human_signoff(self):
        d = ProfileDraft("Name", "name", ["https://example.test"], Path("profiles/name"))
        self.assertEqual(d.status, "REQUIRES HUMAN SIGN-OFF")
        self.assertFalse(d.completed)


if __name__ == "__main__":
    unittest.main()
