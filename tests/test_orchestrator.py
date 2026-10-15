import tempfile
import unittest
from pathlib import Path

from pipeline.orchestrator import Orchestrator
from pipeline.schema import ProfileDraft
from pipeline.security import SecurityValidationError


class Noop: pass


class OrchestratorIsolationTests(unittest.TestCase):
    def test_rejects_output_outside_or_nested_under_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir(); (root/'albright-wp').mkdir()
            o=Orchestrator(root,Noop(),Noop(),Noop(),Noop())
            cases = [
                ProfileDraft('X','x',[],root/'albright-wp'),
                ProfileDraft('X','x',[],root/'elsewhere'),
                ProfileDraft('X','x',[],root/'profiles'/'bucket'/'x'),
                ProfileDraft('X','x',[],root/'profiles'/'wrong-slug'),
            ]
            for draft in cases:
                with self.assertRaises(SecurityValidationError):
                    o._assert_output_isolated(draft)
            valid=ProfileDraft('X','x',[],root/'profiles'/'x')
            o._assert_output_isolated(valid)


if __name__ == "__main__": unittest.main()
