import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from pipeline.llm import OpenAIJSONClient
from pipeline.security import redact_text


class FakeResponse:
    def __init__(self, payload):
        self.payload=payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.payload).encode('utf-8')


class LLMClientTests(unittest.TestCase):
    def test_model_must_be_explicit_and_key_stays_out_of_payload(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'sk-test-secret'}, clear=True):
            with self.assertRaisesRegex(RuntimeError,'model is not configured'):
                OpenAIJSONClient(opener=lambda req, timeout: None)

        captured={}
        def opener(req, timeout):
            captured['headers']=dict(req.header_items())
            captured['body']=json.loads(req.data.decode('utf-8'))
            return FakeResponse({'output_text':'{"ok":true}'})
        with patch.dict(os.environ, {'OPENAI_API_KEY':'sk-test-secret','OPENAI_MODEL':'test-model-id'}, clear=True):
            c=OpenAIJSONClient(opener=opener)
            self.assertEqual(c.model,'test-model-id')
            out=c.complete_json('system','user',temperature=0.0)
        self.assertEqual(out,{'ok':True})
        self.assertNotIn('sk-test-secret', json.dumps(captured['body']))
        self.assertEqual(captured['body']['model'],'test-model-id')
        self.assertIn('Bearer sk-test-secret', captured['headers'].get('Authorization',''))

    def test_http_error_never_echoes_api_key_or_full_provider_body(self):
        secret='sk-super-secret-123456789'
        body=json.dumps({'error':{'type':'invalid_request_error','message':f'bad request for {secret}; '+('x'*1000)}}).encode()
        def opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url,401,'Unauthorized',{},io.BytesIO(body))
        with patch.dict(os.environ, {'OPENAI_API_KEY':secret,'OPENAI_MODEL':'test-model-id'}, clear=True):
            c=OpenAIJSONClient(opener=opener)
            with self.assertRaises(RuntimeError) as ctx:
                c.complete_json('system','user',temperature=0.0)
        msg=str(ctx.exception)
        self.assertNotIn(secret,msg)
        self.assertIn('[REDACTED]',msg)
        self.assertLess(len(msg),500)

    def test_redactor_catches_bearer_and_key_patterns(self):
        s=redact_text('Authorization: Bearer abcdefghijklmnop and sk-abcdefghi')
        self.assertNotIn('abcdefghijklmnop',s)
        self.assertNotIn('sk-abcdefghi',s)


if __name__ == '__main__': unittest.main()
