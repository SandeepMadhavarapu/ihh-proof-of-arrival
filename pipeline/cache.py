from __future__ import annotations

import datetime as _dt
import hashlib
import html
import json
import mimetypes
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Optional, Tuple

from .schema import FetchStatus, SourceDocument


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in self.SKIP:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4", "blockquote", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "blockquote", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
        self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.parts))
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        return raw.strip()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _parse_pdf(data: bytes) -> Tuple[str, str]:
    """Return (text, error). Never guesses when extraction is unavailable."""
    exe = shutil.which("pdftotext")
    if not exe:
        return "", "PDF retrieved but pdftotext is unavailable; content left unparsed"
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "source.pdf"
        src.write_bytes(data)
        p = subprocess.run([exe, str(src), "-"], capture_output=True, text=True, timeout=45)
        if p.returncode != 0:
            return "", f"pdftotext failed: {p.stderr.strip()[:300]}"
        return p.stdout.strip(), ""


def extract_text(data: bytes, content_type: str, url: str) -> Tuple[str, str, str]:
    """Return title, text, parse_error."""
    ct = (content_type or "").lower()
    if "pdf" in ct or url.lower().split("?", 1)[0].endswith(".pdf"):
        text, err = _parse_pdf(data)
        return "", text, err
    if "html" in ct or b"<html" in data[:4096].lower():
        enc = "utf-8"
        m = re.search(br"charset=[\"']?([A-Za-z0-9._-]+)", data[:8192], re.I)
        if m:
            try:
                enc = m.group(1).decode("ascii", "ignore") or "utf-8"
            except Exception:
                pass
        s = data.decode(enc, "replace")
        p = _TextExtractor()
        p.feed(s)
        return re.sub(r"\s+", " ", p.title).strip(), p.text(), ""
    try:
        return "", data.decode("utf-8").strip(), ""
    except UnicodeDecodeError:
        return "", "", "Retrieved content is binary/unsupported and was not converted to text"


class SourceFetcher:
    def __init__(
        self,
        cache_dir: Path,
        timeout: int = 20,
        opener: Optional[Callable[[urllib.request.Request, int], object]] = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._opener = opener

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _paths(self, url: str) -> tuple[Path, Path]:
        k = self._key(url)
        return self.cache_dir / f"{k}.json", self.cache_dir / f"{k}.body"

    def fetch(self, source_id: str, url: str) -> SourceDocument:
        meta_path, body_path = self._paths(url)
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            text = ""
            status = FetchStatus(meta["status"])
            # A previously retrieved PDF/binary may have been cached while its parser was
            # unavailable. Re-parse cached bytes on every read so installing pdftotext later
            # can turn UNPARSED into RETRIEVED without a network refetch.
            if body_path.exists() and status in {FetchStatus.RETRIEVED, FetchStatus.UNPARSED}:
                data = body_path.read_bytes()
                title, text, parse_err = extract_text(data, meta.get("content_type", ""), url)
                if text:
                    status = FetchStatus.RETRIEVED
                    if title and not meta.get("title"):
                        meta["title"] = title
                    meta["error"] = ""
                elif parse_err:
                    status = FetchStatus.UNPARSED
                    meta["error"] = parse_err
            return SourceDocument(
                source_id=source_id,
                url=url,
                status=status,
                title=meta.get("title", ""),
                retrieved_at=meta.get("retrieved_at", ""),
                content_type=meta.get("content_type", ""),
                text=text,
                sha256=meta.get("sha256", ""),
                error=meta.get("error", ""),
                from_cache=True,
            )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "IHH-Profile-Factory/1.0 (+museum research; build-time fetch)",
                "Accept": "text/html,application/pdf,text/plain,*/*;q=0.5",
            },
        )
        try:
            if self._opener:
                resp = self._opener(req, self.timeout)
            else:
                resp = urllib.request.urlopen(req, timeout=self.timeout)
            with resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                final_url = getattr(resp, "geturl", lambda: url)()
            title, text, parse_err = extract_text(data, content_type, final_url)
            status = FetchStatus.RETRIEVED if text else FetchStatus.UNPARSED
            err = parse_err
            body_path.write_bytes(data)
            doc = SourceDocument(
                source_id=source_id,
                url=url,
                status=status,
                title=title,
                retrieved_at=_now(),
                content_type=content_type,
                text=text,
                sha256=_sha(data),
                error=err,
                from_cache=False,
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            doc = SourceDocument(
                source_id=source_id,
                url=url,
                status=FetchStatus.FETCH_FAILED,
                retrieved_at=_now(),
                error=f"{type(e).__name__}: {e}",
                from_cache=False,
            )

        meta = {
            "url": doc.url,
            "status": doc.status.value,
            "title": doc.title,
            "retrieved_at": doc.retrieved_at,
            "content_type": doc.content_type,
            "sha256": doc.sha256,
            "error": doc.error,
        }
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        return doc
