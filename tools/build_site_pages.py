#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap each built inductee profile in the demo site's page chrome.

    python3 tools/build_profile.py --all      # first
    python3 tools/build_site_pages.py

For every inductees/<name>/copy.html this writes site/<name>.html and copies the page's
web images to site/media/<name>/. The chrome (head, header, footer) is taken from
site/inductees.html so the profile pages cannot drift from the rest of the site.
"""
import html, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
chrome = open(os.path.join(SITE, "inductees.html"), encoding="utf-8").read()
head, _, rest = chrome.partition('<main id="main" class="wide">')
_, _, foot = rest.partition("</main>")
head = head.replace('<li><a href="inductees.html" aria-current="page">', '<li><a href="inductees.html">')
foot = foot.replace('<li><a href="inductees.html" aria-current="page">', '<li><a href="inductees.html">')

def strip_dark_mode(css_html):
    """Remove every @media (prefers-color-scheme:dark){...} block, balancing braces."""
    out, i, key = [], 0, "@media (prefers-color-scheme:dark){"
    while True:
        j = css_html.find(key, i)
        if j < 0:
            return "".join(out) + css_html[i:]
        out.append(css_html[i:j])
        depth, k = 1, j + len(key)
        while depth:
            depth += {"{": 1, "}": -1}.get(css_html[k], 0)
            k += 1
        i = k


base = os.path.join(ROOT, "inductees")
for name in sorted(os.listdir(base)):
    src = os.path.join(base, name, "copy.html")
    if not os.path.exists(src):
        continue
    frag = open(src, encoding="utf-8").read()
    person = re.search(r"<h1>(.+?)</h1>", frag).group(1)
    standfirst = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="standfirst">(.+?)</p>', frag, re.S).group(1)))
    desc = html.escape(" ".join(standfirst.split())[:200], quote=True)

    media_out = os.path.join(SITE, "media", name)
    os.makedirs(media_out, exist_ok=True)
    for f in os.listdir(os.path.join(base, name, "media", "web")):
        shutil.copy2(os.path.join(base, name, "media", "web", f), os.path.join(media_out, f))
    frag = frag.replace('src="media/web/', f'src="media/{name}/')
    # The demo site is light-only (site.css sets color-scheme:light), so drop the profile's
    # own dark-mode rules here. The WordPress package in handover/ keeps them.
    frag = strip_dark_mode(frag)
    # The page's own <h1> is the person's name; drop the WordPress-only comment about it.
    frag = re.sub(r"<!-- If your theme already prints.*?-->\n", "", frag)

    page_head = re.sub(r"<title>.*?</title>", f"<title>{person} | Immigrant Hall of Honor</title>", head)
    page_head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + desc, page_head)
    page_head = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{person} | Immigrant Hall of Honor", page_head)
    page_head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + desc, page_head)

    out = (page_head + '<main id="main" class="profile-page">\n'
           + '<p class="crumb"><a href="inductees.html">&larr; All inductees</a></p>\n'
           + frag + "\n</main>" + foot)
    open(os.path.join(SITE, f"{name}.html"), "w", encoding="utf-8", newline="\n").write(out)
    print(f"site/{name}.html")
