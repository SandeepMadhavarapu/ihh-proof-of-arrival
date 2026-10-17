from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Protocol

from .security import redact_text


OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"


class _NoAPIRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("OpenAI API redirect refused; credentials remain at the fixed endpoint")


class JSONClient(Protocol):
    def complete_json(self, system: str, user: str, *, temperature: float) -> Dict[str, Any]: ...


# Claude models documented as still accepting sampling parameters. Current models (Opus 4.7 and
# later, the 5.x family) reject `temperature` with HTTP 400, so it is sent only to these.
ANTHROPIC_TEMPERATURE_MODELS = frozenset({"claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"})


class AnthropicJSONClient:
    """Minimal build-time Claude client through the official `anthropic` SDK.

    The key is read only from ANTHROPIC_API_KEY and the model only from ANTHROPIC_MODEL (or the
    `model` argument); there is no hard-coded model. The SDK is imported lazily so the offline
    test suite and every no-key run need no third-party package. JSON is requested with
    structured outputs when a schema is supplied. A refusal or truncated answer raises, so callers
    fail closed instead of reading partial output. Server-side model fallbacks are deliberately
    NOT enabled: a judge that silently switches model would make its verdicts unreproducible.
    """

    def __init__(self, model: str | None = None, client: Any = None) -> None:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        selected = (model or os.environ.get("ANTHROPIC_MODEL", "")).strip()
        if not selected:
            raise RuntimeError("Anthropic model is not configured; set ANTHROPIC_MODEL")
        self._key = key
        self.model = selected
        self.effort = os.environ.get("ANTHROPIC_EFFORT", "").strip()
        if client is None:
            try:
                import anthropic  # noqa: PLC0415 - optional dependency, only with a key
            except ImportError:
                raise RuntimeError("the 'anthropic' package is not installed; run: pip install anthropic") from None
            client = anthropic.Anthropic(api_key=key, max_retries=2)
        self._client = client

    @property
    def sampling(self) -> str:
        return ("temperature=0" if self.model in ANTHROPIC_TEMPERATURE_MODELS
                else "model default sampling (this model does not accept temperature)")

    def complete_json(self, system: str, user: str, *, temperature: float,
                      json_schema: Dict[str, Any] | None = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": 16000,
            "system": system + "\nReturn one JSON object.",
            "messages": [{"role": "user", "content": user}],
        }
        output_config: Dict[str, Any] = {}
        if self.effort:
            output_config["effort"] = self.effort
        if json_schema:
            output_config["format"] = {"type": "json_schema", "schema": json_schema}
        if output_config:
            kwargs["output_config"] = output_config
        if self.model in ANTHROPIC_TEMPERATURE_MODELS:
            kwargs["temperature"] = temperature
        try:
            response = self._client.messages.create(**kwargs)
        except Exception as exc:  # SDK error classes vary by version; never echo the key
            detail = redact_text(f"{type(exc).__name__}: {getattr(exc, 'message', exc)}", [self._key])
            raise RuntimeError("Anthropic API error: " + detail[:240]) from None
        stop = getattr(response, "stop_reason", None)
        if stop == "refusal":
            raise RuntimeError("Anthropic model declined the request (refusal)")
        if stop == "max_tokens":
            raise RuntimeError("Anthropic response was truncated (max_tokens)")
        text = "".join(getattr(b, "text", "") for b in getattr(response, "content", []) or []
                       if getattr(b, "type", "") == "text").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].lstrip()
        try:
            out = json.loads(text)
        except json.JSONDecodeError:
            raise RuntimeError("Anthropic model output was not valid JSON") from None
        if not isinstance(out, dict):
            raise RuntimeError("Anthropic JSON response must be an object")
        return out


class OpenAIJSONClient:
    """Minimal build-time OpenAI Responses API client.

    The API key is read only from the environment and is never included in returned exceptions.
    A production model must be selected explicitly by --model or OPENAI_MODEL so the repository
    never silently depends on a model id that may age out. The bearer key is sent only to the fixed
    official OpenAI HTTPS Responses endpoint; this client has no arbitrary API-base override.
    """

    def __init__(self, model: str | None = None, opener=None) -> None:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        selected = model or os.environ.get("OPENAI_MODEL", "")
        if not selected.strip():
            raise RuntimeError("OpenAI model is not configured; pass --model or set OPENAI_MODEL")
        self._key = key
        self.model = selected.strip()
        self.endpoint = OPENAI_RESPONSES_ENDPOINT
        self._opener = opener or urllib.request.build_opener(_NoAPIRedirects()).open

    @staticmethod
    def _extract_text(data: Dict[str, Any]) -> str:
        if not isinstance(data, dict) or data.get("status") != "completed" or data.get("error"):
            raise RuntimeError("OpenAI response did not complete successfully")
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        parts: list[str] = []
        for item in data.get("output", []) or []:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []) or []:
                if isinstance(content, dict) and content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
                elif isinstance(content, dict) and content.get("type") == "refusal":
                    raise RuntimeError("OpenAI response refused the request")
        if not parts:
            raise RuntimeError("OpenAI response did not contain output text")
        return "\n".join(parts)

    def _safe_http_error(self, error: urllib.error.HTTPError) -> RuntimeError:
        provider_type = ""
        provider_message = ""
        try:
            raw = error.read().decode("utf-8", "replace")[:4000]
            parsed = json.loads(raw)
            err = parsed.get("error", {}) if isinstance(parsed, dict) else {}
            if isinstance(err, dict):
                provider_type = str(err.get("type", ""))[:80]
                provider_message = str(err.get("message", ""))[:240]
        except Exception:
            pass
        detail = f"OpenAI API HTTP {error.code}"
        if provider_type:
            detail += f" ({redact_text(provider_type, [self._key])})"
        if provider_message:
            detail += ": " + redact_text(provider_message, [self._key])
        return RuntimeError(detail)

    def complete_json(self, system: str, user: str, *, temperature: float) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "store": False,
            "text": {"format": {"type": "json_object"}},
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system + "\nReturn one JSON object."}]},
                {"role": "user", "content": [{"type": "input_text", "text": user}]},
            ],
        }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(req, timeout=120) as r:
                raw = r.read().decode("utf-8")
            data = json.loads(raw)
        except urllib.error.HTTPError as e:
            raise self._safe_http_error(e) from e
        except urllib.error.URLError as e:
            raise RuntimeError("OpenAI API network error: " + redact_text(str(e.reason), [self._key])[:240]) from e
        except TimeoutError as e:
            raise RuntimeError("OpenAI API request timed out") from e
        except json.JSONDecodeError as e:
            raise RuntimeError("OpenAI API response envelope was not valid JSON") from e

        text = self._extract_text(data).strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].lstrip()
        try:
            out = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError("OpenAI model output was not valid JSON") from e
        if not isinstance(out, dict):
            raise RuntimeError("OpenAI JSON response must be an object")
        return out
