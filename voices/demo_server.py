"""Local DEMO of Visitor Voices: the site with notes switched on, plus a moderator page.

    python -m voices.demo_server            # then open http://127.0.0.1:8770/muir.html
    python -m voices.demo_server --reset    # start again with an empty queue

Everything stays on this computer, under voices/.demo/ (gitignored): a private copy of the
site built with the "demo" adapter, the moderation items, their audit log, and a separate
Living Museum queue for tips. It never touches site/, living/proposals/ or anything online.
Every page it serves says DEMO at the top. It listens on 127.0.0.1 only.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import secrets
import shutil
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from living.proposals import Store as LivingStore, verify_chain  # noqa: E402
from voices import bridge  # noqa: E402
from voices.anchors import passages, reattach  # noqa: E402
from voices.core import CONFIRMATION, ID_RE, TYPES, UNDER_13, RateLimit, Store, public, validate  # noqa: E402

DEMO = ROOT / "voices" / ".demo"
SITE = DEMO / "site"
PORT = 8770
CONFIG = {"adapter": "demo"}
TOKEN = secrets.token_urlsafe(24)
LOCK = threading.Lock()
LIMIT = RateLimit()
E = html.escape

BANNER_CSS = ("<style>.vv-demo-banner{margin:0;padding:.55rem 1rem;background:#1a1714;color:#fff;"
              "font:600 .9rem/1.4 system-ui,sans-serif;text-align:center}.vv-demo-banner a{color:#fff}</style>\n")
BANNER = ('<p class="vv-demo-banner" role="note">DEMO &middot; a local demonstration. Notes are stored on '
          'this computer only and nothing is sent to the Immigrant Hall of Honor. '
          '<a href="/voices/moderate">Moderator page</a></p>')


def _load_gen():
    spec = importlib.util.spec_from_file_location("ihh_gen", ROOT / "site-src" / "gen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build() -> None:
    """Copy site/ to voices/.demo/site and rebuild its profile and Verify pages with notes on."""
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "site", SITE)
    from tools import build_site_pages
    build_site_pages.main(str(ROOT), site=str(SITE), voices=CONFIG)
    _load_gen().main(site=str(SITE), voices=CONFIG)
    shutil.copy2(ROOT / "voices" / "demo_adapter.js", SITE / "assets" / "demo-adapter.js")
    for page in SITE.glob("*.html"):
        s = page.read_text(encoding="utf-8")
        s = s.replace("</head>", BANNER_CSS + "</head>", 1).replace("<body>", "<body>\n" + BANNER, 1)
        s = s.replace('<script src="assets/margin-notes.js" defer>',
                      '<script src="assets/demo-adapter.js" defer></script>\n<script src="assets/margin-notes.js" defer>')
        page.write_text(s, encoding="utf-8", newline="\n")


def store() -> Store:
    return Store(DEMO / "moderation")


def living() -> LivingStore:
    return LivingStore(DEMO / "living-proposals")


def claims() -> dict[str, str]:
    cases = _load_gen().CASES
    return {cl["id"]: " ".join(html.unescape(re.sub(r"<[^>]+>", "", cl["text"])).split())
            for c in cases for cl in c["claims"]}


def claim_cases() -> dict[str, str]:
    """claim id -> inductee slug (each Verify case file is named by its inductee's slug)."""
    return {cl["id"]: c["id"] for c in _load_gen().CASES for cl in c["claims"]}


def page_passages(page: str) -> dict[str, str]:
    path = SITE / f"{page}.html"
    return passages(path.read_text(encoding="utf-8")) if ID_RE.fullmatch(page) and path.is_file() else {}


def approved_notes(page: str) -> list[dict]:
    texts, out = page_passages(page), []
    for item in store().all():
        if item["status"] != "approved" or item["kind"] != "note" or item["page"] != page:
            continue
        aid, how = reattach(item["anchor"], item["selector"], texts)
        if aid:
            out.append(dict(public(item), anchor=aid, attached=how))
    return out


def receive(form: dict, client: str) -> tuple[int, str]:
    sub, errors = validate(form)
    if errors == ["spam"]:
        return 200, CONFIRMATION                     # say thanks, keep nothing
    if errors:
        return 400, "; ".join(errors)
    if not LIMIT.allow(client):
        return 429, "You have sent several notes in the last few minutes. Please wait a little and try again."
    with LOCK:
        item = store().add(sub, "demo")
        if bridge.eligible(item):
            pid = bridge.to_living(item, living(), claim_cases().get(item["anchor"], "") if item["kind"] == "claim" else "")
            store().link_proposal(item["id"], pid)
    return 200, CONFIRMATION


def page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | DEMO</title>
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/margin-notes.css">
{BANNER_CSS}<style>main{{max-width:52rem;margin:1.5rem auto;padding:0 16px}}
.vv-mod{{border:1px solid #8a8378;border-radius:6px;padding:1rem;margin:0 0 1rem;background:#fbfaf8;overflow-wrap:anywhere}}
.st{{font:600 .8rem system-ui;text-transform:uppercase;letter-spacing:.05em}} .flag{{color:#7a2e1e;font-weight:700}}
.vv-form button{{margin-right:.5rem}} table{{border-collapse:collapse}} td,th{{text-align:left;padding:.2rem .5rem;vertical-align:top}}</style>
</head><body>{BANNER}<main id="main">{body}</main></body></html>"""


def nojs_form(q: dict) -> str:
    pg, passage = q.get("page", [""])[0], q.get("passage", [""])[0]
    if pg == "verify" and passage:
        quote, kind, heading = claims().get(passage, ""), "claim", "Report or add to this claim"
    elif passage:
        quote, kind, heading = page_passages(pg).get(passage, ""), "note", "Add a note"
    else:
        quote, kind, heading = "", "tip", "Spot something? Tell us"
    if kind != "tip" and not quote:
        return page("Not found", "<h1>That passage was not found</h1><p>It may have changed. <a href='/'>Back to the site</a></p>")
    types = "".join(f'<label class="vv-type"><input type="radio" name="type" value="{k}"{" checked" if (k == "wrong" and kind == "claim") or (k == "more" and kind == "tip") else ""}> {E(v)}</label>'
                    for k, v in TYPES.items())
    return page(heading, f"""<h1>{E(heading)}</h1>
{f'<p class="vv-ctx-l">On this passage:</p><blockquote class="vv-ctx">{E(quote)}</blockquote>' if quote else ''}
<form class="vv-form" method="post" action="/voices/form">
<input type="hidden" name="kind" value="{kind}"><input type="hidden" name="page" value="{E(pg)}"><input type="hidden" name="anchor" value="{E(passage)}">
<fieldset><legend>What kind of note is it?</legend>{types}</fieldset>
<label for="t">Your note</label><textarea id="t" name="text" maxlength="1000" rows="6" required></textarea>
<label for="s">Where did you learn this? <span class="vv-opt">(optional: a book, website or record)</span></label><input type="text" id="s" name="source" maxlength="300">
<p class="vv-kid" id="kid">{E(UNDER_13)}</p>
<label for="n">First name <span class="vv-opt">(optional, shown with your note)</span></label><input type="text" id="n" name="name" maxlength="40" aria-describedby="kid">
<label for="m">Email <span class="vv-opt">(optional, never shown; only so a curator can reply)</span></label><input type="email" id="m" name="email" maxlength="120" aria-describedby="kid">
<div class="vv-hp" aria-hidden="true"><label for="w">Leave this empty</label><input type="text" id="w" name="website" tabindex="-1" autocomplete="off"></div>
<button type="submit" class="vv-send">Send to a curator</button></form>""")


def moderate_page() -> str:
    ok, chain = verify_chain(store().audit_log)
    rows = []
    items = sorted(store().all(), key=lambda i: (i["status"] != "pending", i["id"]))
    cl = claims()
    for it in items:
        where = ""
        if it["kind"] == "note":
            aid, how = reattach(it["anchor"], it["selector"], page_passages(it["page"]))
            where = (f'<p class="flag">FLAGGED: this note no longer matches any passage on {E(it["page"])}. It will not be shown. '
                     f'Re-attach it by hand or reject it.</p>' if aid is None else
                     f'<p>Attaches to <code>{E(aid)}</code> ({E(how)}). <a href="/{E(it["page"])}.html#{E(aid)}">See the passage</a></p>')
            quote = it["selector"].get("exact", "")
        elif it["kind"] == "claim":
            quote = cl.get(it["anchor"], "")
            where = f'<p>Claim <code>{E(it["anchor"])}</code> on the <a href="/verify.html#{E(it["anchor"])}">Verify page</a></p>'
        else:
            quote, where = "", f'<p>General tip about <b>{E(it["inductee"])}</b></p>'
        act = (f'''<form class="vv-form" method="post" action="/voices/moderate"><input type="hidden" name="token" value="{TOKEN}">
<input type="hidden" name="id" value="{E(it['id'])}"><label for="by-{E(it['id'])}">Your name</label>
<input type="text" id="by-{E(it['id'])}" name="by" required><label for="why-{E(it['id'])}">Reason (optional)</label>
<input type="text" id="why-{E(it['id'])}" name="why"><button class="vv-send" name="action" value="approve">Approve</button>
<button class="vv-send" name="action" value="reject">Reject</button></form>''' if it["status"] == "pending" else
               "".join(f'<p class="st">{E(d["action"])}d by {E(d["by"])} at {E(d["at"])} {E(d["why"])}</p>' for d in it["decisions"]))
        rows.append(f'''<section class="vv-mod" id="{E(it['id'])}"><p class="st">{E(it['id'])} &middot; {E(it['status'])} &middot; {E(it['kind'])} &middot; {E(TYPES[it['type']])} &middot; {E(it['page'])}</p>
{where}{f'<blockquote class="vv-ctx">{E(quote)}</blockquote>' if quote else ''}
<p><b>Visitor wrote:</b></p><p class="vv-text">{E(it['text'])}</p>
<table><tr><th>Source</th><td>{E(it['source']) or '&mdash;'} {'(plain text, not a link)' if it['source'] else ''}</td></tr>
<tr><th>Relationship</th><td>{E(it.get('relationship', '')) or '&mdash;'}</td></tr>
<tr><th>Name</th><td>{E(it['name']) or '&mdash;'} (shown as &ldquo;{E(public(it)['by'])}&rdquo;)</td></tr>
<tr><th>Email</th><td>{'given; kept in the item file for a reply, never shown on any page' if it['email'] else '&mdash;'}</td></tr>
<tr><th>Living Museum</th><td>{E(it['living_proposal']) or '&mdash;'}</td></tr></table>{act}</section>''')
    tips = [p for p in living().all()]
    tip_rows = "".join(f'''<tr><td>{E(p.id)}</td><td>{E(p.kind)}</td><td>{E(p.slug)}</td><td>{E(p.status)} / {E(p.verdict)}</td>
<td>{E(p.finder.get("visitor_text", "")[:160])}</td><td>{E(p.finder.get("visitor_source", ""))}</td></tr>''' for p in tips)
    return page("Moderation queue", f"""<h1>Moderation queue</h1>
<p>Every note and report waits here until a person approves it. Only approved margin notes appear on
the site. Audit log: <b>{'intact' if ok else 'BROKEN'}</b> ({E(chain)}).</p>
{''.join(rows) or '<p>Nothing yet.</p>'}
<h2>Living Museum queue (demo copy)</h2>
<p>&ldquo;I know more&rdquo; and &ldquo;Something looks wrong&rdquo; reports that give a source become Living Museum
tips. A tip is not copy: a curator must find an exact span in a trusted source and file a fact proposal,
which then goes through the same five gates as every other fact.</p>
<table><tr><th>Proposal</th><th>Kind</th><th>Inductee</th><th>Status</th><th>Visitor text</th><th>Source given</th></tr>{tip_rows}</table>""")


class Handler(BaseHTTPRequestHandler):
    server_version = "IHH-voices-demo"

    def _host_ok(self) -> bool:
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def _same_origin(self) -> bool:
        origin = self.headers.get("Origin") or self.headers.get("Referer") or ""
        return origin.startswith((f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"))

    def _send(self, code: int, body: str | bytes, ctype: str = "text/html; charset=utf-8", extra=None) -> None:
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                         "style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self' mailto:")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def _body(self) -> bytes:
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(min(n, 20000))

    def do_GET(self):
        if not self._host_ok():
            return self._send(400, "bad host")
        u = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/voices/api/notes":
            return self._json(200, {"notes": approved_notes(q.get("page", [""])[0])})
        if u.path == "/voices/form":
            return self._send(200, nojs_form(q))
        if u.path == "/voices/moderate":
            return self._send(200, moderate_page())
        rel = urllib.parse.unquote(u.path).lstrip("/") or "index.html"
        path = (SITE / rel).resolve()
        if not path.is_relative_to(SITE.resolve()) or not path.is_file():
            return self._send(404, page("Not found", "<h1>Not found</h1>"))
        ctype = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                 ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".xml": "application/xml",
                 ".txt": "text/plain; charset=utf-8"}.get(path.suffix, "application/octet-stream")
        self._send(200, path.read_bytes(), ctype)

    def do_POST(self):
        if not self._host_ok() or not self._same_origin():
            return self._send(403, "forbidden")
        u = urllib.parse.urlsplit(self.path)
        client = self.client_address[0]
        if u.path == "/voices/api/submit":
            try:
                form = json.loads(self._body() or b"{}")
            except json.JSONDecodeError:
                return self._json(400, {"error": "bad request"})
            code, msg = receive(form if isinstance(form, dict) else {}, client)
            return self._json(code, {"ok": code == 200, "message": msg} if code == 200 else {"error": msg})
        form = {k: v[0] for k, v in urllib.parse.parse_qs(self._body().decode("utf-8", "replace")).items()}
        if u.path == "/voices/form":
            if form.get("kind") == "note":
                form["selector"] = {"exact": page_passages(form.get("page", "")).get(form.get("anchor", ""), "")}
            if form.get("kind") == "tip":
                form["page"] = form.get("inductee") or form.get("page") or "general"
            code, msg = receive(form, client)
            back = f'/{form.get("page", "")}.html' if form.get("kind") == "note" else "/verify.html"
            body = (f"<h1>Thank you</h1><p role='status'>{E(msg)}</p>" if code == 200 else
                    f"<h1>That did not send</h1><p role='alert'>{E(msg)}</p><p>Use your browser's Back button to fix it.</p>")
            return self._send(code, page("Thank you" if code == 200 else "Not sent", body + f'<p><a href="{E(back)}">Back to the page</a></p>'))
        if u.path == "/voices/moderate":
            if not secrets.compare_digest(form.get("token", ""), TOKEN) or not form.get("by", "").strip():
                return self._send(403, page("Not allowed", "<h1>Not allowed</h1><p>Reload the moderator page and give your name.</p>"))
            with LOCK:
                store().decide(form.get("id", ""), form.get("action", ""), form["by"].strip()[:60], form.get("why", "").strip())
            return self._send(303, "", extra={"Location": "/voices/moderate"})
        self._send(404, "not found")

    def log_message(self, fmt, *args):
        sys.stderr.write("demo: " + (fmt % args) + "\n")


def main() -> int:
    global PORT
    ap = argparse.ArgumentParser(description="Visitor Voices local DEMO (127.0.0.1 only)")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--reset", action="store_true", help="delete the demo's notes, audit log and tips first")
    a = ap.parse_args()
    PORT = a.port
    if a.reset:
        for sub in ("moderation", "living-proposals"):
            shutil.rmtree(DEMO / sub, ignore_errors=True)
    build()
    ThreadingHTTPServer.allow_reuse_address = False     # on Windows, reuse lets a second copy share the port
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"DEMO running: http://127.0.0.1:{PORT}/muir.html   moderator: http://127.0.0.1:{PORT}/voices/moderate   Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
