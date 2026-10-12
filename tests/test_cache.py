import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError
from unittest.mock import patch

from pipeline.cache import SourceFetcher
from pipeline.schema import FetchStatus


class CacheTests(unittest.TestCase):
    def test_failed_fetch_says_fetch_failed_not_nonexistent(self):
        with tempfile.TemporaryDirectory() as td:
            def opener(req, timeout): raise URLError("offline fixture")
            f=SourceFetcher(Path(td), opener=opener)
            d=f.fetch("S001","https://example.test/missing")
            self.assertEqual(d.status, FetchStatus.FETCH_FAILED)
            self.assertIn("offline fixture", d.error)
            d2=f.fetch("S001","https://example.test/missing")
            self.assertTrue(d2.from_cache)
            self.assertEqual(d2.status, FetchStatus.FETCH_FAILED)

    def test_cached_unparsed_bytes_are_reparsed_without_network(self):
        with tempfile.TemporaryDirectory() as td:
            f=SourceFetcher(Path(td), opener=lambda req, timeout: (_ for _ in ()).throw(AssertionError("network must not run")))
            url="https://example.test/archive.pdf"
            meta_path, body_path=f._paths(url)
            body_path.write_bytes(b"%PDF fixture bytes")
            meta_path.write_text(json.dumps({
                "url":url,"status":"UNPARSED","title":"","retrieved_at":"2026-10-12T00:00:00+00:00",
                "content_type":"application/pdf","sha256":"fixture","error":"parser unavailable"
            }),encoding="utf-8")
            with patch("pipeline.cache.extract_text", return_value=("", "Recovered cached text", "")):
                d=f.fetch("S001",url)
            self.assertTrue(d.from_cache)
            self.assertEqual(d.status, FetchStatus.RETRIEVED)
            self.assertEqual(d.text, "Recovered cached text")


if __name__ == "__main__": unittest.main()
