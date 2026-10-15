import asyncio
import json
import socket
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import Mock, patch

from pipeline.cache import SourceFetcher, _SafeRedirectHandler, _public_connection
from pipeline.llm import OpenAIJSONClient
from pipeline.orchestrator import Orchestrator
from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument
from pipeline.security import SecurityValidationError, validate_media_filename, validate_public_http_url
from pipeline.verifier import VerifierAgent, MAX_SOURCE_CHARS
from pipeline.media_rights import MediaRightsAgent


class ReleaseBoundaryTests(unittest.TestCase):
    def test_incomplete_api_response_cannot_pass_even_with_valid_json(self):
        for status in ('incomplete', 'failed', 'queued', 'in_progress', None):
            with self.subTest(status=status), self.assertRaises(RuntimeError):
                OpenAIJSONClient._extract_text({'status': status, 'output_text': '{"ok":true}'})
        with self.assertRaisesRegex(RuntimeError, 'refused'):
            OpenAIJSONClient._extract_text({'status': 'completed', 'output': [
                {'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'no'}]}
            ]})

    def test_corrupt_metadata_is_not_evidence_and_never_fetches(self):
        with tempfile.TemporaryDirectory() as td:
            opener = Mock(side_effect=AssertionError('network forbidden'))
            fetcher = SourceFetcher(Path(td), opener=opener)
            url = 'https://example.test/source'
            meta, body = fetcher._paths(url)
            for value in ('[]', 'null', '{broken', '{"url": 42}'):
                meta.write_text(value, encoding='utf-8')
                result = fetcher.fetch('S001', url)
                self.assertEqual(result.status, FetchStatus.UNPARSED)
                self.assertEqual(result.text, '')
            opener.assert_not_called()

    def test_private_redirect_is_blocked_before_request_creation(self):
        req = urllib.request.Request('https://example.test/source')
        for target in ('http://127.0.0.1/', 'http://169.254.169.254/', 'http://[::1]/'):
            with self.subTest(target=target), self.assertRaises(SecurityValidationError):
                _SafeRedirectHandler().redirect_request(req, None, 302, 'Found', {}, target)

    def test_connection_pins_resolved_numeric_address(self):
        info = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]
        sock = Mock()
        with patch('pipeline.cache.socket.getaddrinfo', return_value=info) as dns, patch('pipeline.cache.socket.socket', return_value=sock):
            self.assertIs(_public_connection(('example.test', 443), 12), sock)
            sock.connect.assert_called_once_with(('93.184.216.34', 443))
            dns.assert_called_once()

    def test_connection_rejects_mixed_public_private_dns_without_connecting(self):
        info = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443)) for ip in ('93.184.216.34', '10.0.0.1')]
        with patch('pipeline.cache.socket.getaddrinfo', return_value=info), patch('pipeline.cache.socket.socket') as sock:
            with self.assertRaises(SecurityValidationError):
                _public_connection(('example.test', 443))
            sock.assert_not_called()

    def test_windows_ambiguous_filenames_and_url_shapes_are_rejected(self):
        for name in ('CON.jpg', 'nul.png', 'LPT1.webp', 'image.jpg.', 'image.jpg ', '../image.jpg'):
            with self.subTest(name=name), self.assertRaises(SecurityValidationError):
                validate_media_filename(name)
        for url in ('https://example.test:bad/', 'https://example.test\\@127.0.0.1/', 'https://example.test/a b'):
            with self.subTest(url=url), self.assertRaises(SecurityValidationError):
                validate_public_http_url(url)

    def test_large_source_refuses_partial_verification_and_rights_review(self):
        llm = Mock()
        draft = ProfileDraft('X', 'x', [], Path('unused'))
        draft.sources = {'S001': SourceDocument('S001', 'https://example.test', FetchStatus.RETRIEVED, text='x' * (MAX_SOURCE_CHARS + 1))}
        self.assertEqual(VerifierAgent(llm)._source_blocks(draft), [])
        self.assertIn('refusing partial verification', draft.failure_reason)
        draft.failure_reason = ''
        asyncio.run(MediaRightsAgent(llm).run(draft))
        self.assertIn('refusing partial rights review', draft.failure_reason)
        llm.complete_json.assert_not_called()

    def test_failed_rerun_invalidates_old_success_on_return_and_exception(self):
        class Researcher:
            async def run(self, draft):
                draft.failure_reason = 'no evidence'
        class ExplodingResearcher:
            async def run(self, draft):
                raise RuntimeError('fixture failure')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / 'profiles' / 'x'
            out.mkdir(parents=True)
            for researcher in (Researcher(), ExplodingResearcher()):
                (out / 'profile-state.json').write_text('{"completed":true}')
                (out / 'build-qa-report.json').write_text('{"passed":true}')
                orch = Orchestrator(root, researcher, Mock(), Mock(), Mock())
                try:
                    asyncio.run(orch.run(ProfileDraft('X', 'x', [], out)))
                except RuntimeError:
                    pass
                state = json.loads((out / 'profile-state.json').read_text())
                qa = json.loads((out / 'build-qa-report.json').read_text())
                self.assertFalse(state['completed'])
                self.assertFalse(state['museum_ready'])
                self.assertEqual(state['human_signoff'], 'REQUIRED')
                self.assertTrue(state['failure_reason'])
                self.assertFalse(qa['passed'])


if __name__ == '__main__':
    unittest.main()
