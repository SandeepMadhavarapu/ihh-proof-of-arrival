import asyncio
import tempfile
import unittest
from pathlib import Path

from pipeline.orchestrator import Orchestrator
from pipeline.schema import ProfileDraft


class Noop: pass

class OrchestratorIsolationTests(unittest.TestCase):
    def test_rejects_output_outside_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'profiles').mkdir(); (root/'albright-wp').mkdir()
            o=Orchestrator(root,Noop(),Noop(),Noop(),Noop())
            d=ProfileDraft('X','x',[],root/'albright-wp')
            with self.assertRaises(ValueError): o._assert_output_isolated(d)
            d2=ProfileDraft('X','x',[],root/'elsewhere')
            with self.assertRaises(ValueError): o._assert_output_isolated(d2)
            d3=ProfileDraft('X','x',[],root/'profiles'/'x')
            o._assert_output_isolated(d3)


if __name__ == "__main__": unittest.main()
