"""Check every stored note and finding against the current pages, and re-anchor what has moved.

    python -m voices.migrate_anchors --store <moderation folder>            # dry run: report only
    python -m voices.migrate_anchors --store <moderation folder> --write    # apply, with audit lines
    python -m voices.migrate_anchors --approved site-data/approved-notes.json [--write]

Run it after content edits, and once on any store written before notes carried an anchor.
For each item it records `anchor_status`:

  exact     its passage id still exists and still contains its quoted words
  moved     the passage was edited; its quoted words were found in exactly one other passage
  fuzzy     the closest passage is at least 85% similar to its quoted words
  general   a legacy note that never had a passage or quoted words; shown under
            "General notes on this page", never guessed onto a passage
  flagged   it had a passage that can no longer be found safely; not shown, a moderator decides

A moved or fuzzy item gets its new id, and the old one is kept in `anchor_history`. Nothing is
ever deleted, and a flagged item is never moved. Pages are read from the built site/ folder,
so build the site first.
"""
from __future__ import annotations

import argparse
import importlib.util
import html
import json
import re
import sys
from pathlib import Path

from .anchors import norm, passages, reattach
from .core import Store, now

ROOT = Path(__file__).resolve().parents[1]


def claim_ids(root: Path = ROOT) -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("ihh_gen", root / "site-src" / "gen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {cl["id"]: norm(html.unescape(re.sub(r"<[^>]+>", "", cl["text"]))) for c in mod.CASES for cl in c["claims"]}


def page_texts(site: Path, page: str) -> dict[str, str]:
    path = site / f"{page}.html"
    return passages(path.read_text(encoding="utf-8")) if re.fullmatch(r"[a-z0-9-]+", page or "") and path.is_file() else {}


def check(item: dict, site: Path, claims: dict[str, str]) -> tuple[str, str]:
    """(anchor_status, anchor it should have now)."""
    kind, anchor = item.get("kind", "note"), item.get("anchor", "")
    if kind in ("claim", "finding"):
        return ("exact", anchor) if anchor in claims else ("flagged", anchor)
    if kind != "note":
        return "general", ""                 # tips are about an inductee, not a passage
    sel = item.get("selector") or {}
    if not anchor and not norm(sel.get("exact", "")):
        return "general", ""
    aid, how = reattach(anchor, sel, page_texts(site, item.get("page", "")))
    return (how, aid) if aid else ("flagged", anchor)


def migrate(items: list[dict], site: Path, claims: dict[str, str]) -> list[tuple[dict, str, str, str]]:
    """[(item, old anchor, new anchor, status)] for every item; items are updated in place."""
    out = []
    for item in items:
        status, new = check(item, site, claims)
        old = item.get("anchor", "")
        if status in ("moved", "fuzzy") and new != old:
            item.setdefault("anchor_history", []).append({"from": old, "to": new, "how": status, "at": now()})
            item["anchor"] = new
        item["anchor_status"] = status
        out.append((item, old, new, status))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--store", type=Path, help="a moderation folder (items/ and audit.log.jsonl)")
    src.add_argument("--approved", type=Path, help="site-data/approved-notes.json")
    ap.add_argument("--site", type=Path, default=ROOT / "site", help="the built site to read passages from")
    ap.add_argument("--write", action="store_true", help="apply the changes (default: report only)")
    a = ap.parse_args()
    claims = claim_ids()
    if a.store:
        store = Store(a.store)
        items = store.all()
    else:
        data = json.loads(a.approved.read_text(encoding="utf-8"))
        items = data.get("notes", [])
    results = migrate(items, a.site, claims)
    counts: dict[str, int] = {}
    for item, old, new, status in results:
        counts[status] = counts.get(status, 0) + 1
        if status != "exact":
            move = f" {old or '-'} -> {new}" if status in ("moved", "fuzzy") and new != old else ""
            print(f"{status:8} {item.get('id', '?')} on {item.get('page', '?')}{move}")
    print("summary: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "nothing to check"))
    if not a.write:
        print("dry run: nothing written (add --write to apply)")
        return 0
    if a.store:
        for item, old, new, status in results:
            store._write(item)
            if status in ("moved", "fuzzy") and new != old:
                store.audit("migrate_anchors", f"re-anchored ({status})", item["id"], item["status"], item["status"], f"{old} -> {new}")
    else:
        a.approved.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
