from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path

from .security import ensure_media_path, ensure_profile_output, validate_external_link, validate_media_filename


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _row_link(row: dict[str, str]) -> tuple[str, str]:
    url = row.get("stable_item_url", "").strip()
    inst = row.get("institution", "").strip() or "Source"
    if not url:
        return "", inst
    return validate_external_link(url), inst


def _source_item(row: dict[str, str], profile_dir: Path) -> str:
    E = html.escape
    fn = row.get("filename", "").strip()
    is_img = bool(re.search(r"\.(?:jpg|jpeg|png|webp)$", fn, re.I))
    visual: str
    if is_img:
        validate_media_filename(fn)
        media_path = ensure_media_path(profile_dir, fn)
        confirmed = "UNCONFIRMED" not in row.get("long_description_status", "").upper()
        if media_path.exists() and confirmed:
            visual = f'<img class="th" src="media/{E(fn)}" alt="{E(row.get("alt_text", ""))}" loading="lazy" decoding="async">'
        else:
            reason = "SUBJECT NOT VERIFIED" if not confirmed else "IMAGE NOT SUPPLIED"
            visual = (
                '<span class="th ph-th" role="img" aria-label="Archival image placeholder">'
                f'<span class="ph-kicker">ARCHIVAL OBJECT</span><strong>{E(reason)}</strong>'
                '<span class="ph-rule" aria-hidden="true"></span>'
                f'<span class="ph-file">{E(fn)}</span></span>'
            )
    else:
        visual = f'<p class="kindmark">{E(row.get("kind", "source") or "source")}</p>'

    url, inst = _row_link(row)
    link = f'<a href="{E(url)}" rel="noopener noreferrer">{E(inst)}</a>' if url else E(inst)
    rights = row.get("rights_statement_verbatim", "").strip() or "NOT LOCATED IN RETRIEVED SOURCE TEXT"
    status = row.get("status", "").strip()
    desc_status = row.get("long_description_status", "").strip()
    flags = []
    for flag in (status, desc_status):
        upper = flag.upper()
        if flag and any(key in upper for key in ("UNCONFIRMED", "NOT READ", "NOT LOCATED", "NOT DOWNLOADED", "FIXTURE", "TRANSCRIBED")):
            flags.append(f'<span class="evidence-flag">{E(flag)}</span>')
    flags_html = "".join(flags)
    return f'''<li class="src-item">{visual}
<div class="src-body"><p class="source-number">SOURCE {E(row.get("item_no", ""))}</p>
<h3 class="src-h">{E(row.get("title", "Untitled source"))}</h3>
<p class="gloss">{E(row.get("gloss", ""))}</p>
<div class="evidence-flags">{flags_html}</div>
<p class="meta">{E(row.get("creator", ""))} · {E(row.get("date_created", ""))} · {link}</p>
<p class="rights"><b>Rights wording recorded</b><span>{E(rights)}</span></p></div></li>'''


def build_profile(profile_dir: Path, repo_root: Path | None = None) -> list[Path]:
    root = Path(repo_root or REPO_ROOT).resolve()
    profile_dir = ensure_profile_output(root, Path(profile_dir).resolve())
    md_path = profile_dir / "copy.md"
    man_path = profile_dir / "media-manifest.csv"
    if not md_path.exists() or not man_path.exists():
        raise FileNotFoundError("generic build requires copy.md and media-manifest.csv in profile directory")
    md = md_path.read_text(encoding="utf-8")
    with man_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("media-manifest.csv contains no source rows")
    name, status, opening, credit, standfirst, note, sections, questions, activities, quote_attr, quote_text = _parse(md)
    E = html.escape

    anchor = next((r for r in rows if r.get("kind", "").lower() == "photograph"), None)
    if anchor:
        fn = anchor.get("filename", "").strip()
        validate_media_filename(fn)
        p = ensure_media_path(profile_dir, fn)
        confirmed = "UNCONFIRMED" not in anchor.get("long_description_status", "").upper()
        if p.exists() and confirmed:
            anchor_html = f'<img src="media/{E(fn)}" alt="{E(anchor.get("alt_text", ""))}">'
        else:
            state = "SUBJECT NOT VERIFIED" if not confirmed else "IMAGE NOT SUPPLIED"
            anchor_html = f'''<div class="anchor-placeholder" role="img" aria-label="{E(state.title())}">
<span class="archive-label">ARCHIVAL IMAGE</span><strong>{E(state)}</strong>
<span class="archive-rule" aria-hidden="true"></span><span>{E(anchor.get("institution", "Source institution"))}</span></div>'''
    else:
        anchor_html = '''<div class="anchor-placeholder" role="img" aria-label="No verified anchor photograph supplied">
<span class="archive-label">ARCHIVAL IMAGE</span><strong>NO VERIFIED IMAGE SUPPLIED</strong>
<span class="archive-rule" aria-hidden="true"></span><span>The profile remains evidence-complete without inventing one.</span></div>'''

    secs = "\n".join(
        f'''<details class="sec"{" open" if i == 0 else ""}><summary><span class="sec-no">0{i+1}</span><h3>{E(t)}</h3></summary><p>{E(b)}</p></details>'''
        for i, (t, b) in enumerate(sections)
    )
    qs = "\n".join(f"<li>{E(q)}</li>" for q in questions)
    acts = "\n".join(f"<li><b>{E(t)}</b> {E(b)}</li>" for t, b in activities)
    srcs = "\n".join(_source_item(r, profile_dir) for r in rows)
    note_html = f'<aside class="doc"><p class="eyebrow">SOURCE BOUNDARY</p><h2>What this profile will not pretend to know</h2><p>{E(note)}</p></aside>' if note else ""

    out = f'''<!-- Generated at build time from copy.md + media-manifest.csv. No visitor-side API. -->
<div class="ihh-profile">
<style>
.ihh-profile{{--paper:#fbf8f1;--paper2:#f1eadf;--ink:#1c1915;--mut:#625c53;--rule:#cfc4b4;--acc:#7d3022;--acc2:#a85f49;--focus:#174e7a;--shadow:rgba(41,31,20,.08);color:var(--ink);background:var(--paper);font:400 19px/1.68 Georgia,"Iowan Old Style","Palatino Linotype",Palatino,serif;padding:0 0 4rem;isolation:isolate}}
@media(prefers-color-scheme:dark){{.ihh-profile{{--paper:#17130f;--paper2:#221c16;--ink:#f1e9dc;--mut:#beb2a2;--rule:#4c4034;--acc:#e4a08d;--acc2:#f0b6a5;--focus:#87c8ff;--shadow:rgba(0,0,0,.28)}}}}
.ihh-profile *{{box-sizing:border-box}}.ihh-profile :where(h1,h2,h3,p,li,blockquote,figcaption,summary,cite){{font-family:inherit;text-transform:none;letter-spacing:normal}}
.ihh-profile a{{color:inherit;text-decoration-thickness:.08em;text-underline-offset:.18em}}.ihh-profile a:focus-visible,.ihh-profile summary:focus-visible{{outline:3px solid var(--focus);outline-offset:4px}}
.ihh-profile .w{{max-width:43rem;margin:auto;padding:0 1.2rem}}.ihh-profile .wide{{max-width:68rem;margin:auto;padding:0 1.2rem}}.ihh-profile p,.ihh-profile li,.ihh-profile a{{overflow-wrap:anywhere}}
.ihh-profile .mast{{padding:clamp(2rem,7vw,5rem) 0 1.8rem;border-bottom:1px solid var(--rule);background:linear-gradient(180deg,var(--paper2),var(--paper))}}
.ihh-profile .eyebrow,.ihh-profile .source-number,.ihh-profile .archive-label,.ihh-profile .ph-kicker{{font:700 .68rem/1.2 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);margin:0 0 .65rem}}
.ihh-profile .status{{display:inline-flex;gap:.55rem;align-items:center;border:1px solid var(--acc);padding:.5rem .7rem;margin:0 0 1.5rem;font:700 .72rem/1.3 system-ui,sans-serif;letter-spacing:.05em;text-transform:uppercase}}
.ihh-profile .status::before{{content:"";width:.52rem;height:.52rem;border-radius:50%;background:var(--acc)}}
.ihh-profile h1{{font-size:clamp(2.7rem,8vw,5.7rem);line-height:.98;font-weight:400;letter-spacing:-.035em;margin:.1rem 0 1.1rem;max-width:11ch}}
.ihh-profile .opening{{font-size:clamp(1.12rem,2.3vw,1.38rem);line-height:1.5;max-width:35rem;margin:0;color:var(--mut)}}
.ihh-profile figure.anchor{{margin:0;border-bottom:1px solid var(--rule)}}.ihh-profile figure.anchor>img{{width:100%;max-height:72vh;object-fit:cover;display:block}}
.ihh-profile .anchor-placeholder{{min-height:clamp(18rem,48vw,38rem);background:repeating-linear-gradient(135deg,var(--paper2),var(--paper2) 1px,var(--paper) 1px,var(--paper) 18px);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;color:var(--mut)}}
.ihh-profile .anchor-placeholder strong{{font:700 clamp(1rem,2vw,1.35rem)/1.2 system-ui,sans-serif;letter-spacing:.12em;color:var(--ink);margin:.5rem 0 1rem}}.ihh-profile .archive-rule{{width:min(18rem,60vw);height:1px;background:var(--acc);margin:0 0 1rem}}
.ihh-profile figcaption{{font:400 .82rem/1.55 system-ui,sans-serif;color:var(--mut);padding:1rem 1.2rem 1.2rem;max-width:68rem;margin:auto}}
.ihh-profile .standfirst{{font-size:clamp(1.25rem,3vw,1.65rem);line-height:1.5;margin:clamp(2.6rem,7vw,5rem) 0 2rem}}
.ihh-profile .doc{{background:var(--paper2);border-left:4px solid var(--acc);padding:1.25rem 1.35rem;margin:2.2rem 0}}.ihh-profile .doc h2{{font-size:1.12rem;margin:.1rem 0 .65rem}}
.ihh-profile blockquote{{margin:2.6rem 0;padding:1.4rem 0 1.4rem 1.35rem;border-left:4px solid var(--acc);font-size:clamp(1.18rem,2.5vw,1.45rem);line-height:1.55;font-style:italic}}
.ihh-profile blockquote cite{{display:block;font:400 .82rem/1.5 system-ui,sans-serif;color:var(--mut);font-style:normal;margin-top:.8rem}}
.ihh-profile h2{{font-size:clamp(1.45rem,3vw,1.9rem);font-weight:400;line-height:1.2;margin:3.2rem 0 1.1rem}}
.ihh-profile details.sec{{border-top:1px solid var(--rule)}}.ihh-profile details.sec:last-of-type{{border-bottom:1px solid var(--rule)}}.ihh-profile summary{{cursor:pointer;list-style:none;min-height:4rem;display:grid;grid-template-columns:2.2rem 1fr auto;align-items:center;gap:.65rem;padding:.9rem 0}}
.ihh-profile summary::-webkit-details-marker{{display:none}}.ihh-profile summary::after{{content:"+";font:400 1.25rem/1 system-ui,sans-serif;color:var(--acc)}}.ihh-profile details[open] summary::after{{content:"–"}}.ihh-profile .sec-no{{font:700 .66rem/1 system-ui,sans-serif;color:var(--acc);letter-spacing:.08em}}.ihh-profile summary h3{{font-size:1.07rem;margin:0}}.ihh-profile details.sec>p{{margin:.1rem 0 1.4rem;padding-left:2.85rem}}
.ihh-profile .source-deck{{margin-top:4rem;padding:2.8rem 0 3.4rem;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);background:linear-gradient(180deg,var(--paper2),var(--paper))}}
.ihh-profile .sources{{list-style:none;margin:1.4rem 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,19rem),1fr));gap:1rem}}
.ihh-profile .src-item{{min-width:0;background:var(--paper);border:1px solid var(--rule);box-shadow:0 .7rem 1.8rem var(--shadow);padding:1rem;display:flex;flex-direction:column;gap:.8rem}}.ihh-profile .src-body{{min-width:0}}
.ihh-profile .src-h{{font-size:1.05rem;line-height:1.35;margin:.15rem 0 .55rem;display:block}}.ihh-profile .gloss{{font:400 .91rem/1.55 system-ui,sans-serif;margin:0 0 .8rem;color:var(--ink)}}.ihh-profile .meta{{font:400 .76rem/1.55 system-ui,sans-serif;color:var(--mut);margin:.65rem 0}}
.ihh-profile .rights{{font:400 .75rem/1.48 system-ui,sans-serif;color:var(--mut);border-top:1px solid var(--rule);padding-top:.7rem;margin:.7rem 0 0}}.ihh-profile .rights b,.ihh-profile .rights span{{display:block}}.ihh-profile .rights b{{color:var(--ink);margin-bottom:.25rem}}
.ihh-profile .kindmark{{display:inline-block;border:1px solid var(--rule);padding:.42rem .55rem;margin:0;width:max-content;font:700 .66rem/1 system-ui,sans-serif;letter-spacing:.13em;text-transform:uppercase;color:var(--mut)}}
.ihh-profile .th{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}.ihh-profile .ph-th{{min-height:11rem;background:repeating-linear-gradient(135deg,var(--paper2),var(--paper2) 1px,var(--paper) 1px,var(--paper) 14px);border:1px dashed var(--acc);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:1rem}}.ihh-profile .ph-th strong{{font:700 .8rem/1.25 system-ui,sans-serif;letter-spacing:.08em}}.ihh-profile .ph-rule{{width:60%;height:1px;background:var(--rule);margin:.7rem}}.ihh-profile .ph-file{{font:400 .68rem/1.4 ui-monospace,monospace;color:var(--mut);overflow-wrap:anywhere}}
.ihh-profile .evidence-flags{{display:flex;flex-wrap:wrap;gap:.35rem;margin:.6rem 0}}.ihh-profile .evidence-flag{{border:1px solid var(--acc);padding:.28rem .42rem;font:700 .62rem/1.2 system-ui,sans-serif;color:var(--acc)}}
.ihh-profile .questions{{padding-top:1rem}}.ihh-profile .questions ol{{padding-left:1.35rem}}.ihh-profile .questions li{{margin:.75rem 0}}.ihh-profile .final-status{{margin-top:3rem;padding-top:1.4rem;border-top:2px solid var(--ink)}}
@media(max-width:430px){{.ihh-profile{{font-size:18px}}.ihh-profile h1{{font-size:clamp(2.5rem,14vw,4rem)}}.ihh-profile summary{{grid-template-columns:1.8rem 1fr auto}}.ihh-profile details.sec>p{{padding-left:2.45rem}}}}
@media(prefers-reduced-motion:reduce){{.ihh-profile *{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
@media print{{.ihh-profile{{--paper:#fff;--paper2:#fff;--ink:#000;--mut:#333;--rule:#777;--acc:#000;--shadow:transparent}}.ihh-profile details>*:not(summary){{display:block!important}}.ihh-profile .src-item{{break-inside:avoid;box-shadow:none}}}}
</style>
<header class="mast"><div class="w"><p class="status">{E(status)}</p><p class="eyebrow">IMMIGRANT HALL OF HONOR · EVIDENCE-GATED PROFILE</p><h1>{E(name)}</h1><p class="opening">{E(opening)}</p></div></header>
<figure class="anchor">{anchor_html}<figcaption><b>Credit / source note:</b> {E(credit)}</figcaption></figure>
<main>
<div class="w"><p class="standfirst">{E(standfirst)}</p>{note_html}<blockquote>“{E(quote_text)}”<cite> — {E(quote_attr)}</cite></blockquote><h2>Life in five parts</h2>{secs}</div>
<section class="source-deck"><div class="wide"><p class="eyebrow">PROVENANCE REGISTER</p><h2>The sources — and the boundaries around them</h2><ol class="sources">{srcs}</ol></div></section>
<section class="w questions"><h2>Five questions worth arguing about</h2><ol>{qs}</ol><h2>Two things to do</h2><ol>{acts}</ol>
<div class="final-status"><p class="status"><b>Human sign-off required</b></p><p>Machine verification checks evidence spans and build quality. A named human must still read the sources and finished page before museum publication.</p></div></section>
</main></div>'''

    copy_html = profile_dir / "copy.html"
    copy_html.write_text(out, encoding="utf-8")
    full = md.rstrip() + "\n\n---\n\n## Source register\n\n" + "\n\n".join(
        f"**{r.get('item_no','')}. {r.get('title','Untitled source')}**\n\n{r.get('gloss','')}\n\n{r.get('stable_item_url','')}\n\nRights wording recorded: {r.get('rights_statement_verbatim','NOT LOCATED IN RETRIEVED SOURCE TEXT')}"
        for r in rows
    ) + "\n\n---\n\n**PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF BEFORE MUSEUM PUBLICATION.**\n"
    full_path = profile_dir / "copy-full.md"
    full_path.write_text(full, encoding="utf-8")
    preview = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Preview — {E(name)}</title><style>body{{margin:0;font-family:Verdana,sans-serif;background:#fff;color:#333}}.host{{background:#222;color:#fff;padding:10px;font:14px/1.4 system-ui,sans-serif}}</style></head><body><div class="host">Simulated WordPress host · static profile preview</div>{out}<div class="host">End of generated block</div></body></html>'''
    preview_path = profile_dir / "preview.html"
    preview_path.write_text(preview, encoding="utf-8")
    return [copy_html, full_path, preview_path]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generic IHH profile build path")
    ap.add_argument("--profile-dir", required=True)
    args = ap.parse_args(argv)
    paths = build_profile(Path(args.profile_dir), REPO_ROOT)
    print("generic profile written: " + ", ".join(str(p) for p in paths))
    return 0
