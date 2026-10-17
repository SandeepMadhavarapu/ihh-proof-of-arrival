from __future__ import annotations

import datetime as _dt
import hashlib
import html
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Optional, Tuple

from .schema import FetchStatus, SourceDocument
from .security import SecurityValidationError, validate_public_http_url


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


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _parse_pdf(data: bytes) -> Tuple[str, str]:
    """Return (text, error). Never guesses when extraction is unavailable.

    pdftotext is asked for UTF-8 and its bytes are decoded explicitly. Decoding with the
    platform default (or text=True) crashed the whole fetch on Windows in UTF-8 mode when the
    tool emitted Latin-1; an unreadable PDF must only mark the page "could not read".
    """
    exe = shutil.which("pdftotext")
    if not exe:
        return "", "PDF retrieved but pdftotext is unavailable; content left unparsed"
    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.pdf"
            src.write_bytes(data)
            p = subprocess.run([exe, "-enc", "UTF-8", str(src), "-"], capture_output=True, timeout=45)
    except (OSError, subprocess.SubprocessError) as exc:
        return "", f"could not read PDF: {type(exc).__name__}"
    stdout = (p.stdout or b"").decode("utf-8", "replace").strip()
    if p.returncode != 0:
        stderr = (p.stderr or b"").decode("utf-8", "replace").strip()
        return "", f"pdftotext failed: {stderr[:300]}"
    if not stdout:
        return "", "could not read PDF: no extractable text"
    return stdout, ""


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


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_http_url(newurl, resolve_dns=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _public_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    """Resolve once and connect to that validated numeric address (no DNS rebind gap)."""
    host, port = address
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not infos:
        raise SecurityValidationError("source hostname resolved to no addresses")
    for family, kind, proto, _, sockaddr in infos:
        ip = sockaddr[0]
        validate_public_http_url(f"http://[{ip}]/" if ":" in ip else f"http://{ip}/")
    last_error = None
    for family, kind, proto, _, sockaddr in infos:
        sock = socket.socket(family, kind, proto)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    raise last_error or OSError("no source address connected")


class _PublicHTTPConnection(http.client.HTTPConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = _public_connection


class _PublicHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTTPSConnection retains the original hostname for TLS SNI/certificate validation.
        self._create_connection = _public_connection


class _PublicHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_PublicHTTPConnection, req)


class _PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_PublicHTTPSConnection, req, context=self._context)


DEFAULT_USER_AGENT = "IHH-Profile-Factory/1.0 (+museum research; build-time fetch)"


class SourceFetcher:
    def __init__(
        self,
        cache_dir: Path,
        timeout: int = 20,
        opener: Optional[Callable[[urllib.request.Request, int], object]] = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.user_agent = user_agent
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._opener = opener

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _paths(self, url: str) -> tuple[Path, Path]:
        k = self._key(url)
        return self.cache_dir / f"{k}.json", self.cache_dir / f"{k}.body"

    def _cached(self, source_id: str, url: str, meta_path: Path, body_path: Path) -> SourceDocument | None:
        if not meta_path.exists():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict) or any(not isinstance(v, str) for v in meta.values()):
                raise ValueError("cache metadata must be an object of strings")
            if meta.get("url") != url:
                raise ValueError("cached URL does not match cache key")
            status = FetchStatus(meta["status"])
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            return SourceDocument(source_id, url, FetchStatus.UNPARSED, retrieved_at=_now(), error=f"cache metadata invalid: {type(exc).__name__}", from_cache=True)

        text = ""
        if status in {FetchStatus.RETRIEVED, FetchStatus.UNPARSED}:
            if not body_path.exists():
                return SourceDocument(source_id, url, FetchStatus.UNPARSED, retrieved_at=meta.get("retrieved_at", ""), content_type=meta.get("content_type", ""), sha256=meta.get("sha256", ""), error="cache body missing; cached evidence not used", from_cache=True)
            data = body_path.read_bytes()
            expected = meta.get("sha256", "")
            actual = _sha(data)
            if not expected or actual != expected:
                return SourceDocument(source_id, url, FetchStatus.UNPARSED, retrieved_at=meta.get("retrieved_at", ""), content_type=meta.get("content_type", ""), sha256=expected, error="cache SHA-256 mismatch; cached evidence not used", from_cache=True)
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

    def fetch(self, source_id: str, url: str) -> SourceDocument:
        validate_public_http_url(url, resolve_dns=False)
        meta_path, body_path = self._paths(url)
        cached = self._cached(source_id, url, meta_path, body_path)
        if cached is not None:
            return cached

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/pdf,text/plain,*/*;q=0.5",
            },
        )
        try:
            if self._opener:
                # Injected openers are for deterministic/offline tests; URL shape is still checked.
                resp = self._opener(req, self.timeout)
            else:
                validate_public_http_url(url, resolve_dns=True)
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler({}), _SafeRedirectHandler(),
                    _PublicHTTPHandler(), _PublicHTTPSHandler(),
                )
                resp = opener.open(req, timeout=self.timeout)
            with resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                final_url = getattr(resp, "geturl", lambda: url)()
            validate_public_http_url(final_url, resolve_dns=False)
            title, text, parse_err = extract_text(data, content_type, final_url)
            status = FetchStatus.RETRIEVED if text else FetchStatus.UNPARSED
            doc = SourceDocument(
                source_id=source_id,
                url=url,
                status=status,
                title=title,
                retrieved_at=_now(),
                content_type=content_type,
                text=text,
                sha256=_sha(data),
                error=parse_err,
                from_cache=False,
            )
            _atomic_write(body_path, data)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, SecurityValidationError) as e:
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
        _atomic_write(meta_path, (json.dumps(meta, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        return doc
