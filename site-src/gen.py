#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render verify.html from cases.py.

Run from anywhere:  python3 gen.py
Paths are resolved relative to this file, so a fresh extraction works unchanged.
"""
import html, json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))  # site-src/: generator and its data
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")  # site/: deployable output only
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from cases import CASES
from voices import render as voices_render

# One definition of the verdicts, shared with visitor findings (voices/core.py). margin-notes.js
# keeps its own copy for the browser; tests/test_anchored_responses.py checks the two match.
from voices.core import VERDICTS as _VERDICTS
VERDICTS = list(_VERDICTS.items())
LABEL = dict(VERDICTS)
TAGTEXT = {
 "RECORD":"Record", "QUOTATION":"Quotation", "PARAPHRASE":"Paraphrase",
 "INFERENCE":"Our inference", "UNRESOLVED":"Unresolved", "NOT-READ":"Not read at source",
}

def ev_html(items):
    out=[]
    for tag,title,body,ref,url in items:
        cite = (f'<a href="{url}" rel="noopener">{ref}</a>' if url else ref)
        out.append(
          f'      <li class="ev-item" data-tag="{tag}">\n'
          f'        <p class="ev-t"><span class="tag-{tag.lower().replace("-","")}">'
          f'{TAGTEXT[tag]}</span> {title}</p>\n'
          f'        <p>{body}</p>\n'
          f'        <p class="ev-ref">{cite}</p></li>')
    return "\n".join(out)

def claim_report(cfg, cl):
    """No-JS route to "Report or add to this claim"; margin-notes.js adds the button."""
    if cfg["adapter"] == "none":
        return ""
    href = voices_render.nojs_href(cfg, "verify", cl["id"])
    link = (f'<a class="vv-nojs vv-ui" href="{html.escape(href)}">Report or add to this claim</a>' if href else "")
    return f'\n    <p class="vv-claim">{link}</p>'


def inductee_options():
    with open(os.path.join(ROOT, "site-data", "published.json"), encoding="utf-8") as f:
        slugs = json.load(f)["published"]
    opts = []
    for s in slugs:
        with open(os.path.join(ROOT, "inductees", s, "copy.md"), encoding="utf-8") as f:
            name = re.search(r"^# (.+)$", f.read(), re.M).group(1).strip()
        opts.append(f'      <option value="{s}">{html.escape(name)}</option>')
    return "\n".join(opts)


def tell_html(cfg):
    """The general "Spot something? Tell us" form. Sent by margin-notes.js, or without
    JavaScript straight to the demo's form handler; WordPress and email say what to do instead."""
    if cfg["adapter"] == "none":
        return ""
    # Never a GET form: without the demo's handler, the form stays hidden until the script runs,
    # so nothing a visitor types can end up in an address bar.
    action = ' method="post" action="/voices/form"' if cfg["adapter"] == "demo" else ' method="post" hidden'
    nojs = ""
    if cfg["adapter"] == "email":
        addr = html.escape(cfg["email"]["address"])
        nojs = f'<noscript><p class="note">Without JavaScript, email the curators at <a href="mailto:{addr}">{addr}</a>.</p></noscript>'
    elif cfg["adapter"] == "wordpress":
        nojs = '<noscript><p class="note">Without JavaScript, use the comment form at the end of this page.</p></noscript>'
    return f'''
<section class="vv-tell" id="tell" aria-labelledby="tell-h">
  <h2 id="tell-h">Spot something? Tell us</h2>
  <p>Know something about one of our inductees that we have missed, or think we have
  something wrong? Tell a curator. A person reads every message, and nothing on a page
  changes until a curator has checked it against a trusted source.</p>
  {nojs}
  <form class="vv-form" id="vv-tell-form"{action}>
    <input type="hidden" name="kind" value="tip"><input type="hidden" name="type" value="more">
    <label for="tell-inductee">Which inductee is it about?</label>
    <select id="tell-inductee" name="inductee">
{inductee_options()}
      <option value="general">Someone else, or the museum in general</option>
    </select>
    <label for="tell-text">What you know</label>
    <textarea id="tell-text" name="text" maxlength="1000" rows="5" required></textarea>
    <label for="tell-source">Your source <span class="vv-opt">(optional: a book, website, record or family document)</span></label>
    <input type="text" id="tell-source" name="source" maxlength="300">
    <label for="tell-rel">How you know <span class="vv-opt">(optional, for example: family member, teacher, researcher)</span></label>
    <input type="text" id="tell-rel" name="relationship" maxlength="100">
    <p class="vv-kid" id="tell-kid">{voices_render.under13()}</p>
    <label for="tell-name">First name <span class="vv-opt">(optional)</span></label>
    <input type="text" id="tell-name" name="name" maxlength="40" autocomplete="given-name" aria-describedby="tell-kid">
    <label for="tell-email">Email <span class="vv-opt">(optional, never shown; only so a curator can reply)</span></label>
    <input type="email" id="tell-email" name="email" maxlength="120" autocomplete="email" aria-describedby="tell-kid">
    <div class="vv-hp" aria-hidden="true"><label for="tell-website">Leave this empty</label><input type="text" id="tell-website" name="website" tabindex="-1" autocomplete="off"></div>
    <p class="vv-err" role="alert" hidden></p>
    <button type="submit" class="vv-send">Send to a curator</button>
  </form>
  <p class="vv-done" id="vv-tell-done" role="status" tabindex="-1" hidden></p>
</section>
'''


def claim_html(c, cl, i, total, cfg, findings=()):
    tag = ('<span class="cl-tag live">Published on immigranthallofhonor.org</span>'
           if cl["origin"]=="live" else
           '<span class="cl-tag ours">This exhibit&rsquo;s own claim</span>')
    opts="\n".join(
      '        <label><input type="radio" name="v-%s" value="%s"><span>%s</span></label>'
      %(cl["id"],v,lab) for v,lab in VERDICTS)
    cites="\n".join(
      '        <label><input type="radio" name="s-%s" value="%d"><span><b>%d.</b> %s</span></label>'
      %(cl["id"],k+1,k+1,e[1]) for k,e in enumerate(cl["evidence"]))
    cites+=('\n        <label class="none"><input type="radio" name="s-%s" value="0">'
            '<span>None of it &mdash; I am not convinced</span></label>'%cl["id"])
    n=len(cl["evidence"])
    return f'''  <li class="cl" id="{cl['id']}" data-verdict="{cl['verdict']}" data-origin="{cl['origin']}"
      data-case="{c['name']}" data-n="{i}">
    <div class="cl-head">{tag}<h3 class="cl-n">Claim {i} of {total}</h3></div>
    <blockquote class="cl-text">{cl['text']}</blockquote>
    <p class="cl-where">{cl['where']}</p>

    <details class="ev">
      <summary>Open the evidence<span class="cnt">{n} item{'s' if n!=1 else ''}</span></summary>
      <ol class="ev-list">
{ev_html(cl["evidence"])}
      </ol>
    </details>

    <fieldset class="vd">
      <legend>Record your finding</legend>
      <div class="vd-opts">
{opts}
      </div>
    </fieldset>

    <fieldset class="cite">
      <legend>Which piece of evidence settled it?</legend>
      <div class="cite-opts">
{cites}
      </div>
    </fieldset>

    <details class="cur">
      <summary>The curator&rsquo;s finding</summary>
      <p class="stamp {cl['verdict']}">{LABEL[cl['verdict']]}</p>
      <p>{cl['reasoning']}</p>
      <p class="lesson"><b>What this one teaches.</b> {cl['lesson']}</p>
    </details>{voices_render.findings_block(cl['id'], cl['text'], list(findings))}{claim_report(cfg, cl)}
  </li>'''

def main(site=SITE, voices=None):
    """`site` and `voices` are only ever overridden by voices/demo_server.py, for its own copy."""
    cfg = voices_render.load_config(ROOT, voices)
    on = cfg["adapter"] != "none"
    # Approved visitor findings, each tied to its claim id. The demo's own build draws none here;
    # its findings arrive through margin-notes.js instead.
    findings = voices_render.load_findings(ROOT) if voices is None else []
    known = {cl["id"] for c in CASES for cl in c["claims"]}
    for f in findings:
        if f.get("anchor") not in known:
            print(f"  FLAGGED for the moderator: finding {f.get('id', '?')} is on claim {f.get('anchor') or '-'}, "
                  f"which no longer exists; not shown")
    shell=open(os.path.join(site,"about.html"),encoding="utf-8").read()
    head=shell[shell.index("<body>"):shell.index("</header>")+len("</header>")]
    foot=shell[shell.index('<footer class="site-foot">'):]

    sections=[]
    for c in CASES:
        t=len(c["claims"])
        claims="\n\n".join(claim_html(c,cl,i+1,t,cfg,findings) for i,cl in enumerate(c["claims"]))
        sections.append(f'''<section class="case" id="case-{c['id']}" aria-labelledby="h-{c['id']}">
  <p class="case-kick">Case file &mdash; arrived {c['arrived']} from {c['from']}</p>
  <h2 id="h-{c['id']}">{c['name']}</h2>
  <p class="case-note">{c['note']}</p>
  <ol class="claims">
{claims}
  </ol>
</section>''')

    TOTAL=sum(len(c["claims"]) for c in CASES)
    LIVE=sum(1 for c in CASES for cl in c["claims"] if cl["origin"]=="live")
    OURS=TOTAL-LIVE
    FAIL=sum(1 for c in CASES for cl in c["claims"]
             if cl["origin"]=="live" and cl["verdict"]!="confirmed")
    HELD=LIVE-FAIL
    OURFAIL=sum(1 for c in CASES for cl in c["claims"]
                if cl["origin"]=="ours" and cl["verdict"]!="confirmed")
    EV=sum(len(cl["evidence"]) for c in CASES for cl in c["claims"])
    LINKED=sum(1 for c in CASES for cl in c["claims"] for e in cl["evidence"] if e[4])

    jump="\n".join('    <li><a href="#case-%s">%s</a></li>'%(c["id"],c["name"]) for c in CASES)

    attrs = voices_render.page_attrs(cfg, "verify") if on else ""
    main_html=f'''<main id="main" class="wide"{attrs}>

<section class="hero vd-hero">
  <p class="kicker">An interactive exhibit</p>
  <h1>The Verification Desk</h1>
  <p class="lede">Examine the claim. Open the evidence. Record your finding, then say which
  piece of evidence settled it. There is no timer, no score and no way to lose &mdash; you
  can change any verdict at any time, and the curator&rsquo;s reasoning appears whether you
  agree with it or not.</p>
</section>

<section class="tally-band">
  <h2>What is on the desk</h2>
  <ul class="tally">
    <li><b>{TOTAL}</b><span>claims</span></li>
    <li><b>{LIVE}</b><span>published on the live IHH site</span></li>
    <li><b>{FAIL}</b><span>of those did not survive</span></li>
    <li><b>{OURFAIL}</b><span>of our own claims did not survive either</span></li>
    <li><b>{EV}</b><span>pieces of evidence, {LINKED} of them linked to the source</span></li>
  </ul>
  <p class="tally-note"><b>This is not a random sample, and it is not a one-way audit.</b>
  {HELD} of the {LIVE} live-site claims held up perfectly. {OURFAIL} of our own {OURS} claims
  did not &mdash; including one where <b>the museum was right and this exhibit was wrong</b>,
  and one where we had been quoting a document nobody on this project had ever opened. Those
  are on the desk under their own names. Every live-site claim was read on <b>2&nbsp;October 2026</b> and re-checked on
  <b>3&nbsp;October</b>, through an automated fetch rather than by viewing source &mdash; so
  confirm exact punctuation at the page before quoting it. One claim we made about the live
  site has already been <b>withdrawn</b> on re-reading: see the note below.</p>
</section>

<section class="frame-note">
  <h2>A word about using a sponsor&rsquo;s own mistakes</h2>
  <p>The Immigrant Hall of Honor is a small volunteer non-profit doing something worth doing,
  and every error here is the kind every museum has. We put them on display because
  <b>the museums with the most authority are the ones that publish their own corrections</b>
  &mdash; and because we were willing to put ours on the same desk.</p>
  <p>They have already demonstrated the point. An earlier version of this audit led with the
  claim that IHH ran two contradictory copyright regimes on its story forms. On re-reading
  the live forms they have harmonised them, and <b>that criticism is withdrawn</b>.</p>
  <p class="muted">A case file is a list of claims and a list of sources. The claims can come
  from anywhere &mdash; a textbook, a newspaper, a family story, a chatbot. We built these on
  the live site because those errors are real, checkable today, and ours to help fix.</p>
</section>

<nav class="jump-cases" aria-label="Case files">
  <p class="jump-lab">Case files</p>
  <ul>
{jump}
  </ul>
</nav>

<div class="desk-status" id="status" role="status" aria-live="polite">
  <p><b><span id="done">0</span> of {TOTAL}</b> findings recorded.</p>
</div>

{chr(10).join(sections)}

<section class="sheet" id="sheet">
  <h2>Your finding sheet</h2>
  <p class="sub">Builds itself as you work. Nothing is sent anywhere &mdash; it lives in this
  browser tab and disappears when you close it.</p>
  <div id="sheet-body"><p class="sheet-empty">No findings recorded yet. Start with any case file above.</p></div>
  <p class="cta">
    <button type="button" class="btn small" id="copy-sheet">Copy my findings</button>
    <button type="button" class="btn ghost small" id="print-sheet">Print</button>
    <button type="button" class="btn ghost small" id="clear-sheet">Clear all</button>
  </p>
  <p class="note" id="copy-note" hidden></p>
</section>
{tell_html(cfg)}
<section class="colleague">
  <h2>Why a museum would build this</h2>
  <p>Every other way of making a history site &ldquo;engaging&rdquo; asks the visitor to trust
  it more. This one asks them to trust it less, and hands them the tools. The claims are real,
  the errors are real and still live, and the evidence is named and linked well enough that a
  visitor can go and disagree with us &mdash; which, on four of these claims, would have been
  the right call.</p>
  <p>It is also the cheapest thing here to extend. A new case file is a list of claims and a
  list of sources in <code>cases.py</code> &mdash; no new code, no new design, no developer.</p>
  <p class="cta"><a class="btn" href="method.html">How this was made, and what we refused to build</a></p>
</section>

</main>'''

    out=(shell[:shell.index("<body>")]
         .replace("<title>About | Immigrant Hall of Honor</title>",
                  "<title>The Verification Desk | Immigrant Hall of Honor</title>")
         .replace('content="About | Immigrant Hall of Honor"',
                  'content="The Verification Desk | Immigrant Hall of Honor"')
         .replace('content="Who we are, what we hold, and how to reach us."',
                  f'content="Examine a claim, open the evidence, record your finding. {TOTAL} real claims about five immigrants, {EV} named sources, no timer and no score."')
         + head + "\n" + main_html + "\n" + foot)
    # this page is the current one
    out = out.replace(' href="about.html" aria-current="page"', ' href="about.html"')
    out = out.replace('<li><a href="verify.html">Verify</a></li>',
                      '<li><a href="verify.html" aria-current="page">Verify</a></li>')
    if on or findings:
        out = out.replace("</head>", '<link rel="stylesheet" href="assets/margin-notes.css">\n</head>', 1)
    if on:
        out = out.replace("</body>", '<script src="assets/margin-notes.js" defer></script>\n</body>', 1)
    path=os.path.join(site,"verify.html")
    open(path,"w",encoding="utf-8",newline="\n").write(out)
    print(f"verify.html: {TOTAL} claims, {EV} evidence items ({LINKED} linked), {len(out)} chars")

if __name__=="__main__":
    main()
