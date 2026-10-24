"""Build-time rendering of approved notes, and the adapter settings pages carry.

Used by tools/build_site_pages.py (profile pages) and site-src/gen.py (the Verify page).
Everything a visitor wrote is escaped here; emails are redacted; nothing becomes a link.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import quote

from .anchors import passages, reattach
from .core import EMAIL_RE, TYPES, UNDER_13, display_name

E = html.escape
# What site/ may be built with. "demo" exists only inside voices/demo_server.py's own build
# folder (voices/.demo/), so a production build can never carry the demo adapter.
PRODUCTION_ADAPTERS = ("none", "wordpress", "email")


def load_config(root: str, override: dict | None = None) -> dict:
    if override is not None:
        return override
    path = os.path.join(root, "site-data", "visitor-voices.json")
    cfg = {"adapter": "none"}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    a = cfg.get("adapter")
    if a not in PRODUCTION_ADAPTERS:
        sys.exit(f"{path}: adapter must be one of {', '.join(PRODUCTION_ADAPTERS)} (got {a!r})")
    if a == "wordpress" and not re.fullmatch(r"https://[^\s\"'<>]+", cfg.get("wordpress", {}).get("site", "")):
        sys.exit(f"{path}: wordpress.site must be the https:// address of the WordPress site")
    if a == "email" and not EMAIL_RE.fullmatch(cfg.get("email", {}).get("address", "")):
        sys.exit(f"{path}: email.address must be an email address")
    return cfg


def load_approved(root: str) -> list[dict]:
    """Approved notes only. Anything else in the file (pending, rejected, malformed) is ignored."""
    path = os.path.join(root, "site-data", "approved-notes.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        notes = json.load(f).get("notes", [])
    return [n for n in notes if isinstance(n, dict) and n.get("status") == "approved"
            and n.get("type") in TYPES and n.get("kind", "note") == "note"]


def page_attrs(cfg: dict, page: str) -> str:
    a = cfg["adapter"]
    out = f' data-ihh-notes="{E(a)}" data-ihh-page="{E(page)}"'
    if a == "wordpress":
        wp = cfg["wordpress"]
        out += f' data-ihh-wp="{E(wp["site"])}" data-ihh-post="{E(str(wp.get("post_ids", {}).get(page, "")))}"'
    elif a == "email":
        out += f' data-ihh-email="{E(cfg["email"]["address"])}"'
    elif a == "demo":
        out += ' data-ihh-api="/voices/api"'
    return out


def nojs_href(cfg: dict, page: str, anchor: str) -> str | None:
    a = cfg["adapter"]
    if a == "demo":
        return f"/voices/form?page={quote(page)}&passage={quote(anchor)}"
    if a == "email":
        return f"mailto:{cfg['email']['address']}?subject=" + quote(f"Note on {page}, passage {anchor}")
    if a == "wordpress":
        post = cfg["wordpress"].get("post_ids", {}).get(page)
        return f"{cfg['wordpress']['site']}/?p={int(post)}&ihh_passage={quote(anchor)}#respond" if post else None
    return None


def note_text(s: str) -> str:
    return E(EMAIL_RE.sub("[email removed]", s)).replace("\n", "<br>")


def annotate(frag: str, page: str, notes: list[dict], cfg: dict) -> tuple[str, str, list[str]]:
    """(fragment with margin markers and no-JS links, 'Notes on this page' section, flagged ids)."""
    texts = passages(frag)
    placed, flagged = defaultdict(list), []
    for n in notes:
        aid, _ = reattach(n.get("anchor", ""), n.get("selector") or {}, texts)
        if aid is None:
            flagged.append(n.get("id", "?"))
        else:
            placed[aid].append(n)
    on = cfg["adapter"] != "none"

    def opener(m):
        aid, bits = m.group(1), []
        if aid in placed:
            k = len(placed[aid])
            bits.append(f'<a class="vv-mark vv-ui" href="#vv-{aid}">{k}<span class="vv-sr"> visitor '
                        f'note{"s" if k > 1 else ""} on this passage</span></a>')
        href = nojs_href(cfg, page, aid) if on else None
        if href:
            bits.append(f'<a class="vv-nojs vv-ui" href="{E(href)}">Add a note<span class="vv-sr"> on this passage</span></a>')
        return m.group(0) + (f'<span class="vv-rail vv-ui">{"".join(bits)}</span>' if bits else "")

    frag = re.sub(r' id="([a-z0-9-]+)" data-ihh-anchor>', opener, frag)
    if not placed and not on:
        return frag, "", flagged
    items = []
    for aid in (a for a in texts if a in placed):
        notes_html = "".join(
            f'<li class="vv-note"><p class="vv-meta"><span class="vv-type">{E(TYPES[n["type"]])}</span> &middot; '
            f'{E(display_name(n.get("by", "")))} &middot; <time datetime="{E(n.get("date", ""))}">{E(n.get("date", ""))}</time></p>'
            f'<p class="vv-text">{note_text(n.get("text", ""))}</p></li>' for n in placed[aid])
        quoted = (placed[aid][0].get("selector") or {}).get("exact") or texts[aid]
        items.append(f'<li class="vv-entry" id="vv-{aid}"><blockquote class="vv-q">{E(quoted if len(quoted) <= 300 else quoted[:300].rsplit(" ", 1)[0] + "…")}</blockquote>'
                     f'<ul class="vv-notes">{notes_html}</ul><p class="vv-back"><a href="#{aid}">Back to the passage</a></p></li>')
    body = (f'<ol class="vv-list">{"".join(items)}</ol>' if items else
            '<ol class="vv-list"></ol><p class="vv-empty">No notes on this page yet.</p>')
    index = f'''
<section class="vv-index" id="notes" aria-labelledby="notes-h">
<h2 id="notes-h">Notes on this page</h2>
<p class="vv-lede">Notes left by visitors, in their own words. A curator reads every note before it
appears. Notes are not checked facts; the page above is.</p>
{body}
</section>'''
    return frag, index, flagged


def under13() -> str:
    return E(UNDER_13)
