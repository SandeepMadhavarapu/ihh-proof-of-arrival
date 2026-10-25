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
  unchecked its page is not in the built site (not built yet, or not published); left alone

A moved or fuzzy item gets its new id, and the old one is kept in `anchor_history`. Nothing is
ever deleted, and a flagged item is never moved. Pages are read from the built site/ folder,
so build the site first; an item whose page is missing is reported as unchecked and not touched.
With --write only items whose anchor or status actually changed are rewritten, and every one of
those rewrites gets a line in the store's audit log.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .anchors import norm, passages, reattach
from .claims import claim_texts
from .core import Store, now

ROOT = Path(__file__).resolve().parents[1]


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
    texts = page_texts(site, item.get("page", ""))
    if not texts:
        return "unchecked", anchor            # never flag a note just because its page is not built
    aid, how = reattach(anchor, sel, texts)
    return (how, aid) if aid else ("flagged", anchor)


def migrate(items: list[dict], site: Path, claims: dict[str, str]) -> list[tuple[dict, str, str, str]]:
    """[(item, old anchor, new anchor, status)] for every item; items are updated in place.
    An unchecked item is left exactly as it was."""
    out = []
    for item in items:
        status, new = check(item, site, claims)
        old = item.get("anchor", "")
        if status == "unchecked":
            out.append((item, old, old, status))
            continue
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
    claims = claim_texts()
    if a.store:
        store = Store(a.store)
        items = store.all()
    else:
        data = json.loads(a.approved.read_text(encoding="utf-8"))
        items = data.get("notes", [])
    before = {id(i): (i.get("anchor", ""), i.get("anchor_status")) for i in items}
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
        changed = 0
        for item, old, new, status in results:
            if (item.get("anchor", ""), item.get("anchor_status")) == before[id(item)]:
                continue                      # nothing changed: do not rewrite the file
            store._write(item)
            changed += 1
            what = f"re-anchored ({status})" if status in ("moved", "fuzzy") and new != old else f"anchor status: {status}"
            store.audit("migrate_anchors", what, item["id"], item["status"], item["status"],
                        f"{old} -> {new}" if new != old else f"anchor {old or '-'}")
        print(f"{changed} item(s) rewritten, each with an audit line")
    else:
        a.approved.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
