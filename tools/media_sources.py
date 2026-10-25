#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interviews and media from other institutions: one data file per inductee, drawn on its page.

    site-data/sources/<slug>.json       {"sources": [ {...}, ... ]}   (format: site-data/sources/README.md)
    python3 tools/media_sources.py      # check every file without building the site

tools/build_site_pages.py calls render() for every published profile. Entries marked
"placeholder": true appear only in a preview build (--preview, or the local demo), never on the
published pages. A file that breaks the
format stops the build with the reason, so a typo can never quietly publish a bad entry.

Permission decides what the page does with a source:
  granted     embedded, but only after the visitor presses Play (until then the page makes no
              request to the host), and only from a host in EMBED_HOSTS; otherwise a link
  link-only   a link to the holder's own page, never embedded or hosted here
  pending     the same as link-only until the holder agrees
"""
import html, json, os, re, sys
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape

PERMISSIONS = ("pending", "granted", "link-only")
KINDS = {"video": "Video", "audio": "Audio", "interview": "Interview", "oral-history": "Oral history",
         "article": "Article", "document": "Document"}
FIELDS = {"id", "title", "kind", "creator", "creator_role", "institution", "date", "url", "embed_url",
          "permission", "credit", "description", "placeholder"}
REQUIRED = ("id", "title", "kind", "institution", "url", "permission")
# Players we will load inside the page, once a visitor asks and permission is granted.
EMBED_HOSTS = ("www.youtube-nocookie.com", "player.vimeo.com", "archive.org", "www.loc.gov", "www.c-span.org")
TODO = re.compile(r"\bTODO\b")
DATE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?")


class SourceError(ValueError):
    pass


def check(entry, where):
    """Raise SourceError naming the file, entry and field, or return the entry unchanged."""
    if not isinstance(entry, dict):
        raise SourceError(f"{where}: each source must be an object")
    sid = entry.get("id", "?")
    bad = sorted(set(entry) - FIELDS)
    if bad:
        raise SourceError(f"{where} [{sid}]: unknown field(s) {', '.join(bad)} (allowed: {', '.join(sorted(FIELDS))})")
    for k, v in entry.items():
        if k == "placeholder":
            if not isinstance(v, bool):
                raise SourceError(f"{where} [{sid}]: placeholder must be true or false")
        elif not isinstance(v, str):
            raise SourceError(f"{where} [{sid}]: '{k}' must be text in quotes, e.g. \"{k}\": \"...\" (got {type(v).__name__})")
    for k in REQUIRED:
        if not str(entry.get(k) or "").strip():
            raise SourceError(f"{where} [{sid}]: '{k}' is required")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,80}", sid):
        raise SourceError(f"{where} [{sid}]: id must be lowercase letters, digits and hyphens")
    if entry["permission"] not in PERMISSIONS:
        raise SourceError(f"{where} [{sid}]: permission must be one of {', '.join(PERMISSIONS)}")
    if entry["kind"] not in KINDS:
        raise SourceError(f"{where} [{sid}]: kind must be one of {', '.join(KINDS)}")
    placeholder = entry.get("placeholder") is True
    for k, v in entry.items():
        if isinstance(v, str) and TODO.search(v) and not placeholder:
            raise SourceError(f"{where} [{sid}]: '{k}' still says TODO; set \"placeholder\": true or fill it in")
    url = entry["url"]
    if not (url == "TODO" and placeholder) and not re.fullmatch(r"https://[^\s\"'<>]+", url):
        raise SourceError(f"{where} [{sid}]: url must be the https:// address of the holder's page")
    emb = entry.get("embed_url") or ""
    if emb and not (emb == "TODO" and placeholder):
        if not re.fullmatch(r"https://[^\s\"'<>]+", emb) or urlsplit(emb).hostname not in EMBED_HOSTS:
            raise SourceError(f"{where} [{sid}]: embed_url must be https:// on one of {', '.join(EMBED_HOSTS)}")
    date = entry.get("date") or ""
    if date and not (date == "TODO" and placeholder) and not DATE.fullmatch(date):
        raise SourceError(f"{where} [{sid}]: date must be YYYY, YYYY-MM or YYYY-MM-DD")
    return entry


def load(root, slug):
    """The checked sources for one inductee ([] if it has no file yet)."""
    path = os.path.join(root, "site-data", "sources", f"{slug}.json")
    if not os.path.exists(path):
        return []
    where = os.path.relpath(path, root)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise SourceError(f"{where}: not valid JSON ({e})")
    items = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise SourceError(f"{where}: must be an object with a \"sources\" list")
    seen = set()
    for entry in items:
        check(entry, where)
        if entry["id"] in seen:
            raise SourceError(f"{where} [{entry['id']}]: id used twice")
        seen.add(entry["id"])
    return items


def _host(url):
    return urlsplit(url).hostname or ""


def item_html(s):
    placeholder = s.get("placeholder") is True
    inst, perm, url = s["institution"], s["permission"], s["url"]
    attr = " &middot; ".join(E(x) for x in (
        (s.get("creator", "") + (f" ({s['creator_role']})" if s.get("creator_role") else "")).strip(),
        inst, s.get("date", "")) if x)
    linkable = url != "TODO"
    link = (f'<a href="{E(url)}" rel="noopener">View at {E(inst)}</a>' if linkable else
            '<span class="ms-todo">Link to the holder&rsquo;s page: TODO</span>')
    emb = s.get("embed_url") or ""
    player = ""
    if perm == "granted":
        if emb and emb != "TODO":
            player = (f'<div class="ms-embed" data-embed="{E(emb)}" data-title="{E(s["title"])}">'
                      f'<a class="btn ms-play" href="{E(url if linkable else emb)}" rel="noopener">Play the recording</a>'
                      f'<p class="ms-note">Playing loads it from {E(_host(emb))}, which may set cookies. '
                      f'Nothing loads until you press Play.</p></div>')
        elif placeholder:
            player = '<div class="ms-embed ms-embed-ph"><p>The embedded player will appear here (embed_url: TODO).</p></div>'
    label = {"granted": f"Shown with permission of {E(inst)}.",
             "link-only": f"Link only: the recording stays with {E(inst)}.",
             "pending": "Permission requested. Link only until the holder agrees."}[perm]
    credit = f'<p class="ms-credit">Credit: {E(s["credit"])}</p>' if s.get("credit") else ""
    desc = f'<p class="ms-desc">{E(s["description"])}</p>' if s.get("description") else ""
    badge = '<span class="ms-ph">Placeholder &mdash; not a real source</span>' if placeholder else ""
    return (f'<li class="ms-item ms-{perm}{" ms-placeholder" if placeholder else ""}" id="src-{E(s["id"])}" '
            f'data-permission="{perm}">\n'
            f'  <p class="ms-kind">{E(KINDS[s["kind"]])}{badge}</p>\n'
            f'  <h3 class="ms-title">{E(s["title"])}</h3>\n'
            + (f'  <p class="ms-attr">{attr}</p>\n' if attr else "")
            + f'  {desc}{player}\n  <p class="ms-perm">{label} {link}</p>{credit}\n</li>')


def render(root, slug, preview=False):
    """The section for one profile page. Always drawn, so the structure is visible on every page.
    Placeholder entries (layout examples full of TODO) are drawn only in a preview build: the local
    demo, or `python3 tools/build_site_pages.py --preview`. The published site never shows them."""
    items = [s for s in load(root, slug) if preview or s.get("placeholder") is not True]
    body = ('<ul class="ms-list plain">\n' + "\n".join(item_html(s) for s in items) + "\n</ul>") if items else (
        '<p class="ms-empty">No outside interviews or media have been added for this person yet.</p>')
    return f'''
<section class="media-src" id="interviews-and-media" aria-labelledby="ms-h">
<h2 id="ms-h">Interviews and media from other institutions</h2>
<p class="ms-lede">First-person recordings and expert perspectives held by other museums, archives
and media organisations. Each one links to the institution that holds it. A recording is embedded
here only when its holder has given permission.</p>
{body}
</section>'''


# The WordPress package's version: no JavaScript is allowed in that block, so every source is a
# link to its holder, even when permission is granted (an editor can add the holder's own embed
# code in WordPress once permission is on file). Placeholders never appear. Between the markers so
# tools/build_site_pages.py can swap in the site's own version.
WP_START, WP_END = "<!-- ms:start -->", "<!-- ms:end -->"
WP_CSS = (".ihh-profile ol.media{list-style:none;margin:1.4rem 0 0;padding:0;display:grid;"
          "grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:1.6rem}\n"
          ".ihh-profile .ms-wp-item{border-top:2px solid var(--ink);padding-top:.9rem}\n")


def render_wp(root, slug):
    """(HTML for the WordPress block, Markdown for copy-full.md, CSS); empty when there is nothing."""
    items = [s for s in load(root, slug) if s.get("placeholder") is not True]
    if not items:
        return "", "", ""
    perm = {"granted": "Shown with permission of {i}.", "link-only": "Link only: the recording stays with {i}.",
            "pending": "Permission requested. Link only until the holder agrees."}
    lis, md = [], []
    for s in items:
        who = ", ".join(x for x in ((s.get("creator", "") + (f" ({s['creator_role']})" if s.get("creator_role") else "")).strip(),
                                     s["institution"], s.get("date", "")) if x)
        lis.append(f'''    <li class="ms-wp-item">
      <p class="kindmark">{E(KINDS[s["kind"]])}</p>
      <h3 class="src-h">{E(s["title"])}</h3>
      {f'<p class="gloss">{E(s["description"])}</p>' if s.get("description") else ""}
      <p class="meta">{E(who)}</p>
      <p class="rights">{E(perm[s["permission"]].format(i=s["institution"]))} <a href="{E(s["url"])}" rel="noopener">View at {E(s["institution"])}</a></p>
    </li>''')
        md.append(f"**{s['title']}**\n\n" + (f"{s['description']}\n\n" if s.get("description") else "")
                  + f"{who}\n<{s['url']}>\n{perm[s['permission']].format(i=s['institution'])}\n")
    html_out = (f'''{WP_START}
<div class="wide">
<h2>Interviews and media from other institutions</h2>
<p class="gloss">First-person recordings and expert perspectives held by other museums, archives and
media organisations. Each links to the institution that holds it.</p>
<ol class="media">
{chr(10).join(lis)}
</ol>
</div>
{WP_END}''')
    return html_out, "## Interviews and media from other institutions\n\n" + "\n".join(md), WP_CSS


def main():
    folder = os.path.join(ROOT, "site-data", "sources")
    files = sorted(f for f in os.listdir(folder) if f.endswith(".json")) if os.path.isdir(folder) else []
    total = 0
    for f in files:
        try:
            n = len(load(ROOT, f[:-5]))
        except SourceError as e:
            sys.exit(f"ERROR {e}")
        total += n
        print(f"site-data/sources/{f}: {n} source(s) OK")
    print(f"{total} source(s) in {len(files)} file(s)")


if __name__ == "__main__":
    main()
