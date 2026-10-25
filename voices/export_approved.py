"""Write approved margin notes and Verify findings to site-data/approved-notes.json, for a static build.

    python -m voices.export_approved --store <moderation folder> [--out site-data/approved-notes.json]

Only items a person approved are written, and only their public fields (never an email, never
a source link). The --store argument is required, so the demo's notes are never exported by
accident. Commit the result through a reviewed pull request; tools/build_site_pages.py then draws
the notes, re-attaching each one to its passage or reporting it as flagged.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import Store, public

ROOT = Path(__file__).resolve().parents[1]
NOTE = ("Visitor notes a curator has approved. Only entries with status approved are ever drawn on the "
        "site. Written by voices/export_approved.py from the moderation store, and changed only through "
        "a reviewed pull request. Never put visitor text in inductees/*/copy.md.")


def export(store: Store) -> dict:
    notes = [dict(public(i), status="approved") for i in store.all()
             if i["status"] == "approved" and i["kind"] in ("note", "finding")]
    return {"_note": NOTE, "notes": notes}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--store", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "site-data" / "approved-notes.json")
    a = ap.parse_args()
    data = export(Store(a.store))
    a.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{a.out}: {len(data['notes'])} approved note(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
