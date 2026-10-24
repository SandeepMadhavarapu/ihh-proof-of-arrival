"""PRIVATE review dashboard. Local only: binds to 127.0.0.1, never deployed, never linked from site/.

    python living/run.py review            # then open http://127.0.0.1:8765/

Server-rendered HTML with plain forms, so it works without JavaScript. Every decision needs a
reviewer name (and a reason to reject), is written to the proposal file, and is appended to the
audit log. "Approve" records the decision only. "Approve and create PR branch" also runs the
publisher on a new branch living/<ID> and commits; merging that pull request is the final approval.
"""
from __future__ import annotations

import difflib
import html
import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ..config import ROOT, PAUSED, check_not_paused, load_sources, registrable_domain
from ..proposals import Store, now
from ..publisher import PUBLISHABLE_VERDICTS, PublishError, append_to_section, publish

E = html.escape
TOKEN = secrets.token_urlsafe(24)
STYLE = """
:root{--ink:#1d1a16;--mut:#58524a;--bg:#fbfaf7;--card:#fff;--rule:#d8d2c6;--acc:#8c2b1b;--ok:#1d5e2e;--warn:#7a5200;--bad:#8c1b1b;--mark:#fff1b8}
@media (prefers-color-scheme:dark){:root{--ink:#ece7df;--mut:#b3ab9f;--bg:#15130f;--card:#1e1b16;--rule:#3b362e;--acc:#e29c87;--ok:#8fd19e;--warn:#e7c46b;--bad:#f0a19a;--mark:#4a3c10}}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--bg)}
main{max-width:70rem;margin:0 auto;padding:1rem}h1{font-size:1.5rem;margin:.5rem 0}
.banner{border:2px solid var(--acc);padding:.6rem .9rem;margin:0 0 1rem;font-weight:600}
nav a{margin-right:1rem;color:var(--ink)}a{color:var(--ink)}
.card{background:var(--card);border:1px solid var(--rule);padding:1rem;margin:1rem 0}
.row{display:grid;grid-template-columns:1fr 1fr;gap:1rem}@media (max-width:760px){.row{grid-template-columns:1fr}}
.badge{display:inline-block;border:1px solid currentColor;padding:0 .4rem;font-size:.8rem;margin-right:.3rem;border-radius:2px}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.mut{color:var(--mut);font-size:.9rem}
mark{background:var(--mark);color:var(--ink);padding:0 .1rem}blockquote{margin:.4rem 0;padding-left:.8rem;border-left:3px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:.9rem}td,th{border-top:1px solid var(--rule);padding:.3rem;text-align:left;vertical-align:top}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem;background:var(--bg);padding:.5rem;border:1px solid var(--rule)}
label{display:block;margin:.4rem 0 .1rem;font-weight:600}input[type=text],textarea{width:100%;font:inherit;padding:.4rem;border:1px solid var(--mut);background:var(--card);color:var(--ink)}
button{font:inherit;padding:.45rem .8rem;margin:.5rem .5rem 0 0;border:1px solid var(--ink);background:var(--card);color:var(--ink);cursor:pointer;min-height:44px}
button.primary{background:var(--ink);color:var(--bg)}:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
"""

VERDICT_CLASS = {"PASSED_ALL_GATES": "ok", "NEEDS_HUMAN_JUDGMENT": "warn", "CONFLICT": "warn", "REJECTED": "bad",
                 "NOT_VERIFIED": "mut"}
VERDICT_TEXT = {"PASSED_ALL_GATES": "Passed all gates", "NEEDS_HUMAN_JUDGMENT": "NEEDS HUMAN JUDGMENT",
                "CONFLICT": "CONFLICT — correction item", "REJECTED": "Rejected by the gates",
                "NOT_VERIFIED": "Not verified yet (run: python living/run.py verify)"}


def highlight(context: str, span: str) -> str:
    i = context.find(span)
    if i < 0:
        return E(context)
    return E(context[:i]) + "<mark>" + E(span) + "</mark>" + E(context[i + len(span):])


def diff_preview(p) -> str:
    if p.kind != "fact":
        return "<p class=mut>No automatic change: " + ("an editor changes the existing sentence by hand." if p.kind == "correction"
                                                       else "a person decides what to do with the published fact.") + "</p>"
    path = ROOT / "inductees" / p.slug / "copy.md"
    before = path.read_text(encoding="utf-8")
    try:
        after = append_to_section(before, p.section, f"{p.sentence} {{verified:{p.id}}}")
    except PublishError as exc:
        return f"<p class=bad>{E(str(exc))}</p>"
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(), f"inductees/{p.slug}/copy.md (now)",
                                f"inductees/{p.slug}/copy.md (if approved)", n=2, lineterm="")
    return "<pre>" + E("\n".join(diff)) + "</pre>"


def card(p, sources) -> str:
    checks = {c["url"]: c for c in p.gates.get("gate1", {}).get("checks", [])}
    ev_html = []
    for e in p.evidence:
        c = checks.get(e.url, {})
        tier = e.tier if e.tier is not None else sources.tier(e.url)
        by = e.retrieved_by or c.get("retrieved_by", "") or "not retrieved"
        by_label = {"human": "Retrieved by a person (saved in a browser)", "network": "Fetched by the system",
                    "fixture": "Offline test fixture"}.get(by, by)
        ctx = highlight(c["context"], " ".join(e.span.split())) if c.get("context") else f"<mark>{E(e.span)}</mark>"
        ev_html.append(f"""<div class=card><p><span class="badge {'ok' if tier == 1 else 'warn' if tier == 2 else 'bad'}">Tier {tier or '—'}</span>
<b>{E(registrable_domain(e.url))}</b> &middot; {f'<code>{E(e.url)}</code> (given by a visitor: not a link; check it by hand)' if e.retrieved_by == "visitor" else f'<a href="{E(e.url)}" rel="noopener noreferrer">open source</a>'}</p>
<p class=mut>{E(by_label)} {E(e.retrieved_at)} &middot; sha256 {E(e.sha256[:16]) or '—'}</p>
<blockquote>{ctx}</blockquote></div>""")
    rows = []
    for g, label in [("gate1", "1 Evidence (deterministic)"), ("gate2", "2 Corroboration"), ("gate3", "3 Meaning (blind judge)"),
                     ("gate4", "4 Conflict"), ("gate5", "5 Media rights")]:
        r = p.gates.get(g)
        if not r:
            rows.append(f"<tr><th>{label}</th><td class=mut>not run</td></tr>")
            continue
        if "status" in r:
            res, cls = r["status"], "warn" if r["status"].startswith("NEEDS") or r["status"] == "NOT RUN" else "ok" if r["status"] == "SUPPORTED" else "bad"
            detail = r.get("reason", "") + (" Unsupported: " + ", ".join(r.get("unsupported_words", [])) if r.get("unsupported_words") else "")
        elif r.get("required") is False:
            res, cls, detail = "not required", "mut", ""
        else:
            res, cls, detail = ("passed", "ok", "") if r.get("passed") else ("FAILED", "bad", "; ".join(r.get("reasons", [])))
        rows.append(f"<tr><th>{label}</th><td class={cls}>{E(res)}</td><td>{E(detail)}</td></tr>")
    domains = p.gates.get("gate2", {}).get("domains") or sorted({registrable_domain(e.url) for e in p.evidence})
    finder = p.finder or {}
    editor = "<p class=warn>The wording is the source's own sentence. An editor should rewrite it for ages 12–18 before approval (a rewrite is re-checked).</p>" if finder.get("needs_editor") else ""
    can_approve = p.status == "pending" and p.verdict in PUBLISHABLE_VERDICTS and p.kind == "fact"
    why_not = "" if can_approve else ("<p class=mut>Approval is disabled: " + (
        "the gates rejected it." if p.verdict == "REJECTED" else
        "this is a visitor's tip, not copy. If the source holds up, file a fact proposal with an exact span from it." if p.kind == "tip" else
        "this is a correction or re-verification item; an editor acts on it by hand." if p.kind != "fact" else
        f"status is {p.status}." if p.status != "pending" else f"verdict is {p.verdict}.") + "</p>")
    form = f"""<form method=post action="/decide"><input type=hidden name=token value="{TOKEN}"><input type=hidden name=id value="{p.id}">
<label for="by-{p.id}">Your name</label><input type=text id="by-{p.id}" name=by required autocomplete=name>
<label for="why-{p.id}">Reason (required to reject)</label><textarea id="why-{p.id}" name=reason rows=2></textarea>
{"<button class=primary name=action value=approve>Approve</button><button name=action value=approve_branch>Approve and create PR branch</button>" if can_approve else ""}
<button name=action value=reject>Reject</button></form>""" if p.status == "pending" else \
        f"<p><b>Decision:</b> {E(p.decision.get('action', p.status))} by {E(p.decision.get('by', '?'))} at {E(p.decision.get('at', ''))} {E(p.decision.get('reason', ''))}</p>"
    return f"""<section class=card id="{p.id}" aria-labelledby="h-{p.id}">
<h2 id="h-{p.id}">{p.id} &middot; {E(p.slug)} &middot; {E(p.kind)} <span class="badge {VERDICT_CLASS.get(p.verdict, 'mut')}">{E(VERDICT_TEXT.get(p.verdict, p.verdict))}</span></h2>
<p class=mut>Status: {E(p.status)} &middot; section: {E(p.section)} &middot; finder: {E(finder.get('mode', ''))} (confidence {E(str(finder.get('confidence', '—')))}) &middot; independent domains: {len(domains)} ({E(', '.join(domains))})</p>
<div class=row><div><h3>Proposed sentence</h3><blockquote>{E(p.sentence)}</blockquote>{editor}
{f"<h3>Visitor tip (not copy)</h3><blockquote>{E(finder.get('visitor_text', ''))}</blockquote><p class=mut>Source given: {E(finder.get('visitor_source', ''))}</p>" if p.kind == "tip" else ""}
{f"<p class=warn><b>Conflicts with:</b> {E(p.related)}</p>" if p.related else ""}
<h3>Gates</h3><table>{''.join(rows)}</table>
{"<ul>" + "".join(f"<li>{E(r)}</li>" for r in p.reasons) + "</ul>" if p.reasons else ""}</div>
<div><h3>Sources</h3>{''.join(ev_html)}</div></div>
<h3>Change preview</h3>{diff_preview(p)}{why_not}{form}</section>"""


def page(view: str) -> str:
    store, sources = Store(), load_sources()
    items = store.all()
    groups = {"pending": [p for p in items if p.status == "pending" and p.verdict != "REJECTED"],
              "rejected": [p for p in items if p.status == "rejected" or p.verdict == "REJECTED"],
              "decided": [p for p in items if p.status in ("approved", "published")]}
    shown = groups.get(view, groups["pending"])
    paused = f"<p class=banner>PAUSED: {E(str(PAUSED.relative_to(ROOT)))} exists. Decisions are disabled.</p>" if PAUSED.exists() else ""
    judge = "<p class=banner>No semantic judge is configured (no API key). Every proposal that passes the deterministic gates says NEEDS HUMAN JUDGMENT: you are the judge of meaning.</p>"
    import os
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        judge = ""
    nav = " ".join(f'<a href="/?view={k}"{" aria-current=page" if k == view else ""}>{k.title()} ({len(v)})</a>' for k, v in groups.items())
    body = "".join(card(p, sources) for p in shown) or "<p>Nothing here.</p>"
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content="noindex,nofollow"><title>Living Museum review queue (private)</title><style>{STYLE}</style></head>
<body><main><h1>Living Museum review queue</h1><p class=mut>Private, local only. Nothing here is public until a reviewed pull request is merged.</p>
{paused}{judge}<nav aria-label="Queue">{nav}</nav>{body}</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: str, headers: dict | None = None) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        q = urllib.parse.urlparse(self.path)
        if q.path != "/":
            return self._send(404, "not found")
        view = urllib.parse.parse_qs(q.query).get("view", ["pending"])[0]
        self._send(200, page(view))

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/decide":
            return self._send(404, "not found")
        length = min(int(self.headers.get("Content-Length", "0")), 20000)
        form = {k: v[0] for k, v in urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8")).items()}
        if not secrets.compare_digest(form.get("token", ""), TOKEN):
            return self._send(403, "bad or missing form token")
        try:
            check_not_paused()
            msg = decide(form.get("id", ""), form.get("action", ""), form.get("by", ""), form.get("reason", ""))
        except Exception as exc:
            return self._send(400, f"<p>{E(str(exc))}</p><p><a href='/'>Back</a></p>")
        self._send(303, msg, {"Location": "/?view=decided#" + form.get("id", "")})

    def log_message(self, fmt, *args):  # quiet; decisions are in the audit log
        pass


def decide(pid: str, action: str, by: str, reason: str) -> str:
    store = Store()
    p = store.get(pid)
    by, reason = by.strip(), reason.strip()
    if not by:
        raise ValueError("a reviewer name is required")
    if p.status != "pending":
        raise ValueError(f"{pid} is already {p.status}")
    old = p.status
    if action == "reject":
        if not reason:
            raise ValueError("a reason is required to reject")
        p.status = "rejected"
    elif action in ("approve", "approve_branch"):
        if p.verdict not in PUBLISHABLE_VERDICTS or p.kind != "fact":
            raise ValueError(f"{pid} cannot be approved (verdict {p.verdict}, kind {p.kind})")
        p.status = "approved"
    else:
        raise ValueError("unknown action")
    p.decision = {"by": by, "at": now(), "action": action, "reason": reason}
    store.update(p, by, action, reason or "approved in the review dashboard", old)
    if action == "approve_branch":
        publish(pid, store, reviewer=by, branch=True)
    return f"{pid}: {p.status}"


def serve(port: int = 8765) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Review queue (private, local only): http://127.0.0.1:{port}/   Ctrl+C to stop")
    httpd.serve_forever()
