#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one inductee profile for WordPress from its folder.

    python3 tools/build_profile.py inductees/lamarr
    python3 tools/build_profile.py --all

Reads   <folder>/copy.md, <folder>/media-manifest.csv, <folder>/media/
Writes  <folder>/copy.html      paste into ONE WordPress "Custom HTML" block
        <folder>/preview.html   the same block inside a hostile stand-in theme
        <folder>/copy-full.md   the whole page as Markdown, for editors without Custom HTML
        <folder>/media/web/     1600px JPEG copies of every image the page uses

The format of copy.md is documented in templates/copy-template.md.
"""
import csv, hashlib, html, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import media_sources  # noqa: E402
CSS = open(os.path.join(ROOT, "templates", "profile.css"), encoding="utf-8").read()
IMG_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
# Added only to profiles that carry approved Living Museum facts, so other pages stay byte-identical.
BADGE_CSS = (".ihh-profile .vbadge{display:inline-block;margin:.15rem 0 0;padding:.05rem .45rem;"
             "font:400 .76rem/1.6 system-ui,sans-serif;color:var(--mut);border:1px solid var(--rule);"
             "border-radius:2px;white-space:normal}\n"
             ".ihh-profile .vbadge a{color:var(--ink)}\n")
E = html.escape


def inline(s):
    """The small subset of Markdown copy.md uses inside paragraphs."""
    s = E(" ".join(s.split()), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', s)
    return s


def slugify(s, n=24):
    s = re.sub(r"[^a-z0-9]+", "-", html.unescape(s).lower()).strip("-")
    return s[:n].rstrip("-") or "section"


class Anchors:
    """Stable passage ids for Margin Notes: section slug + a short hash of the passage's text.
    The same text always gets the same id, so ids survive rebuilds; an edited passage gets a
    new id, and voices/anchors.py re-attaches notes to it by their quoted text instead."""

    def __init__(self, slug):
        self.slug, self.seen = slug, {}

    def __call__(self, section, rendered):
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", rendered)).split())
        base = f"{self.slug}-{slugify(section)}-{hashlib.sha1(text.encode('utf-8')).hexdigest()[:6]}"
        n = self.seen[base] = self.seen.get(base, 0) + 1
        return f' id="{base if n == 1 else f"{base}-{n}"}" data-ihh-anchor'


def field(md, label):
    m = re.search(r"\*\*" + re.escape(label) + r":\*\*\n(.+?)(?:\n\n|\Z)", md, re.S)
    return m.group(1).strip() if m else ""


def parse(md):
    name = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    parts = re.split(r"^---\s*$", md, flags=re.M)
    if len(parts) < 3:
        sys.exit("copy.md needs three parts separated by lines of ---: head, story, extras")
    head, story, extras = parts[0], parts[1], "---".join(parts[2:])
    sections = []
    for chunk in re.split(r"^## ", story, flags=re.M)[1:]:
        title, _, body = chunk.partition("\n")
        paras = [p for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
        sections.append((title.strip(), paras))
    quote = re.search(r"\*\*Quotation:\*\*\n((?:>.*\n?)+)", extras)
    qtext = " ".join(l.lstrip("> ").strip() for l in quote.group(1).splitlines()) if quote else ""
    qblock = re.search(r"## Discussion questions\n(.*?)(?=\n## |\Z)", extras, re.S)
    questions = re.findall(r"^\d+\.\s+(.+?)(?=\n\d+\.|\Z)", qblock.group(1).strip(), re.M | re.S) if qblock else []
    ablock = re.search(r"## Activities\n(.*?)(?=\n## |\Z)", extras, re.S)
    activities = re.findall(r"\*\*\d+\.\s*(.+?)\*\*\s*(.+?)(?=\n\*\*\d+\.|\Z)", ablock.group(1), re.S) if ablock else []
    return dict(
        name=name,
        opening=field(head, "Opening line"),
        anchor=field(head, "Anchor item"),
        standfirst=field(head, "Standfirst"),
        spot_item=field(extras, "Spotlight item"),
        spot_intro=field(extras, "Spotlight introduction"),
        spot_text=re.search(r"\*\*Spotlight excerpt:\*\*\n((?:>.*\n?)+)", extras),
        quote=qtext,
        quote_source=field(extras, "Quotation source"),
        sections=sections,
        questions=questions,
        activities=activities,
        compiled=field(extras, "Compiled by"),
    )


def web_copy(folder, filename):
    """1600px JPEG for the page; originals stay untouched in media/."""
    src = os.path.join(folder, "media", filename)
    out_name = os.path.splitext(filename)[0] + ".jpg"
    out = os.path.join(folder, "media", "web", out_name)
    if not os.path.exists(src):
        # Full-resolution originals deliberately stay outside Git. A fresh checkout
        # builds from the reviewed web derivative without recompressing it.
        if os.path.isfile(out) and os.path.getsize(out) > 0:
            return "media/web/" + out_name
        return None
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        cmd = (["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", "1600", src, "--out", out]
               if sys.platform == "darwin" else
               ["convert", src + "[0]", "-resize", "1600x1600>", "-quality", "82", out])
        subprocess.run(cmd, check=True, capture_output=True)
    return "media/web/" + out_name


VERIFIED = re.compile(r"\s*\{verified:(LM-\d+)\}\s*$")


def load_verified(folder):
    """Approved Living Museum facts for this profile (written only by living/publisher.py)."""
    path = os.path.join(folder, "verified-facts.json")
    if not os.path.exists(path):
        return {}
    import json
    with open(path, encoding="utf-8") as fh:
        return {f["id"]: f for f in json.load(fh)["facts"]}


def checked(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m - 1]} {y}"


def build(folder):
    folder = os.path.abspath(folder)
    md = open(os.path.join(folder, "copy.md"), encoding="utf-8").read()
    verified = load_verified(folder)
    cited = {n for f in verified.values() for n in f["source_items"]}
    rows = list(csv.DictReader(open(os.path.join(folder, "media-manifest.csv"), encoding="utf-8")))
    shown = [r for r in rows if not r["recommendation"].upper().startswith("DROP")]
    p = parse(md)
    aid = Anchors(os.path.basename(folder))
    by_no = {r["item_no"]: r for r in rows}

    for r in shown:
        r["_web"] = web_copy(folder, r["filename"]) if r["filename"].lower().endswith(IMG_EXT) else None

    anchor = by_no.get(p["anchor"])
    if not anchor or not anchor.get("_web"):
        sys.exit(f"{folder}: **Anchor item:** must name a manifest row whose image is in media/")

    def credit(r):
        return (f'{E(r["required_credit"])}. Rights, in the institution&rsquo;s words: '
                f'&ldquo;{E(r["rights_statement_verbatim"])}&rdquo; '
                f'<a href="{E(r["stable_item_url"])}" rel="noopener">View the record</a>.')

    def source_item(r):
        if r.get("_web"):
            thumb = f'<img class="th" src="{r["_web"]}" alt="{E(r["alt_text"])}" loading="lazy" decoding="async">'
        else:
            thumb = f'<p class="kindmark">{E(r["kind"])}</p>'
        dup = (f'<p class="dupe">{E(r["duplicate_or_original"])}</p>'
               if r["duplicate_or_original"].upper().startswith("DUPLICATE") else "")
        link = (f'<a href="{E(r["stable_item_url"])}" rel="noopener">{E(r["institution"])}</a>'
                if r["stable_item_url"] else E(r["institution"]))
        anchor = f' id="src-{r["item_no"]}"' if r["item_no"] in cited else ""
        return f'''    <li class="src-item"{anchor}>
      {thumb}
      <h3 class="src-h">{E(r["title"])}</h3>
      <p class="gloss"{aid("sources", E(r["gloss"]))}>{E(r["gloss"])}</p>
      {dup}
      <p class="meta">{E(r["creator"])} &middot; {E(r["date_created"])} &middot; {link}</p>
      <p class="rights"><b>Rights, in the institution&rsquo;s words:</b> {E(r["rights_statement_verbatim"])}</p>
    </li>'''

    def para(x, section):
        m = VERIFIED.search(x)
        if not m:
            return f"<p{aid(section, inline(x))}>{inline(x)}</p>"
        fact = verified.get(m.group(1))
        if fact is None:
            sys.exit(f"{folder}: copy.md cites {m.group(1)} but verified-facts.json has no such fact")
        links = ", ".join(f'<a href="#src-{n}">{n}</a>' for n in fact["source_items"])
        word = "Source" if len(fact["source_items"]) == 1 else "Sources"
        badge = (f'<span class="vbadge"><span aria-hidden="true">&#10003;</span> Verified &middot; '
                 f'{word} {links} &middot; Last checked <time datetime="{fact["last_checked"]}">'
                 f'{checked(fact["last_checked"])}</time></span>')
        return f'<p class="vfact"{aid(section, inline(x[:m.start()]))}>{inline(x[:m.start()])} {badge}</p>'

    secs = "\n".join(
        f'''  <details class="sec"{' open' if i == 0 else ''}>
    <summary><h3>{E(t)}</h3></summary>
    {"".join(para(x, t) for x in paras)}
  </details>''' for i, (t, paras) in enumerate(p["sections"]))

    spotlight = ""
    if p["spot_item"] and p["spot_item"] in by_no:
        s = by_no[p["spot_item"]]
        excerpt = ""
        if p["spot_text"]:
            ex = " ".join(l.lstrip("> ").strip() for l in p["spot_text"].group(1).splitlines())
            excerpt = f'<blockquote class="excerpt"><p{aid("document", inline(ex))}>{inline(ex)}</p></blockquote>'
        img = (f'<img class="th" src="{s["_web"]}" alt="{E(s["alt_text"])}" loading="lazy">'
               if s.get("_web") else "")
        spotlight = f'''<section class="doc">
  <p class="label">The document behind this story</p>
  {img}
  <p><b>{E(s["title"])}</b> &mdash; {E(s["creator"])}, {E(s["date_created"])}.</p>
  <p{aid("document", inline(p["spot_intro"]))}>{inline(p["spot_intro"])}</p>
  {excerpt}
  <p class="meta">{credit(s)}</p>
</section>'''

    quote = (f'<blockquote class="pull"{aid("quote", inline(p["quote"]))}>&ldquo;{inline(p["quote"])}&rdquo;'
             # The space keeps the quote and its attribution apart in the passage text that
             # Margin Notes quote ("...the rule.” Albert Einstein", not "rule.”Albert").
             f' <cite>{inline(p["quote_source"])}</cite></blockquote>') if p["quote"] else ""
    qs = "\n".join(f"      <li>{inline(q)}</li>" for q in p["questions"])
    acts = "\n".join(f"      <li><b>{inline(t)}</b> {inline(b)}</li>" for t, b in p["activities"])
    srcs = "\n".join(source_item(r) for r in shown)
    try:
        media_html, media_md, media_css = media_sources.render_wp(ROOT, os.path.basename(folder))
    except media_sources.SourceError as e:
        sys.exit(f"ERROR {e}")
    compiled = inline(p["compiled"]) if p["compiled"] else (
        '<span class="fillme">[NAME OF THE PERSON WHO CHECKED THIS]</span>, '
        '<span class="fillme">[MONTH YEAR]</span>')

    out = f'''<!-- {E(p["name"]).upper()} — inductee profile for the Immigrant Hall of Honor
     Paste this whole file into ONE WordPress "Custom HTML" block. No JavaScript, no external
     files except the images. Upload the files in media/web/ to the Media Library first, then
     replace each "media/web/" path below with the URL WordPress gives you (INSTALL.md).
     Generated by tools/build_profile.py from copy.md and media-manifest.csv. Edit those. -->
<div class="ihh-profile">
<style>
{CSS}{BADGE_CSS if verified else ""}{media_css}.ihh-profile .doc img.th{{margin:0 0 1rem}}
.ihh-profile blockquote.excerpt{{margin:1rem 0;padding-left:1rem;border-left:3px solid var(--rule);font-size:1rem;color:var(--ink);font-style:normal}}
</style>

<p class="opening"{aid("opening", inline(p["opening"]))}>{inline(p["opening"])}</p>

<figure class="anchor">
  <img src="{anchor["_web"]}" alt="{E(anchor["alt_text"])}" loading="eager">
  <figcaption{aid("anchor-caption", E(anchor["title"]))}><b>{E(anchor["title"])}.</b> {credit(anchor)}</figcaption>
</figure>

<div class="w">
<!-- If your theme already prints the page title as a heading, delete the next line. -->
<h1>{E(p["name"])}</h1>
<p class="standfirst"{aid("standfirst", inline(p["standfirst"]))}>{inline(p["standfirst"])}</p>

{spotlight}

{quote}

<h2>The story</h2>
{secs}
</div>

<div class="wide">
<h2>The sources</h2>
<p class="gloss">Every fact on this page comes from one of these {len(shown)} items. Each links to
the institution that holds it and gives that institution&rsquo;s own rights wording.</p>
<ol class="sources">
{srcs}
</ol>
</div>
{media_html}

<div class="w">
<h2>Questions to talk about</h2>
<ol class="qs">
{qs}
</ol>

<h2>Things to try</h2>
<ol class="acts">
{acts}
</ol>

<p class="byline">Researched and compiled for the Immigrant Hall of Honor by {compiled}.
Research assisted by AI and checked by the team; every source above was opened and read.</p>
</div>
</div>
'''
    open(os.path.join(folder, "copy.html"), "w", encoding="utf-8", newline="\n").write(out)

    preview = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview &mdash; {E(p["name"])}</title>
<style>
/* An opinionated stand-in for a WordPress theme. If the block's scoping fails, it shows here. */
body{{margin:0;font-family:Verdana,sans-serif;font-size:14px;line-height:1.4;color:#333;background:#fff;text-align:center}}
h1,h2,h3,h4{{font-family:Impact,sans-serif;text-transform:uppercase;letter-spacing:2px}}
p{{margin:0 0 24px}} ol,ul{{padding-left:60px}} blockquote{{font-size:11px;color:#999}}
.host-chrome{{background:#222;color:#fff;padding:12px;font:11px/1.4 Verdana,sans-serif}}
</style></head><body>
<div class="host-chrome">Simulated WordPress theme &mdash; below is the pasted Custom HTML block</div>
{out}
<div class="host-chrome">End of block</div>
</body></html>
'''
    open(os.path.join(folder, "preview.html"), "w", encoding="utf-8", newline="\n").write(preview)

    def md_item(r):
        lines = [f'**{r["item_no"]}. {r["title"]}**', "", r["gloss"], "",
                 f'{r["creator"]} · {r["date_created"]} · {r["institution"]}']
        if r["stable_item_url"]:
            lines.append(f'<{r["stable_item_url"]}>')
        lines.append(f'Rights, in the institution\'s words: "{r["rights_statement_verbatim"]}"')
        if r.get("_web"):
            lines += [f'Image: `{r["_web"]}`', f'Credit: {r["required_credit"]}', f'Alt text: {r["alt_text"]}']
        return "\n".join(lines) + "\n"

    def plain_marker(m):
        f = verified[m.group(1)]
        return f" (Verified: sources {', '.join(f['source_items'])}; last checked {checked(f['last_checked'])})"

    md_out = re.sub(r"\s*\{verified:(LM-\d+)\}", plain_marker, md) if verified else md
    full = (md_out.rstrip() + "\n\n---\n\n## The sources\n\n" + "\n".join(md_item(r) for r in shown)
            + (f"\n---\n\n{media_md}" if media_md else ""))
    open(os.path.join(folder, "copy-full.md"), "w", encoding="utf-8", newline="\n").write(full)
    print(f"{os.path.relpath(folder, ROOT)}: {len(p['sections'])} sections, {len(shown)} sources "
          f"({sum(1 for r in shown if r.get('_web'))} images), {len(p['questions'])} questions, "
          f"{len(p['activities'])} activities, {out.count('<script')} script tags")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--all"]:
        base = os.path.join(ROOT, "inductees")
        args = [os.path.join(base, d) for d in sorted(os.listdir(base))
                if os.path.exists(os.path.join(base, d, "copy.md"))]
    if not args:
        sys.exit(__doc__)
    for a in args:
        build(a)
