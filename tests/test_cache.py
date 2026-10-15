import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError
from unittest.mock import patch

from pipeline.cache import SourceFetcher
from pipeline.schema import FetchStatus
from pipeline.security import SecurityValidationError


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
            data=b"%PDF fixture bytes"
            body_path.write_bytes(data)
            meta_path.write_text(json.dumps({
                "url":url,"status":"UNPARSED","title":"","retrieved_at":"2026-10-12T00:00:00+00:00",
                "content_type":"application/pdf","sha256":hashlib.sha256(data).hexdigest(),"error":"parser unavailable"
            }),encoding="utf-8")
            with patch("pipeline.cache.extract_text", return_value=("", "Recovered cached text", "")):
                d=f.fetch("S001",url)
            self.assertTrue(d.from_cache)
            self.assertEqual(d.status, FetchStatus.RETRIEVED)
            self.assertEqual(d.text, "Recovered cached text")

    def test_cache_hash_mismatch_is_never_used_as_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            f=SourceFetcher(Path(td), opener=lambda req, timeout: (_ for _ in ()).throw(AssertionError("network must not run")))
            url="https://example.test/source"
            meta_path, body_path=f._paths(url)
            body_path.write_bytes(b"tampered")
            meta_path.write_text(json.dumps({
                "url":url,"status":"RETRIEVED","title":"","retrieved_at":"2026-10-12T00:00:00+00:00",
                "content_type":"text/plain","sha256":"00"*32,"error":""
            }),encoding="utf-8")
            d=f.fetch("S001",url)
            self.assertEqual(d.status, FetchStatus.UNPARSED)
            self.assertEqual(d.text, "")
            self.assertIn("SHA-256 mismatch", d.error)

    def test_private_and_local_urls_are_rejected_before_fetch(self):
        with tempfile.TemporaryDirectory() as td:
            f=SourceFetcher(Path(td), opener=lambda req, timeout: (_ for _ in ()).throw(AssertionError("must not fetch")))
            for url in ["http://127.0.0.1/x", "http://localhost/x", "http://10.0.0.5/x", "file:///etc/passwd"]:
                with self.subTest(url=url), self.assertRaises(SecurityValidationError):
                    f.fetch("S001",url)


if __name__ == "__main__": unittest.main()
