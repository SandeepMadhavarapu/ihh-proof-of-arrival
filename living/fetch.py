"""Polite, honest retrieval for the Living Museum.

Three ways a page can be "retrieved", and every Page records which one:
  network  fetched now by pipeline.cache.SourceFetcher (SSRF guards, SHA-checked cache) with an
           identifying User-Agent, after reading robots.txt with that SAME User-Agent, with a
           per-host delay between requests.
  human    a reviewer opened the page in an ordinary browser and saved it; imported with
           `python living/run.py import-snapshot`. Hashed and labelled retrieved_by=human.
  fixture  offline test data (living/eval/fixtures), used only by the eval and tests.

Never: solving challenges, rotating user agents or IPs, headless tricks to get past a 403, or
reading a blocked page any other way. A blocked page is "could not retrieve", nothing more.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
import urllib.robotparser
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

from pipeline.cache import SourceFetcher, extract_text
from pipeline.schema import FetchStatus

from .config import CACHE, Sources

try:  # Windows Python ships without a CA bundle; certificates are still fully verified.
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass


@dataclass
class Page:
    url: str
    status: str                 # RETRIEVED | FETCH_FAILED | UNPARSED | BLOCKED_BY_ROBOTS
    text: str = ""
    sha256: str = ""
    retrieved_at: str = ""
    retrieved_by: str = ""      # network | human | fixture
    error: str = ""
    title: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "RETRIEVED" and bool(self.text)

    def meta(self) -> dict:
        d = asdict(self)
        d.pop("text")
        return d


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


class Fetcher:
    def __init__(self, sources: Sources, *, role: str = "verifier", fresh: bool = True,
                 fixtures: dict[str, dict] | None = None, cache_root: Path = CACHE,
                 max_fetches: int | None = None) -> None:
        self.sources = sources
        self.fixtures = fixtures
        self.fresh = fresh
        self.cache_dir = cache_root / role
        self.human_dir = cache_root / "human"
        self.max_fetches = max_fetches
        self.fetch_count = 0
        self._last: dict[str, float] = {}
        self._robots: dict[str, object] = {}
        self._pages: dict[str, Page] = {}
        self._fetcher = None if fixtures is not None else SourceFetcher(
            self.cache_dir, timeout=sources.timeout, user_agent=sources.user_agent)

    # -- robots.txt (RFC 9309), read with the same User-Agent as the page fetch --------------
    def robots_allows(self, url: str) -> tuple[bool, str]:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            self._wait(p.netloc)
            req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": self.sources.user_agent})
            try:
                with urllib.request.urlopen(req, timeout=self.sources.timeout) as resp:
                    rp = urllib.robotparser.RobotFileParser()
                    rp.parse(resp.read().decode("utf-8", "replace").splitlines())
                    self._robots[base] = rp
            except urllib.error.HTTPError as exc:
                self._robots[base] = "allow" if 400 <= exc.code < 500 else "deny"
            except Exception:
                self._robots[base] = "deny"
        rule = self._robots[base]
        if rule == "allow":
            return True, "robots.txt answered 4xx: no restrictions (RFC 9309)"
        if rule == "deny":
            return False, "robots.txt unreachable or 5xx: treated as disallow (RFC 9309)"
        return rule.can_fetch(self.sources.user_agent, url), "robots.txt rules applied"

    def _wait(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None:
            delay = self.sources.rate_limit_seconds - (time.monotonic() - last)
            if delay > 0:
                time.sleep(delay)
        self._last[host] = time.monotonic()

    # -- human snapshots -----------------------------------------------------------------------
    def _human_paths(self, url: str) -> tuple[Path, Path]:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.human_dir / f"{key}.json", self.human_dir / f"{key}.body"

    def human_snapshot(self, url: str) -> Page | None:
        meta_path, body_path = self._human_paths(url)
        if not meta_path.exists() or not body_path.exists():
            return None
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        data = body_path.read_bytes()
        if hashlib.sha256(data).hexdigest() != meta.get("sha256"):
            return Page(url, "UNPARSED", retrieved_by="human", error="human snapshot SHA-256 mismatch; not used")
        title, text, err = extract_text(data, meta.get("content_type", "text/html"), url)
        return Page(url, "RETRIEVED" if text else "UNPARSED", text, meta["sha256"], meta["retrieved_at"],
                    "human", err or f"saved by {meta.get('reviewer', 'a reviewer')} in a normal browser", title)

    def import_human_snapshot(self, url: str, file: Path, reviewer: str) -> Page:
        if self.sources.tier(url) is None:
            raise ValueError("refusing to import a snapshot for a domain that is not on the allowlist")
        data = Path(file).read_bytes()
        meta_path, body_path = self._human_paths(url)
        self.human_dir.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(data)
        ctype = "application/pdf" if data[:5] == b"%PDF-" else "text/html"
        meta = {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "retrieved_at": _now(),
                "reviewer": reviewer, "content_type": ctype, "retrieved_by": "human"}
        meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
        return self.human_snapshot(url)

    # -- the one entry point -------------------------------------------------------------------
    def get(self, url: str) -> Page:
        if url in self._pages:
            return self._pages[url]
        page = self._get(url)
        self._pages[url] = page
        return page

    def _get(self, url: str) -> Page:
        if self.fixtures is not None:
            fx = self.fixtures.get(url)
            if fx is None:
                return Page(url, "FETCH_FAILED", retrieved_by="fixture", error="no offline fixture for this URL")
            return Page(url, fx.get("status", "RETRIEVED"), fx.get("text", ""), fx.get("sha256", ""),
                        fx.get("retrieved_at", ""), "fixture", fx.get("error", ""), fx.get("title", ""))
        if self.sources.tier(url) is None:
            return Page(url, "FETCH_FAILED", error="domain not on the allowlist; not fetched")
        if self.max_fetches is not None and self.fetch_count >= self.max_fetches:
            return Page(url, "FETCH_FAILED", error="per-run fetch cap reached; not fetched")
        allowed, why = self.robots_allows(url)
        if not allowed:
            human = self.human_snapshot(url)
            return human or Page(url, "BLOCKED_BY_ROBOTS", error=why)
        if self.fresh:  # the verifier re-fetches; never trust another stage's copy
            for path in self._fetcher._paths(url):
                path.unlink(missing_ok=True)
        self._wait(urlparse(url).netloc)
        self.fetch_count += 1
        try:
            doc = self._fetcher.fetch("S001", url)
        except Exception as exc:  # recorded, never treated as evidence
            doc = None
            err = f"could not retrieve: {type(exc).__name__}"
        if doc is not None and doc.status == FetchStatus.RETRIEVED and doc.text:
            return Page(url, "RETRIEVED", doc.text, doc.sha256, doc.retrieved_at, "network", title=doc.title)
        err = err if doc is None else f"could not retrieve: {doc.status.value} {doc.error}".strip()
        human = self.human_snapshot(url)
        if human is not None:
            return human
        return Page(url, "FETCH_FAILED" if doc is None or doc.status == FetchStatus.FETCH_FAILED else "UNPARSED",
                    error=err[:300])

    def snapshot_path(self, url: str) -> str:
        """Where the raw bytes behind a network Page are kept (gitignored)."""
        if self._fetcher is None:
            return ""
        return str(self._fetcher._paths(url)[1].relative_to(CACHE.parent.parent)).replace("\\", "/")
