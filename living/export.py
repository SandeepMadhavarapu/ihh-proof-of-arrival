"""Export approved content as copy-paste HTML for WordPress. No plugin needed.

    python living/run.py export-wp

Each inductee's page block is already inductees/<slug>/copy.html (paste into ONE "Custom HTML"
block; see handover/INSTALL.md); approved facts appear in it with their Verified badge.
This command writes the "New at the Museum" list as one more self-contained block, built only
from the committed, approved feed site-data/new-at-the-museum.json.
"""
from __future__ import annotations

import html
import json

from .config import CACHE, ROOT

E = html.escape
STYLE = """.ihh-new{--ink:#1a1714;--mut:#56514a;--rule:#d9d4cb;font:1rem/1.6 Georgia,serif;color:var(--ink);max-width:46rem}
.ihh-new ol{list-style:none;margin:0;padding:0}.ihh-new li{border-top:1px solid var(--rule);padding:1rem 0}
.ihh-new .m,.ihh-new .s{font:.85rem/1.5 system-ui,sans-serif;color:var(--mut);margin:0 0 .3rem;overflow-wrap:anywhere}
.ihh-new p{margin:0 0 .4rem}.ihh-new a{color:var(--ink)}
@media (prefers-color-scheme:dark){.ihh-new{--ink:#ece7df;--mut:#a7a096;--rule:#39352d}}"""


def wordpress_block() -> str:
    feed = json.loads((ROOT / "site-data" / "new-at-the-museum.json").read_text(encoding="utf-8"))
    entries = sorted(feed.get("entries", []), key=lambda e: (e["date"], e["id"]), reverse=True)
    if entries:
        items = "\n".join(
            f'<li><p class="m">{E(e["date"])} &middot; {E(e["slug"].title())}</p><p>{E(e["sentence"])}</p>'
            f'<p class="s">Source{"s" if len(e["sources"]) > 1 else ""}: '
            + "; ".join(f'<a href="{E(s["url"])}" rel="noopener">{E(s["title"])}</a> ({E(s["institution"])})' for s in e["sources"])
            + "</p></li>" for e in entries)
        body = f"<ol>\n{items}\n</ol>"
    else:
        body = "<p>Nothing new yet. When our team has checked a new discovery against its original source and approved it, it will appear here with that source.</p>"
    return (f"<!-- New at the Museum - paste into ONE WordPress 'Custom HTML' block. Generated from approved entries only. -->\n"
            f'<div class="ihh-new"><style>{STYLE}</style>\n<h2>New at the Museum</h2>\n{body}\n</div>\n')


def write() -> str:
    out = CACHE / "exports" / "new-at-the-museum-wordpress.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(wordpress_block(), encoding="utf-8", newline="\n")
    return str(out)
