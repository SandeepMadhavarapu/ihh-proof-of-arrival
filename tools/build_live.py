#!/usr/bin/env python3
"""Build the PUBLIC DEMONSTRATION copy of the site (GitHub Pages) into _live/.

    python3 tools/build_live.py            # writes _live/ (git-ignored); never touches site/

The demonstration is a student prototype for the Immigrant Hall of Honor, not IHH's website, so
this copy differs from site/ in exactly these ways, and in no others:
  * every page carries a persistent banner saying so, with a link to immigranthallofhonor.org;
  * every page carries <meta name="robots" content="noindex,nofollow">;
  * Margin Notes and "Spot something? Tell us" run with the PREVIEW adapter: whatever a visitor
    writes stays in their own browser (localStorage) and is never sent anywhere;
  * curator-preview.html (not in the navigation; linked from the banner) lets that same browser
    approve or reject its own notes, so the whole moderated flow can be tried in a minute.
site/ and the WordPress handover keep their production setting (site-data/visitor-voices.json)
and never contain the preview adapter; tests/test_live_build.py checks all of this.
"""
import importlib.util
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
LIVE = os.path.join(ROOT, "_live")
CONFIG = {"adapter": "preview"}
OFFICIAL = "https://immigranthallofhonor.org/"

NOINDEX = '<meta name="robots" content="noindex,nofollow">\n'
BANNER_CSS = """<style>
.live-banner p{margin:0}
.live-banner{margin:0;padding:.6rem 1rem;background:#2a211a;color:#fbf6ee;font:500 .92rem/1.45 Georgia,'Times New Roman',serif;text-align:center}
.live-banner a{color:#fbf6ee;text-decoration:underline;text-underline-offset:3px;display:inline-block;min-height:24px;padding:2px 0}
.live-banner a:focus-visible{outline:2px solid #fbf6ee;outline-offset:2px}
</style>
"""
BANNER = ('<aside class="live-banner" aria-label="About this prototype"><p>Student prototype built for the Immigrant Hall of Honor '
          '&mdash; ChallengeX 2026. Not the official IHH website. Official site: '
          f'<a href="{OFFICIAL}">immigranthallofhonor.org</a>. '
          'Notes you leave here stay in your browser. '
          '<a href="curator-preview.html">Try the curator view</a></p></aside>')


def _load_gen():
    spec = importlib.util.spec_from_file_location("ihh_gen_live", os.path.join(ROOT, "site-src", "gen.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def curator_page(shell: str) -> str:
    """The curator preview, wrapped in the site's own header and footer."""
    head = shell[:shell.index('<main id="main"')]
    foot = shell[shell.index("</main>") + len("</main>"):]
    head = re.sub(r"<title>.*?</title>", "<title>Curator preview | Immigrant Hall of Honor (prototype)</title>", head)
    head = head.replace(' aria-current="page"', "")
    main = """<main id="main" class="">
<h1>Curator preview</h1>
<p class="lede">In the museum, nothing a visitor writes appears until a curator has read it. This
page lets you play that curator for the notes <b>you</b> left on this prototype.</p>
<p>Everything here is stored in this browser only. Nothing has been sent to the Immigrant Hall of
Honor or to anyone else, and clearing your browser data removes it. Approve a note, then open the
page it belongs to: it now sits beside the exact passage you wrote about.</p>
<p class="note" id="cp-status" role="status" aria-live="polite"></p>
<div id="cp-queue" class="cp-queue"><p class="cp-empty">This page needs JavaScript, because the
notes live in your browser.</p></div>
<style>
.cp-queue{display:grid;gap:1rem;margin:1.5rem 0}
.cp-item{border:1px solid var(--rule-strong);background:var(--paper);padding:1rem 1.2rem}
.cp-meta{font-size:.85rem;color:var(--muted);margin:0 0 .5rem}
.cp-status{font-weight:600;color:var(--accent)}
.cp-quote{margin:.4rem 0 .8rem;padding-left:.9rem;border-left:3px solid var(--rule);font-style:italic}
.cp-actions{display:flex;flex-wrap:wrap;gap:.6rem;margin:.8rem 0 0}
</style>
</main>"""
    scripts = ('<script src="assets/preview-adapter.js" defer></script>\n'
               '<script src="assets/curator-preview.js" defer></script>\n')
    return head + main + foot.replace("</body>", scripts + "</body>", 1)


def decorate(page: str) -> str:
    if NOINDEX not in page:
        page = page.replace("</head>", NOINDEX + BANNER_CSS + "</head>", 1)
    if 'class="live-banner"' not in page:
        # after the skip link, so "Skip to content" stays the first thing on the page
        page, n = re.subn(r'(<a class="skip"[^>]*>.*?</a>)', lambda m: m.group(1) + "\n" + BANNER, page, count=1)
        if not n:
            page = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + BANNER, page, count=1)
    page = page.replace('<script src="assets/margin-notes.js" defer>',
                        '<script src="assets/preview-adapter.js" defer></script>\n'
                        '<script src="assets/margin-notes.js" defer>')
    return page


def build(out: str = LIVE) -> str:
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(os.path.join(ROOT, "site"), out)
    from tools import build_site_pages
    build_site_pages.main(ROOT, site=out, voices=CONFIG)
    _load_gen().main(site=out, voices=CONFIG)
    shutil.copy2(os.path.join(ROOT, "voices", "preview_adapter.js"), os.path.join(out, "assets", "preview-adapter.js"))
    shutil.copy2(os.path.join(ROOT, "voices", "curator_preview.js"), os.path.join(out, "assets", "curator-preview.js"))
    with open(os.path.join(out, "about.html"), encoding="utf-8") as f:
        shell = f.read()
    with open(os.path.join(out, "curator-preview.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(curator_page(shell))
    n = 0
    for name in sorted(os.listdir(out)):
        if name.endswith(".html"):
            path = os.path.join(out, name)
            with open(path, encoding="utf-8") as f:
                s = f.read()
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(decorate(s))
            n += 1
    # GitHub Pages: serve files as they are (no Jekyll processing).
    open(os.path.join(out, ".nojekyll"), "w").close()
    print(f"{os.path.relpath(out, ROOT)}/: {n} pages, preview adapter, banner and noindex on every page")
    return out


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else LIVE)
