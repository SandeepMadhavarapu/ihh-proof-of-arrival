"""Send a visitor's "I know more" / "Something looks wrong" (with a source) to the Living Museum.

The visitor's words never become copy. The proposal created here is kind "tip": its sentence and
claim are empty, the visitor's text and source are kept in `finder` (which the verifier never
sees), and its evidence is the cited URL with NO span. The verifier skips tips
(living/verifier.py), and the review queue cannot approve one: a curator reads the source,
and if it holds up, writes a normal fact proposal with an exact span from that source, which
then goes through the same five gates as every other fact.

    python -m voices.bridge <item.json> [--store living/proposals]   # by hand, for a curator
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from living.proposals import Evidence, Proposal, Store as LivingStore

URL = re.compile(r"https?://[^\s<>\"']+")


def eligible(item: dict) -> bool:
    return bool(item.get("source")) and (item["type"] in ("more", "wrong") or item["kind"] == "tip")


def to_living(item: dict, store: LivingStore, slug: str = "") -> str:
    """Create the tip proposal; return its id ('' if the item is not eligible)."""
    if not eligible(item):
        return ""
    urls = URL.findall(item["source"])
    slug = slug or item.get("inductee") or (item["page"] if item["page"] != "verify" else "")
    p = Proposal(
        id=store.next_id(), kind="tip", slug=slug or "unknown", section="", sentence="", claim="",
        evidence=[Evidence(url=u, span="", retrieved_by="visitor") for u in urls[:3]],
        finder={"mode": "visitor-tip", "moderation_item": item["id"], "type": item["type"],
                "where": item.get("anchor", ""), "visitor_text": item["text"],
                "visitor_source": item["source"],
                "note": "Visitor tip. Not copy. A curator must find an exact span in a trusted "
                        "source and file a fact proposal before anything can be published."},
        reasons=["Visitor tip: awaiting a curator-supplied span; the verifier does not run on tips."],
    )
    store.create(p, "visitor-voices", f"tip from moderation item {item['id']}")
    return p.id


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("item", type=Path)
    ap.add_argument("--store", type=Path, default=None, help="Living Museum proposals folder")
    a = ap.parse_args()
    item = json.loads(a.item.read_text(encoding="utf-8"))
    pid = to_living(item, LivingStore(a.store) if a.store else LivingStore())
    print(pid or "not eligible: needs a source and type 'I know more' or 'Something looks wrong'")
    return 0 if pid else 1


if __name__ == "__main__":
    sys.exit(main())
