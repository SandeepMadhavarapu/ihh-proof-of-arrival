#!/usr/bin/env python3
"""Look closer: annotated artifacts, built from site-data/artifacts/research.json.

    python3 tools/artifacts.py --check     # verify every annotation against its evidence (no build)

Used by tools/build_site_pages.py (a "Look closer" section on each profile that has an artifact,
plus site/artifacts.html) and by tools/package_handover.sh (handover/<slug>/look-closer.html, a
static Custom HTML block for WordPress: no JavaScript).

The check refuses to build if, for any hotspot or "Can you spot it?" answer:
  * an evidence span is not found word for word in the text it cites: 'artifact' (the transcription
    of the artifact itself), 'related' (a related page of the same record) or 'profile' (the
    inductee's verified inductees/<slug>/copy.md);
  * a number, date or month in the text does not appear in its evidence;
  * a capitalised name in the text does not appear in its evidence;
  * the artifact has no rights wording, no image, or no alt text (125 characters at most).
These are mechanical checks. They catch invented numbers, dates and names; they do not prove
that a sentence's meaning is supported, which is why a person still reviews every annotation.
"""
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site-data", "artifacts", "research.json")
IMAGES = os.path.join(ROOT, "site-data", "artifacts", "images")
E = html.escape
LABEL = "Annotations drafted with AI and checked against the sources listed."

MONTHS = ("january february march april may june july august september october november december "
          "jan feb mar apr jun jul aug sep sept oct nov dec").split()
NUMBER_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
                "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "eighteen": "18",
                "twenty": "20", "eighty": "80", "eighty-eight": "88"}
# Capitalised words that are ordinary English at the start of a clause or are labels, not names.
COMMON = set("""A An The This That These Those It Its He His She Her They Their There Each Every One Two Three
Four Five Six Seven Eight Nine Ten Figure Fig Without Who What Which Where When Why How Read Find If In On At
For From By To And But So Or Not No Of Is Was Were Be Class Occupation Age Show Look""".split())


class CheckError(Exception):
    pass


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)["artifacts"]


def profile_text(slug):
    with open(os.path.join(ROOT, "inductees", slug, "copy.md"), encoding="utf-8") as f:
        return f.read()


def _tokens(text):
    """Numbers (with their commas), month names and number words in a piece of visitor text."""
    t = norm(text)
    out = set(re.findall(r"\d[\d,./-]*\d|\d", t))
    low = t.lower()
    out |= {m for m in MONTHS if re.search(r"\b" + m + r"\b", low)}
    out |= {NUMBER_WORDS[w] for w in NUMBER_WORDS if re.search(r"\b" + w + r"\b", low)}
    return {x.rstrip(".,") for x in out}


def _names(text):
    t = norm(text)
    words = {re.sub(r"'s$", "", w) for w in re.findall(r"\b[A-Z][a-zA-Z'\-]+\b", t)}
    return {w for w in words if w not in COMMON}


def _check_claim(a, label, text, evidence, texts):
    if not evidence:
        raise CheckError(f"{a['id']} {label}: no evidence")
    spans = []
    for ev in evidence:
        src = ev.get("source")
        if src not in texts:
            raise CheckError(f"{a['id']} {label}: unknown evidence source {src!r}")
        span = norm(ev.get("exact_span", ""))
        if len(span) < 4 or span not in norm(texts[src]):
            raise CheckError(f"{a['id']} {label}: span not found in {src}: {ev.get('exact_span')!r}")
        spans.append(span)
    joined = " ".join(spans)
    missing = {t for t in _tokens(text) if t not in _tokens(joined) and t not in norm(joined).lower()}
    if missing:
        raise CheckError(f"{a['id']} {label}: number/date not in its evidence: {sorted(missing)}")
    low = norm(joined).lower()
    unnamed = {n for n in _names(text) if n.lower() not in low}
    if unnamed:
        raise CheckError(f"{a['id']} {label}: name not in its evidence: {sorted(unnamed)}")


def check(artifacts=None):
    artifacts = artifacts if artifacts is not None else load()
    seen = set()
    for a in artifacts:
        if a["id"] in seen or not re.fullmatch(r"[a-z0-9-]+", a["id"]):
            raise CheckError(f"bad or duplicate artifact id {a['id']!r}")
        seen.add(a["id"])
        r = a.get("rights") or {}
        if not r.get("exact_span") or not r.get("source_url", "").startswith("https://"):
            raise CheckError(f"{a['id']}: no rights wording with its source")
        if not os.path.isfile(os.path.join(IMAGES, a["image"])):
            raise CheckError(f"{a['id']}: image missing: site-data/artifacts/images/{a['image']}")
        if not a.get("alt") or len(a["alt"]) > 125:
            raise CheckError(f"{a['id']}: alt text missing or longer than 125 characters")
        texts = {"artifact": a["transcription"], "related": a.get("related_text", ""), "profile": profile_text(a["slug"])}
        ns = [h["n"] for h in a["hotspots"]]
        if ns != list(range(1, len(ns) + 1)) or not 4 <= len(ns) <= 7:
            raise CheckError(f"{a['id']}: hotspots must be numbered 1..n with 4 to 7 of them")
        for h in a["hotspots"]:
            g = h["region"]
            if not all(0 <= g[k] <= 100 for k in "xywh") or g["x"] + g["w"] > 100.5 or g["y"] + g["h"] > 100.5:
                raise CheckError(f"{a['id']} hotspot {h['n']}: region outside the image")
            _check_claim(a, f"hotspot {h['n']}", h["text"], h["evidence"], texts)
        s = a["spot_it"]
        if s["hotspot"] not in ns:
            raise CheckError(f"{a['id']}: spot-it points at a missing hotspot")
        _check_claim(a, "spot-it answer", s["answer"], s["evidence"], texts)
    return artifacts


def for_slug(slug, artifacts=None):
    return [a for a in (artifacts if artifacts is not None else load()) if a["slug"] == slug]


def image_size(a):
    """(width, height) read from the JPEG header, so the page reserves the image's space before it
    loads and the numbered markers are the right size from the start."""
    with open(os.path.join(IMAGES, a["image"]), "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise CheckError(f"{a['image']}: not a baseline JPEG")
        marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + length
    raise CheckError(f"{a['image']}: no image size found")


def copy_images(site):
    out = os.path.join(site, "media", "artifacts")
    os.makedirs(out, exist_ok=True)
    for a in load():
        shutil.copy2(os.path.join(IMAGES, a["image"]), os.path.join(out, a["image"]))


def _evidence_html(a, ev):
    if ev["source"] == "profile":
        where = "this inductee&rsquo;s profile"
    elif ev["source"] == "related":
        where = f'<a href="{E(a["download_url"] or a["item_url"])}">{E(a.get("related_title", "the record"))}</a>'
    else:
        where = f'<a href="{E(a["item_url"])}">the document itself</a>'
    return f'<li>&ldquo;{E(ev["exact_span"])}&rdquo; &mdash; {where}</li>'


def section(a, img_src, heading="h2", js=True):
    """One artifact. Without JavaScript (and in the WordPress block) the numbered markers are
    links to the numbered notes, which are ordinary text below the image."""
    aid = a["id"]
    iw, ih = image_size(a)
    marks = []
    for h in a["hotspots"]:
        g = h["region"]
        marks.append(
            f'<a class="lc-hs" id="lc-{aid}-m{h["n"]}" href="#lc-{aid}-{h["n"]}" '
            f'style="left:{g["x"]}%;top:{g["y"]}%;width:{g["w"]}%;height:{g["h"]}%" '
            f'aria-label="Note {h["n"]}: {E(h["title"], quote=True)}"><span class="lc-n" aria-hidden="true">{h["n"]}</span></a>')
    notes = []
    for h in a["hotspots"]:
        evs = "".join(_evidence_html(a, ev) for ev in h["evidence"])
        notes.append(f'''  <li id="lc-{aid}-{h["n"]}" class="lc-note">
    <h3 class="lc-t"><span class="lc-num">{h["n"]}</span> {E(h["title"])}</h3>
    <p>{E(h["text"])}</p>
    <details class="lc-ev"><summary>Source</summary><ul>{evs}</ul></details>
    <p class="lc-back"><a href="#lc-{aid}-m{h["n"]}">Back to the document</a></p>
  </li>''')
    s = a["spot_it"]
    r = a["rights"]
    zoom = (f'<p class="lc-tools"><button type="button" class="lc-zoom" aria-pressed="false" '
            f'aria-controls="lc-{aid}-stage">Zoom in</button> '
            f'<a href="{E(img_src)}">Open the full image</a></p>') if js else f'<p class="lc-tools"><a href="{E(img_src)}">Open the full image</a></p>'
    h_open, h_close = f"<{heading} id=\"lc-{aid}-h\">", f"</{heading}>"
    return f'''<section class="look-closer" id="lc-{aid}" aria-labelledby="lc-{aid}-h">
<p class="lc-kick">Look closer</p>
{h_open}{E(a["title"])}{h_close}
<p class="lc-lede">Select a number on the document, or read the notes below it. {E(LABEL)}</p>
{zoom}
<div class="lc-stage" id="lc-{aid}-stage">
  <div class="lc-frame">
    <img src="{E(img_src)}" alt="{E(a["alt"], quote=True)}" width="{iw}" height="{ih}" loading="lazy">
    {"".join(marks)}
  </div>
</div>
<p class="lc-credit">{E(a["credit"])} Rights, in the source&rsquo;s own words: &ldquo;{E(r["exact_span"])}&rdquo; (<a href="{E(r["source_url"])}">source</a>).</p>
<ol class="lc-notes">
{chr(10).join(notes)}
</ol>
<details class="lc-spot">
  <summary><span class="lc-spot-k">Can you spot it?</span> {E(s["question"])}</summary>
  <p>{E(s["answer"])} <a href="#lc-{aid}-m{s["hotspot"]}">Show me on the document</a></p>
</details>
<details class="lc-tr">
  <summary>Read the full transcription</summary>
  <p class="lc-trn">{E(a.get("transcription_note", ""))}</p>
  <div class="lc-trt">{"".join(f"<p>{E(line)}</p>" for line in a["transcription"].split(chr(10)))}</div>
</details>
</section>'''


def site_section(slug, artifacts=None):
    items = for_slug(slug, artifacts)
    return "".join("\n" + section(a, f"media/artifacts/{a['image']}") for a in items)


def index_main(artifacts, names):
    cards = []
    for a in artifacts:
        who = names.get(a["slug"], a["slug"])
        cards.append(f'''  <li class="lc-card">
    <img src="media/artifacts/{E(a["image"])}" alt="" loading="lazy" width="{image_size(a)[0]}" height="{image_size(a)[1]}">
    <p class="lc-card-k">{E(who)}</p>
    <h2 class="lc-card-t"><a href="{a["slug"]}.html#lc-{a["id"]}">{E(a["title"])}</a></h2>
    <p class="lc-card-n">{len(a["hotspots"])} notes &middot; Can you spot it?</p>
  </li>''')
    return f'''<main id="main" class="wide look-index">

<h1>Look closer</h1>
<p class="lede">Real documents from the inductees&rsquo; lives: patents, a visa form and a
citizenship declaration. Each one has numbered notes that explain what you are looking at, and every
note shows the source it comes from. {E(LABEL)}</p>

<ul class="lc-cards">
{chr(10).join(cards)}
</ul>
</main>'''


# A self-contained copy for the WordPress handover: scoped CSS, no JavaScript, image path relative
# to the package (upload it to the Media Library and replace the path, as INSTALL.md describes).
WP_CSS = """.ihh-look{--ink:#1f1a17;--muted:#5a5048;--accent:#8b2a1d;--rule:#c3b293;--paper:#fbf7ef;
font:400 1.05rem/1.6 Georgia,'Times New Roman',serif;color:var(--ink);max-width:62rem;margin:2rem auto}
.ihh-look *{box-sizing:border-box}.ihh-look h2{font-size:1.6rem;line-height:1.25;margin:.2rem 0 .6rem}
.ihh-look h3{font-size:1.1rem;margin:0 0 .3rem}.ihh-look a{color:var(--accent)}
.ihh-look .lc-kick{margin:0;font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.ihh-look .lc-lede,.ihh-look .lc-credit{color:var(--muted);font-size:.9rem}
.ihh-look .lc-frame{position:relative;max-width:40rem;margin:1rem auto;border:1px solid var(--rule);background:#fff}
.ihh-look .lc-frame img{display:block;width:100%;height:auto}
.ihh-look .lc-hs{position:absolute;display:block;min-width:28px;min-height:28px;border:2px dashed rgba(139,42,29,.5);text-decoration:none}
.ihh-look .lc-hs:hover,.ihh-look .lc-hs:focus{border-color:var(--accent);background:rgba(139,42,29,.08);outline:none}
.ihh-look .lc-n,.ihh-look .lc-num{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:28px;
border-radius:14px;background:var(--accent);color:#fff;font:700 .85rem/1 Arial,sans-serif}
.ihh-look .lc-n{position:absolute;left:-14px;top:-14px}
.ihh-look .lc-notes{list-style:none;padding:0;display:grid;gap:1rem}
.ihh-look .lc-note{border-top:1px solid var(--rule);padding-top:.8rem}
.ihh-look details{margin:.6rem 0}.ihh-look summary{cursor:pointer;min-height:24px}
.ihh-look .lc-spot{border:2px solid var(--accent);padding:.6rem 1rem;background:var(--paper)}
"""


def wp_block(a, img_src):
    return (f"<!-- LOOK CLOSER: {E(a['title'])}. Paste into ONE WordPress Custom HTML block. No JavaScript. "
            f"Upload {a['image']} to the Media Library first and replace the image path below. "
            f"Generated by tools/artifacts.py from site-data/artifacts/research.json. -->\n"
            f'<div class="ihh-look">\n<style>\n{WP_CSS}</style>\n'
            + section(a, img_src, heading="h2", js=False) + "\n</div>\n")


def write_handover(handover):
    for a in check():
        out = os.path.join(handover, a["slug"])
        os.makedirs(os.path.join(out, "media", "artifacts"), exist_ok=True)
        shutil.copy2(os.path.join(IMAGES, a["image"]), os.path.join(out, "media", "artifacts", a["image"]))
        with open(os.path.join(out, f"look-closer-{a['id']}.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(wp_block(a, f"media/artifacts/{a['image']}"))


if __name__ == "__main__":
    try:
        arts = check()
    except CheckError as e:
        sys.exit(f"ERROR {e}")
    n = sum(len(a["hotspots"]) for a in arts)
    print(f"artifacts: {len(arts)} artifacts, {n} hotspots, every span and number/date/name checked")
    if "--handover" in sys.argv[1:]:
        write_handover(os.path.join(ROOT, "handover"))
