"""Final-pass check for the R3 media-permissions research.

    python review/workstream-3/check_media_permissions.py            # pages read with the fetcher
    python review/workstream-3/check_media_permissions.py --browser  # print the JS check for browser pages

For every page marked via=fetch, re-fetches it with the Living Museum's polite fetcher
(identifying User-Agent, robots.txt; allowlist not applied because these are research pages, not
museum evidence) and confirms each quoted span appears after whitespace normalization.
Pages marked via=browser cannot be fetched by a script (403 or JavaScript-rendered); for those
the --browser flag prints a snippet to run in an ordinary browser tab on that page, and the
results are recorded in browser-span-check.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from living.config import load_sources  # noqa: E402
from living.fetch import Fetcher  # noqa: E402
from living.textnorm import norm  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> int:
    data = json.loads((HERE / "media-permissions-research.json").read_text(encoding="utf-8"))
    if "--browser" in sys.argv:
        for p in data["pages"]:
            if p["via"] == "browser":
                print(p["id"], p["url"], json.dumps(p["spans"], ensure_ascii=False))
        return 0
    sources = load_sources()
    fetcher = Fetcher(sources, role="research-check", fresh=True)
    fetcher.sources.tier = lambda url: 2 if url.startswith("https://") else None
    bad = 0
    for p in data["pages"]:
        if p["via"] not in ("fetch", "fetch-image-pdf"):
            continue
        page = fetcher.get(p["url"])
        if p["via"] == "fetch-image-pdf":   # bytes retrieved; a scan has no text to quote
            ok = page.status in ("RETRIEVED", "UNPARSED") and "no extractable text" in (page.error or "") or page.ok
            print(f"{'OK  ' if ok else 'FAIL'} {p['id']}: retrieved ({page.status}; image-only PDF)")
            bad += not ok
            continue
        if not page.ok:
            print(f"COULD NOT RETRIEVE {p['id']}: {page.status} {page.error[:120]}")
            bad += 1
            continue
        text = norm(page.text)
        missing = [s for s in p["spans"] if norm(s) not in text]
        print(f"{'OK  ' if not missing else 'MISS'} {p['id']}: {len(p['spans']) - len(missing)}/{len(p['spans'])} spans")
        for s in missing:
            print("     missing:", s[:100])
        bad += bool(missing)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
