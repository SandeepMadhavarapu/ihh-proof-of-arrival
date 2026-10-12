from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


def _grab(md: str, label: str) -> str:
    m = re.search(r"\*\*" + re.escape(label) + r"[^*]*:\*\*\n(.+?)\n\n", md, re.S)
    return " ".join(m.group(1).split()) if m else ""


def _parse(md: str):
    hm = re.search(r"^#\s+(.+)$", md, re.M)
    if not hm:
        raise ValueError("copy.md is missing its H1 profile name")
    name = hm.group(1).strip()
    opening = _grab(md, "Opening line")
    credit = _grab(md, "Credit")
    standfirst = _grab(md, "Standfirst")
    status_m = re.search(r"\*\*Status:\*\*\s*(.+)", md)
    status = status_m.group(1).strip() if status_m else "REQUIRES HUMAN SIGN-OFF"
    note = _grab(md, "Document note")

    parts = md.split("---")
    if len(parts) < 3:
        raise ValueError("copy.md does not contain expected section boundaries")
    body = parts[1]
    sections = []
    for chunk in re.split(r"\n## ", body)[1:]:
        lines = chunk.split("\n")
        sections.append((lines[0].strip(), " ".join(" ".join(lines[1:]).split())))
    if len(sections) != 5:
        raise ValueError(f"expected exactly five narrative sections; found {len(sections)}")

    qm = re.search(r"## Five discussion questions\n(.*?)\n## Two activities\n(.*?)$", md, re.S)
    if not qm:
        raise ValueError("discussion questions / activities block missing")
    questions = [" ".join(q.split()) for q in re.findall(r"^\d+\.\s+(.+?)(?=\n\d+\.|\Z)", qm.group(1), re.M | re.S)]
    activities = [(" ".join(t.split()), " ".join(b.split())) for t, b in re.findall(
        r"\*\*\d+\.\s*(.+?)\*\*\s*(.+?)(?=\n\*\*\d+\.|\Z)", qm.group(2), re.M | re.S)]
    if len(questions) != 5 or len(activities) != 2:
        raise ValueError("copy.md must contain exactly five questions and two activities")

    quote = re.search(r"\*\*First-person quotation \((.+?)\):\*\*\n> (.+?)\n\n", md, re.S)
    if not quote:
        raise ValueError("verified first-person quotation missing")
    quote_attr = re.sub(r"^one,\s*as reported by\s*", "", quote.group(1).strip(), flags=re.I)
    quote_text = " ".join(quote.group(2).replace("\n>", "").split())
    return name, status, opening, credit, standfirst, note, sections, questions, activities, quote_attr, quote_text


def _source_item(row: dict[str, str], profile_dir: Path) -> str:
    E = html.escape
    fn = row.get("filename", "")
    is_img = bool(re.search(r"\.(?:jpg|jpeg|png|webp)$", fn, re.I))
    media_path = profile_dir / "media" / fn if is_img else None
    if is_img and media_path and media_path.exists() and "UNCONFIRMED" not in row.get("long_description_status", "").upper():
        visual = f'<img class="th" src="media/{E(fn)}" alt="{E(row.get("alt_text", ""))}" loading="lazy" decoding="async">'
    elif is_img:
        visual = '<span class="th ph-th"><span>Image not supplied or subject not verified.</span></span>'
    else:
        visual = f'<p class="kindmark">{E(row.get("kind", "source"))}</p>'
    url = row.get("stable_item_url", "")
    inst = row.get("institution", "") or "Source"
    link = f'<a href="{E(url)}" rel="noopener">{E(inst)}</a>' if url else E(inst)
    rights = row.get("rights_statement_verbatim", "") or "NOT LOCATED IN RETRIEVED SOURCE TEXT"
    status = row.get("status", "")
    warning = ""
    if "UNCONFIRMED" in row.get("long_description_status", "").upper() or "NOT READ" in status.upper():
        warning = f'<p class="unread">{E(row.get("long_description_status", status))}</p>'
    return f'''<li class="src-item">{visual}
<h3 class="src-h">{E(row.get("title", "Untitled source"))}</h3>
<p class="gloss">{E(row.get("gloss", ""))}</p>{warning}
<p class="meta">{E(row.get("creator", ""))} · {E(row.get("date_created", ""))} · {link}</p>
<p class="rights"><b>Rights wording recorded:</b> {E(rights)}</p></li>'''


def build_profile(profile_dir: Path) -> list[Path]:
    profile_dir = profile_dir.resolve()
    md_path = profile_dir / "copy.md"
    man_path = profile_dir / "media-manifest.csv"
    if not md_path.exists() or not man_path.exists():
        raise FileNotFoundError("generic build requires copy.md and media-manifest.csv in profile directory")
    md = md_path.read_text(encoding="utf-8")
    with man_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    name, status, opening, credit, standfirst, note, sections, questions, activities, quote_attr, quote_text = _parse(md)
    E = html.escape

    anchor = next((r for r in rows if r.get("kind", "").lower() == "photograph"), None)
    if anchor:
        fn = anchor.get("filename", "")
        p = profile_dir / "media" / fn
        if p.exists() and "UNCONFIRMED" not in anchor.get("long_description_status", "").upper():
            anchor_html = f'<img src="media/{E(fn)}" alt="{E(anchor.get("alt_text", ""))}">'
        else:
            anchor_html = '<div class="ph"><span>Verified anchor photograph not supplied; profile remains publishable without it.</span></div>'
    else:
        anchor_html = '<div class="ph"><span>No verified anchor photograph was supplied by the source set.</span></div>'

    secs = "\n".join(
        f'<details class="sec"{" open" if i == 0 else ""}><summary><h3>{E(t)}</h3></summary><p>{E(b)}</p></details>'
        for i, (t, b) in enumerate(sections)
    )
    qs = "\n".join(f"<li>{E(q)}</li>" for q in questions)
    acts = "\n".join(f"<li><b>{E(t)}</b> {E(b)}</li>" for t, b in activities)
    srcs = "\n".join(_source_item(r, profile_dir) for r in rows)
    note_html = f'<section class="doc"><h2>Source note</h2><p>{E(note)}</p></section>' if note else ""

    out = f'''<!-- Generated at build time from copy.md + media-manifest.csv. No visitor-side API. -->
<div class="ihh-profile">
<style>
.ihh-profile{{--p:#fbfaf8;--p2:#f3f0ea;--ink:#1a1714;--mut:#56514a;--rule:#d9d4cb;--acc:#7a2e1e;color:var(--ink);background:var(--p);font:400 19px/1.62 Georgia,serif;padding:0 0 3rem}}
@media(prefers-color-scheme:dark){{.ihh-profile{{--p:#15130f;--p2:#1e1b16;--ink:#ece7df;--mut:#a7a096;--rule:#39352d;--acc:#e29c87}}}}
.ihh-profile *{{box-sizing:border-box}}.ihh-profile .w{{max-width:42rem;margin:auto;padding:0 1.15rem}}.ihh-profile .wide{{max-width:62rem;margin:auto;padding:0 1.15rem}}
.ihh-profile h1{{font-size:clamp(2rem,6vw,3rem);line-height:1.12;font-weight:400}}.ihh-profile h2{{font-size:1.5rem;font-weight:400;margin-top:2.3rem}}.ihh-profile h3{{font-size:1.08rem;margin:0;display:inline}}
.ihh-profile p,.ihh-profile li{{overflow-wrap:anywhere}}.ihh-profile .status{{border:2px solid var(--acc);padding:.75rem 1rem;font:700 .86rem/1.4 system-ui,sans-serif}}
.ihh-profile .opening,.ihh-profile .standfirst{{font-size:1.15rem}}.ihh-profile figure{{margin:1rem 0}}.ihh-profile figure img{{display:block;max-width:100%;height:auto}}.ihh-profile .ph,.ihh-profile .ph-th{{background:var(--p2);border:1px dashed var(--acc);min-height:9rem;display:flex;align-items:center;justify-content:center;text-align:center;padding:1rem}}
.ihh-profile figcaption,.ihh-profile .meta,.ihh-profile .rights,.ihh-profile .gloss{{font:400 .8rem/1.5 system-ui,sans-serif;color:var(--mut)}}.ihh-profile blockquote{{border-left:4px solid var(--acc);padding-left:1rem;font-size:1.15rem}}
.ihh-profile details{{border-top:1px solid var(--rule)}}.ihh-profile summary{{cursor:pointer;min-height:44px;display:flex;align-items:center}}.ihh-profile summary:focus-visible,.ihh-profile a:focus-visible{{outline:3px solid var(--acc);outline-offset:2px}}
.ihh-profile .sources{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1.4rem}}.ihh-profile .src-item{{border-top:2px solid var(--ink);padding-top:.8rem}}.ihh-profile .th{{max-width:100%;height:auto}}.ihh-profile .kindmark{{font:700 .7rem system-ui,sans-serif;text-transform:uppercase}}.ihh-profile .unread{{font:700 .78rem system-ui,sans-serif;border:1px dashed var(--acc);padding:.4rem}}
.ihh-profile a{{color:var(--ink);text-underline-offset:.16em}}@media print{{.ihh-profile details>*:not(summary){{display:block!important}}.ihh-profile{{background:#fff;color:#000}}}}
</style>
<div class="w"><p class="status">{E(status)} — generated by the Profile Factory; a named human must review before museum publication.</p><h1>{E(name)}</h1><p class="opening">{E(opening)}</p></div>
<figure class="anchor">{anchor_html}<figcaption class="wide"><b>Credit/source note:</b> {E(credit)}</figcaption></figure>
<div class="w"><p class="standfirst">{E(standfirst)}</p>{note_html}<blockquote>“{E(quote_text)}”<cite> — {E(quote_attr)}</cite></blockquote><h2>Life in five parts</h2>{secs}</div>
<div class="wide"><h2>The sources, and what each one is for</h2><ol class="sources">{srcs}</ol></div>
<div class="w"><h2>Five questions worth arguing about</h2><ol>{qs}</ol><h2>Two things to do</h2><ol>{acts}</ol>
<p class="status"><b>Human sign-off required.</b> Verification is machine-assisted and evidence-gated, but this profile is not museum-ready until a human reads the sources and the finished page.</p></div></div>'''

    copy_html = profile_dir / "copy.html"
    copy_html.write_text(out, encoding="utf-8")
    full = md.rstrip() + "\n\n---\n\n## Source register\n\n" + "\n\n".join(
        f"**{r.get('item_no','')}. {r.get('title','Untitled source')}**\n\n{r.get('gloss','')}\n\n{r.get('stable_item_url','')}\n\nRights wording recorded: {r.get('rights_statement_verbatim','NOT LOCATED IN RETRIEVED SOURCE TEXT')}"
        for r in rows
    ) + "\n\n---\n\n**REQUIRES HUMAN SIGN-OFF BEFORE MUSEUM PUBLICATION.**\n"
    full_path = profile_dir / "copy-full.md"
    full_path.write_text(full, encoding="utf-8")
    preview = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Preview — {E(name)}</title><style>body{{margin:0;font-family:Verdana,sans-serif;background:#fff;color:#333}}.host{{background:#222;color:#fff;padding:10px}}</style></head><body><div class="host">Simulated WordPress host</div>{out}<div class="host">End of generated block</div></body></html>'''
    preview_path = profile_dir / "preview.html"
    preview_path.write_text(preview, encoding="utf-8")
    return [copy_html, full_path, preview_path]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generic IHH profile build path")
    ap.add_argument("--profile-dir", required=True)
    args = ap.parse_args(argv)
    paths = build_profile(Path(args.profile_dir))
    print("generic profile written: " + ", ".join(str(p) for p in paths))
    return 0
