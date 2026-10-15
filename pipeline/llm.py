from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Protocol

from .security import redact_text


class JSONClient(Protocol):
    def complete_json(self, system: str, user: str, *, temperature: float) -> Dict[str, Any]: ...


class OpenAIJSONClient:
    """Minimal build-time OpenAI Responses API client.

    The API key is read only from the environment and is never included in returned exceptions.
    A production model must be selected explicitly by --model or OPENAI_MODEL so the repository
    never silently depends on a model id that may age out.
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
        self.endpoint = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/") + "/responses"
        self._opener = opener or urllib.request.urlopen

    @staticmethod
    def _extract_text(data: Dict[str, Any]) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        parts: list[str] = []
        for item in data.get("output", []) or []:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []) or []:
                if isinstance(content, dict) and content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
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
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
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
