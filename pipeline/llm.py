from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Protocol


class JSONClient(Protocol):
    def complete_json(self, system: str, user: str, *, temperature: float) -> Dict[str, Any]: ...


class OpenAIJSONClient:
    """Minimal build-time OpenAI client. The API key is read only from the environment."""

    def __init__(self, model: str | None = None) -> None:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._key = key
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-5.6")
        self.endpoint = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/") + "/responses"

    @staticmethod
    def _extract_text(data: Dict[str, Any]) -> str:
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        parts: list[str] = []
        for item in data.get("output", []) or []:
            for content in item.get("content", []) or []:
                if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        if not parts:
            raise RuntimeError("OpenAI response did not contain output text")
        return "\n".join(parts)

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
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:1000]
            raise RuntimeError(f"OpenAI API HTTP {e.code}: {body}") from e
        text = self._extract_text(data).strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].lstrip()
        try:
            out = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError("OpenAI response was not valid JSON") from e
        if not isinstance(out, dict):
            raise RuntimeError("OpenAI JSON response must be an object")
        return out
