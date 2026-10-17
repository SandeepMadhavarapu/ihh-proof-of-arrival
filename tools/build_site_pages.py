#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap each published inductee profile in the demo site's page chrome.

    python3 tools/build_profile.py --all      # first
    python3 tools/build_site_pages.py

Only the slugs listed in site-data/published.json are published: for each one this writes
site/<slug>.html and copies the page's web images to site/media/<slug>/. A folder under
inductees/ that is not on that list is never published, whatever it contains. It also writes
site/new.html ("New at the Museum") from site-data/new-at-the-museum.json, which only the
approval step (living/publisher.py, through a reviewed pull request) ever appends to.
The chrome (head, header, footer) is taken from site/inductees.html so generated pages cannot
drift from the rest of the site. This script reads nothing under living/.
"""
import datetime, html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape


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


def published_slugs(root):
    path = os.path.join(root, "site-data", "published.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    slugs = data["published"]
    if not isinstance(slugs, list) or not all(isinstance(s, str) and re.fullmatch(r"[a-z0-9-]+", s) for s in slugs):
        sys.exit(f"{path}: 'published' must be a list of lowercase slugs")
    return slugs


def chrome(site):
    with open(os.path.join(site, "inductees.html"), encoding="utf-8") as f:
        page = f.read()
    head, _, rest = page.partition('<main id="main" class="wide">')
    _, _, foot = rest.partition("</main>")
    head = head.replace('<li><a href="inductees.html" aria-current="page">', '<li><a href="inductees.html">')
    foot = foot.replace('<li><a href="inductees.html" aria-current="page">', '<li><a href="inductees.html">')
    return head, foot


def retitle(head, title, desc):
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, head)
    return re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, head)


def nice_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def build_new_page(root, site, head, foot, names):
    with open(os.path.join(root, "site-data", "new-at-the-museum.json"), encoding="utf-8") as f:
        feed = json.load(f)
    entries = sorted(feed.get("entries", []), key=lambda e: (e["date"], e["id"]), reverse=True)
    items = []
    for e in entries:
        if e["slug"] not in names:
            continue  # never link to a page that is not published
        srcs = "; ".join(f'<a href="{E(s["url"])}" rel="noopener">{E(s["title"])}</a> ({E(s["institution"])})'
                         for s in e["sources"])
        items.append(f'''  <li class="new-item">
    <p class="new-meta"><time datetime="{E(e["date"])}">{nice_date(e["date"])}</time> &middot; <a href="{E(e["slug"])}.html">{E(names[e["slug"]])}</a></p>
    <p class="new-text">{E(e["sentence"])}</p>
    <p class="new-src">Source{"s" if len(e["sources"]) > 1 else ""}: {srcs}</p>
  </li>''')
    body = ('<ol class="new-list">\n' + "\n".join(items) + "\n</ol>") if items else (
        '<p class="note new-empty">Nothing new yet. When our team has checked a new discovery '
        'against its original source and approved it, it will appear here with that source.</p>')
    main = f'''<main id="main" class="wide">

<h1>New at the Museum</h1>
<p class="lede">Fresh discoveries about our inductees, newest first. Each one was found in a
trusted archive or reference work, checked word for word against that source, and approved by a
person on our team before it was added to the inductee&rsquo;s page.</p>

{body}
</main>'''
    title = "New at the Museum | Immigrant Hall of Honor"
    desc = "Recently checked and approved discoveries about the inductees, each with its source."
    out = retitle(head, title, desc) + main + foot
    with open(os.path.join(site, "new.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"site/new.html ({len(items)} entr{'y' if len(items) == 1 else 'ies'})")


def main(root=ROOT):
    site = os.path.join(root, "site")
    base = os.path.join(root, "inductees")
    head, foot = chrome(site)
    slugs = published_slugs(root)
    for name in sorted(os.listdir(base)):
        if os.path.isdir(os.path.join(base, name)) and name not in slugs:
            print(f"not published (not in site-data/published.json): inductees/{name}")
    names = {}
    for name in slugs:
        src = os.path.join(base, name, "copy.html")
        if not os.path.exists(src):
            sys.exit(f"site-data/published.json lists '{name}' but inductees/{name}/copy.html does not exist")
        with open(src, encoding="utf-8") as f:
            frag = f.read()
        person = re.search(r"<h1>(.+?)</h1>", frag).group(1)
        names[name] = html.unescape(person)
        standfirst = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="standfirst">(.+?)</p>', frag, re.S).group(1)))
        desc = html.escape(" ".join(standfirst.split())[:200], quote=True)

        media_out = os.path.join(site, "media", name)
        os.makedirs(media_out, exist_ok=True)
        for f in os.listdir(os.path.join(base, name, "media", "web")):
            shutil.copy2(os.path.join(base, name, "media", "web", f), os.path.join(media_out, f))
        frag = frag.replace('src="media/web/', f'src="media/{name}/')
        # The demo site is light-only (site.css sets color-scheme:light), so drop the profile's
        # own dark-mode rules here. The WordPress package in handover/ keeps them.
        frag = strip_dark_mode(frag)
        # The page's own <h1> is the person's name; drop the WordPress-only comment about it.
        frag = re.sub(r"<!-- If your theme already prints.*?-->\n", "", frag)

        page_head = retitle(head, f"{person} | Immigrant Hall of Honor", desc)
        out = (page_head + '<main id="main" class="profile-page">\n'
               + '<p class="crumb"><a href="inductees.html">&larr; All inductees</a></p>\n'
               + frag + "\n</main>" + foot)
        with open(os.path.join(site, f"{name}.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        print(f"site/{name}.html")
    build_new_page(root, site, head, foot, names)


if __name__ == "__main__":
    main()
