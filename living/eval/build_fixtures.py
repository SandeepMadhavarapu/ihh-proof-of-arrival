"""Build the offline eval fixtures from pages actually fetched over the network.

    python living/eval/build_fixtures.py

Reads the local fetch caches (gitignored: living/.cache/*/ and, if present, the feasibility
spike's cache), re-extracts each page's text with pipeline.cache.extract_text, and writes
living/eval/fixtures.json containing, for every URL the eval cases cite, EXCERPTS of about
+/-2,500 characters around each cited span (merged when they overlap), plus the full page's
SHA-256, title and retrieval time. Excerpts, not whole pages: enough to exercise every gate, small
enough not to republish anyone's page. A URL that could not be retrieved is recorded as such.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pipeline.cache import extract_text  # noqa: E402
from living.textnorm import norm  # noqa: E402

RADIUS = 2500
EVAL = ROOT / "living" / "eval"


def cached_pages() -> dict[str, dict]:
    pages: dict[str, dict] = {}
    metas = glob.glob(str(ROOT / "living" / ".cache" / "*" / "*.json")) + \
        glob.glob(str(ROOT / "spike" / ".profile-factory-cache" / "*.json"))
    for meta_path in metas:
        try:
            meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        url = meta.get("url")
        body = Path(meta_path[:-5] + ".body")
        if not url:
            continue
        if meta.get("status") != "RETRIEVED" or not body.exists():
            pages.setdefault(url, {"status": "FETCH_FAILED", "error": meta.get("error", "")[:200]})
            continue
        data = body.read_bytes()
        if hashlib.sha256(data).hexdigest() != meta.get("sha256"):
            continue
        title, text, err = extract_text(data, meta.get("content_type", ""), url)
        if not text:
            continue
        prev = pages.get(url)
        if prev and prev.get("status") == "RETRIEVED" and prev["retrieved_at"] >= meta.get("retrieved_at", ""):
            continue
        pages[url] = {"status": "RETRIEVED", "text": norm(text), "title": title, "sha256": meta["sha256"],
                      "retrieved_at": meta.get("retrieved_at", "")}
    return pages


def excerpt(text: str, spans: list[str]) -> str:
    ranges = []
    for s in spans:
        pos = text.find(norm(s))
        if pos >= 0:
            ranges.append([max(0, pos - RADIUS), min(len(text), pos + len(norm(s)) + RADIUS)])
    ranges.sort()
    merged: list[list[int]] = []
    for r in ranges:
        if merged and r[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], r[1])
        else:
            merged.append(r)
    return " [...] ".join(text[a:b] for a, b in merged)


def main() -> int:
    cases = json.loads((EVAL / "cases.json").read_text(encoding="utf-8"))["cases"]
    pages = cached_pages()
    wanted: dict[str, list[str]] = {}
    for c in cases:
        if c.get("page_text") is not None:
            continue
        for e in c["evidence"]:
            wanted.setdefault(e["url"], []).append(e["span"])
    fixtures, missing = {}, []
    for url, spans in sorted(wanted.items()):
        page = pages.get(url)
        if page is None:
            missing.append(url)
            fixtures[url] = {"status": "FETCH_FAILED", "error": "no network copy available when fixtures were built"}
        elif page["status"] != "RETRIEVED":
            fixtures[url] = {"status": page["status"], "error": page.get("error", "")}
        else:
            fixtures[url] = {"status": "RETRIEVED", "excerpt": True, "title": page["title"],
                             "sha256": page["sha256"], "retrieved_at": page["retrieved_at"],
                             "text": excerpt(page["text"], spans) or page["text"][:RADIUS]}
    out = {"_note": "Excerpts of pages fetched over the network on the dates shown, around the spans the eval "
                    "cites. Built by living/eval/build_fixtures.py. Not whole pages; not for republication.",
           "pages": fixtures}
    (EVAL / "fixtures.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(fixtures)} fixture pages, {sum(1 for f in fixtures.values() if f['status'] == 'RETRIEVED')} retrieved; "
          f"no copy for: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
