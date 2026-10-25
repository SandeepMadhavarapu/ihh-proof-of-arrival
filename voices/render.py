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

from .anchors import passage_ends, passages, reattach
from .core import EMAIL_RE, FINDING_LABEL, TYPES, UNDER_13, VERDICTS, display_name

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


def _approved(root: str) -> list[dict]:
    path = os.path.join(root, "site-data", "approved-notes.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        notes = json.load(f).get("notes", [])
    return [n for n in notes if isinstance(n, dict) and n.get("status") == "approved"]


def load_approved(root: str) -> list[dict]:
    """Approved notes only. Anything else in the file (pending, rejected, malformed) is ignored."""
    return [n for n in _approved(root) if n.get("type") in TYPES and n.get("kind", "note") == "note"]


def load_findings(root: str) -> list[dict]:
    """Approved Verify findings only (a visitor's verdict on one claim), with a known verdict."""
    return [n for n in _approved(root) if n.get("kind") == "finding" and n.get("verdict") in VERDICTS]


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


def _clip(q: str) -> str:
    return q if len(q) <= 300 else q[:300].rsplit(" ", 1)[0] + "…"


def _note_li(n: dict) -> str:
    return (f'<li class="vv-note"><p class="vv-meta"><span class="vv-type">{E(TYPES[n["type"]])}</span> &middot; '
            f'{E(display_name(n.get("by", "")))} &middot; <time datetime="{E(n.get("date", ""))}">{E(n.get("date", ""))}</time></p>'
            f'<p class="vv-text">{note_text(n.get("text", ""))}</p></li>')


def _quoted(n: dict, current: str) -> str:
    """What the visitor responded to. If the passage has since been reworded, say so."""
    q = norm_ws((n.get("selector") or {}).get("exact") or "") or current
    changed = bool(q) and q not in current
    note = '<p class="vv-was">This comment was left on an earlier wording of the passage.</p>' if changed else ""
    return f'<blockquote class="vv-q">{E(_clip(q))}</blockquote>{note}'


def norm_ws(s: str) -> str:
    return " ".join(html.unescape(s).split())


def annotate(frag: str, page: str, notes: list[dict], cfg: dict) -> tuple[str, str, list[str]]:
    """(fragment with margin markers, per-passage threads and no-JS links, 'Notes on this page'
    section, flagged ids).

    A note goes where its id or quoted words place it (voices/anchors.py). A note that had a
    passage which can no longer be found safely is flagged for the moderator and not shown.
    A legacy note that never had a passage (no id and no quoted words) is not guessed onto one:
    it is listed under "General notes on this page" instead."""
    texts = passages(frag)
    placed, flagged, general = defaultdict(list), [], []
    for n in notes:
        sel = n.get("selector") or {}
        if not n.get("anchor") and not norm_ws(sel.get("exact", "")):
            general.append(n)
            continue
        aid, _ = reattach(n.get("anchor", ""), sel, texts)
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
                        f'comment{"s" if k > 1 else ""} on this section</span></a>')
        href = nojs_href(cfg, page, aid) if on else None
        if href:
            bits.append(f'<a class="vv-nojs vv-ui" href="{E(href)}">Comment on this section</a>')
        return m.group(0) + (f'<span class="vv-rail vv-ui">{"".join(bits)}</span>' if bits else "")

    # Threads go straight after each passage's closing tag, last first so offsets stay valid.
    ends = passage_ends(frag)
    for aid in sorted((a for a in placed if a in ends), key=lambda a: ends[a], reverse=True):
        k = len(placed[aid])
        thread = (f'<details class="vv-thread vv-ui" id="vv-t-{aid}"><summary>{k} visitor comment'
                  f'{"s" if k > 1 else ""} on this section</summary>'
                  f'{_quoted(placed[aid][0], texts[aid])}'
                  f'<ul class="vv-notes plain">{"".join(_note_li(n) for n in placed[aid])}</ul></details>')
        frag = frag[:ends[aid]] + thread + frag[ends[aid]:]
    frag = re.sub(r' id="([a-z0-9-]+)" data-ihh-anchor>', opener, frag)
    if not placed and not general and not on:
        return frag, "", flagged
    items = []
    for aid in (a for a in texts if a in placed):
        items.append(f'<li class="vv-entry" id="vv-{aid}">{_quoted(placed[aid][0], texts[aid])}'
                     f'<ul class="vv-notes">{"".join(_note_li(n) for n in placed[aid])}</ul>'
                     f'<p class="vv-back"><a href="#{aid}">Back to the passage</a></p></li>')
    body = (f'<ol class="vv-list">{"".join(items)}</ol>' if items else
            '<ol class="vv-list"></ol><p class="vv-empty">No notes on this page yet.</p>')
    if general:
        body += ('<h3 class="vv-general-h">General notes on this page</h3>'
                 '<p class="vv-lede">Older notes that were not left on a particular section.</p>'
                 f'<ul class="vv-notes vv-general">{"".join(_note_li(n) for n in general)}</ul>')
    index = f'''
<section class="vv-index" id="notes" aria-labelledby="notes-h">
<h2 id="notes-h">Notes on this page</h2>
<p class="vv-lede">Notes left by visitors, in their own words. A curator reads every note before it
appears. Notes are not checked facts; the page above is.</p>
{body}
</section>'''
    return frag, index, flagged


def findings_block(claim_id: str, claim_text: str, findings: list[dict]) -> str:
    """Approved visitor findings on one Verify claim: a tally that expands to the comments.
    Findings are matched by the claim's id; one left on an earlier wording says so."""
    mine = [f for f in findings if f.get("anchor") == claim_id]
    if not mine:
        return ""
    counts = [(v, sum(1 for f in mine if f["verdict"] == v)) for v in VERDICTS]
    tally = " &middot; ".join(f"{k} {E(VERDICTS[v])}" for v, k in counts if k)
    current = norm_ws(re.sub(r"<[^>]+>", "", claim_text))
    lis = "".join(
        f'<li class="vv-note"><p class="vv-meta"><span class="vv-type">{E(FINDING_LABEL)}: {E(VERDICTS[f["verdict"]])}</span> &middot; '
        f'{E(display_name(f.get("by", "")))} &middot; <time datetime="{E(f.get("date", ""))}">{E(f.get("date", ""))}</time></p>'
        + (f'<p class="vv-text">{note_text(f["text"])}</p>' if f.get("text") else "")
        + ('<p class="vv-was">Shared on an earlier wording of this claim.</p>'
           if norm_ws((f.get("selector") or {}).get("exact", "")) not in ("", current) else "")
        + "</li>" for f in mine)
    k = len(mine)
    return (f'\n    <details class="vv-thread vv-findings" id="vv-t-{E(claim_id)}"><summary>{k} visitor finding'
            f'{"s" if k > 1 else ""}: {tally}</summary><ul class="vv-notes plain">{lis}</ul></details>')


def under13() -> str:
    return E(UNDER_13)
