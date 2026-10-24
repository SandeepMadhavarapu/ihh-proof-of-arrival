import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from pipeline.llm import OPENAI_RESPONSES_ENDPOINT, OpenAIJSONClient
from pipeline.security import redact_text


class FakeResponse:
    def __init__(self, payload):
        self.payload=payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.payload).encode('utf-8')


class LLMClientTests(unittest.TestCase):
    def test_model_must_be_explicit_key_stays_out_of_payload_and_endpoint_is_fixed(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'sk-test-secret'}, clear=True):
            with self.assertRaisesRegex(RuntimeError,'model is not configured'):
                OpenAIJSONClient(opener=lambda req, timeout: None)

        captured={}
        def opener(req, timeout):
            captured['url']=req.full_url
            captured['headers']=dict(req.header_items())
            captured['body']=json.loads(req.data.decode('utf-8'))
            return FakeResponse({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"ok":true}'}]}]})
        with patch.dict(os.environ, {
            'OPENAI_API_KEY':'sk-test-secret',
            'OPENAI_MODEL':'test-model-id',
            'OPENAI_API_BASE':'https://attacker.invalid/v1',
        }, clear=True):
            c=OpenAIJSONClient(opener=opener)
            self.assertEqual(c.model,'test-model-id')
            self.assertEqual(c.endpoint,OPENAI_RESPONSES_ENDPOINT)
            out=c.complete_json('system','user',temperature=0.0)
        self.assertEqual(out,{'ok':True})
        self.assertEqual(captured['url'],OPENAI_RESPONSES_ENDPOINT)
        self.assertNotIn('sk-test-secret', json.dumps(captured['body']))
        self.assertEqual(captured['body']['model'],'test-model-id')
        self.assertEqual(captured['body']['temperature'],0)
        self.assertEqual(captured['body']['text'],{'format':{'type':'json_object'}})
        self.assertFalse(captured['body']['store'])
        self.assertIn('Bearer sk-test-secret', captured['headers'].get('Authorization',''))

    def test_http_error_never_echoes_api_key_or_full_provider_body(self):
        secret='sk-' + 'super-secret-123456789'  # synthetic key assembled only inside this test
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


class _Block:
    def __init__(self, text): self.type = "text"; self.text = text


class _Msg:
    def __init__(self, text, stop="end_turn"): self.content = [_Block(text)]; self.stop_reason = stop


class _FakeAnthropic:
    def __init__(self, reply=None, error=None):
        self.calls = []
        self.reply, self.error = reply, error
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.reply


class AnthropicClientTests(unittest.TestCase):
    def test_key_and_model_must_come_from_environment(self):
        from pipeline.llm import AnthropicJSONClient
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_API_KEY is not set"):
                AnthropicJSONClient(client=_FakeAnthropic())
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-secret"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_MODEL"):
                AnthropicJSONClient(client=_FakeAnthropic())

    def test_schema_sent_temperature_only_where_accepted(self):
        from pipeline.llm import AnthropicJSONClient
        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}
        for model, expect_temp in [("claude-opus-5-5", False), ("claude-haiku-4-5", True)]:
            fake = _FakeAnthropic(_Msg('{"ok": true}'))
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-secret", "ANTHROPIC_MODEL": model}, clear=True):
                c = AnthropicJSONClient(client=fake)
                self.assertEqual(c.complete_json("sys", "user", temperature=0.0, json_schema=schema), {"ok": True})
            sent = fake.calls[0]
            self.assertEqual(sent["model"], model)
            self.assertEqual(sent["output_config"]["format"], {"type": "json_schema", "schema": schema})
            self.assertEqual("temperature" in sent, expect_temp)
            self.assertNotIn("sk-ant-test-secret", json.dumps(sent))
            self.assertNotIn("fallbacks", sent)

    def test_refusal_truncation_and_bad_json_fail_closed(self):
        from pipeline.llm import AnthropicJSONClient
        env = {"ANTHROPIC_API_KEY": "sk-ant-test-secret", "ANTHROPIC_MODEL": "claude-opus-5-5"}
        for reply, pattern in [(_Msg("", "refusal"), "refusal"), (_Msg('{"ok"', "max_tokens"), "truncated"),
                               (_Msg("not json"), "not valid JSON"), (_Msg("[1, 2]"), "must be an object")]:
            with patch.dict(os.environ, env, clear=True):
                with self.assertRaisesRegex(RuntimeError, pattern):
                    AnthropicJSONClient(client=_FakeAnthropic(reply)).complete_json("s", "u", temperature=0.0)

    def test_provider_error_never_echoes_key(self):
        from pipeline.llm import AnthropicJSONClient
        env = {"ANTHROPIC_API_KEY": "sk-ant-test-secret", "ANTHROPIC_MODEL": "claude-opus-5-5"}
        with patch.dict(os.environ, env, clear=True):
            c = AnthropicJSONClient(client=_FakeAnthropic(error=ValueError("bad key sk-ant-test-secret")))
            with self.assertRaises(RuntimeError) as cm:
                c.complete_json("s", "u", temperature=0.0)
        self.assertNotIn("sk-ant-test-secret", str(cm.exception))
        self.assertIsNone(cm.exception.__cause__)
