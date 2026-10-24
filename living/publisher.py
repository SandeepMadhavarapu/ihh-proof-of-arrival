"""The approval step: the ONLY code that changes copy.md, a media manifest or site/.

`publish` applies one proposal that a named person has approved in the review dashboard:
  1. refuses unless status is "approved" and the gates allowed a human decision;
  2. re-fetches every source and re-runs the deterministic gates (a page may have changed
     since the approval); any failure aborts with nothing written;
  3. appends the sentence to its section of inductees/<slug>/copy.md with a {verified:ID} marker;
  4. adds each new source to media-manifest.csv as a cited reference row (existing bytes kept);
  5. records the evidence forever in inductees/<slug>/verified-facts.json;
  6. appends a visitor-facing entry to site-data/new-at-the-museum.json;
  7. rebuilds: tools/build_profile.py, tools/build_site_pages.py, tools/package_handover.sh,
     then qa/rebuild.sh must pass;
  8. with --branch: creates branch living/<ID>, commits, and writes the pull-request body to
     living/proposals/<ID>.pr.md. A person merging that pull request is the final approval.
It never sets MUSEUM READY and never pushes.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

from .config import ROOT, check_not_paused, load_sources, registrable_domain
from .fetch import Fetcher
from .gates import gate1, gate2
from .proposals import Proposal, Store
from .verifier import to_input

PUBLISHABLE_VERDICTS = ("PASSED_ALL_GATES", "NEEDS_HUMAN_JUDGMENT")


class PublishError(RuntimeError):
    pass


def _today() -> str:
    return dt.date.today().isoformat()


def append_to_section(md: str, section: str, paragraph: str) -> str:
    head, sep, rest = md.partition("\n---\n")
    story, sep2, extras = rest.partition("\n---\n")
    if not sep or not sep2:
        raise PublishError("copy.md does not have the head --- story --- extras layout")
    pattern = re.compile(r"(^## " + re.escape(section) + r"\n)(.*?)(?=^## |\Z)", re.S | re.M)
    m = pattern.search(story)
    if not m:
        raise PublishError(f"section '## {section}' not found in copy.md")
    body = m.group(2).rstrip("\n")
    new_body = body + "\n\n" + paragraph + "\n\n"
    story = story[:m.start(2)] + new_body + story[m.end(2):]
    return head + sep + story + sep2 + extras


def _manifest_rows(path: Path) -> tuple[list[str], list[dict], str]:
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(raw))
    return list(reader.fieldnames or []), list(reader), newline


def add_reference_rows(path: Path, p: Proposal, sources, today: str) -> list[str]:
    """Append a cited-reference row for every evidence URL not already in the manifest."""
    fields, rows, newline = _manifest_rows(path)
    by_url = {r.get("stable_item_url", ""): r["item_no"] for r in rows}
    next_no = max((int(r["item_no"]) for r in rows if r["item_no"].isdigit()), default=0) + 1
    items, new_lines = [], []
    for e in p.evidence:
        if e.url in by_url:
            items.append(by_url[e.url])
            continue
        note = sources.note(e.url)
        institution = note.split(" (")[0] if note else registrable_domain(e.url)
        row = {k: "" for k in fields}
        row.update({
            "item_no": str(next_no), "kind": "reference entry",
            "title": (e.title or institution)[:160], "creator": "", "date_created": "n.d.",
            "institution": institution, "stable_item_url": e.url,
            "rights_statement_verbatim": "(not checked; cited only)",
            "our_rights_determination": "Cited, not reproduced.", "required_credit": institution,
            "gloss": f"Evidence for the verified fact {p.id}: “{e.span}”",
            "duplicate_or_original": "n/a", "date_checked": today, "status": "OPENED", "recommendation": "CITE",
        })
        buf = io.StringIO()
        csv.DictWriter(buf, fieldnames=fields, lineterminator=newline).writerow(row)
        new_lines.append(buf.getvalue())
        by_url[e.url] = str(next_no)
        items.append(str(next_no))
        next_no += 1
    if new_lines:
        data = path.read_bytes()
        if not data.endswith(newline.encode()):
            data += newline.encode()
        path.write_bytes(data + "".join(new_lines).encode("utf-8"))
    return list(dict.fromkeys(items))


def _shell_env() -> tuple[str, dict]:
    """(bash executable, environment) for the repo's shell scripts.

    The scripts call `python3`; on Windows that is often the Microsoft Store stub, so a small
    `python3` shim pointing at this interpreter is put first on PATH (Git Bash converts the
    Windows-style PATH itself). Git Bash is preferred over WSL's bash.exe.
    """
    env = dict(os.environ, PYTHONUTF8="1")
    bash = "bash"
    if os.name == "nt":
        bindir = ROOT / "living" / ".cache" / "bin"
        bindir.mkdir(parents=True, exist_ok=True)
        shim = bindir / "python3"
        shim.write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "$@"\n', encoding="utf-8", newline="\n")
        shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        for candidate in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"):
            if Path(candidate).exists():
                bash = candidate
                break
    return bash, env


def rebuild(slug: str, run_qa: bool = True) -> list[str]:
    bash, env = _shell_env()
    steps = [[sys.executable, "tools/build_profile.py", f"inductees/{slug}"],
             [sys.executable, "tools/build_site_pages.py"],
             [bash, "tools/package_handover.sh"]]
    if run_qa:
        steps.append([bash, "qa/rebuild.sh"])
    log = []
    for cmd in steps:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
        log.append(f"{' '.join(cmd[-2:])}: exit {r.returncode} {tail[0][:160]}")
        if r.returncode != 0:
            raise PublishError(f"{' '.join(cmd)} failed:\n{(r.stdout + r.stderr)[-1500:]}")
    return log


def publish(pid: str, store: Store, *, reviewer: str = "", branch: bool = False, refetch: bool = True,
            run_qa: bool = True, fixtures=None) -> dict:
    check_not_paused()
    p = store.get(pid)
    if p.status != "approved":
        raise PublishError(f"{pid} is '{p.status}', not 'approved'. A person approves first in the review dashboard.")
    if p.verdict not in PUBLISHABLE_VERDICTS:
        raise PublishError(f"{pid} verdict is {p.verdict}; only {PUBLISHABLE_VERDICTS} may be published")
    if p.kind == "correction":
        raise PublishError(f"{pid} is a correction: an editor changes the existing sentence by hand. Nothing is replaced automatically.")
    if p.kind not in ("fact",):
        raise PublishError(f"publishing kind '{p.kind}' is not supported yet")
    sources = load_sources()
    if refetch:
        fetcher = Fetcher(sources, role="publisher", fresh=True, fixtures=fixtures)
        inp = to_input(p)
        pages = {u: fetcher.get(u) for u, _ in inp.evidence}
        g1, g2 = gate1(inp, pages, sources), gate2(inp, sources)
        if not (g1["passed"] and g2["passed"]):
            raise PublishError("re-check before publishing failed; nothing written: " + "; ".join(g1["reasons"] + g2["reasons"]))

    folder = ROOT / "inductees" / p.slug
    today = _today()
    if branch:
        r = subprocess.run(["git", "checkout", "-b", f"living/{pid}"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            raise PublishError("could not create branch: " + r.stderr.strip())

    copy = folder / "copy.md"
    copy.write_text(append_to_section(copy.read_text(encoding="utf-8"), p.section, f"{p.sentence} {{verified:{pid}}}"),
                    encoding="utf-8", newline="\n")
    items = add_reference_rows(folder / "media-manifest.csv", p, sources, today)

    vf_path = folder / "verified-facts.json"
    vf = json.loads(vf_path.read_text(encoding="utf-8")) if vf_path.exists() else {
        "_note": "Written only by living/publisher.py. Each fact keeps its exact evidence forever.", "facts": []}
    vf["facts"].append({
        "id": pid, "section": p.section, "sentence": p.sentence, "source_items": items, "last_checked": today,
        "approved_by": p.decision.get("by", reviewer), "approved_at": p.decision.get("at", ""),
        "evidence": [{"url": e.url, "span": e.span, "sha256": e.sha256, "retrieved_at": e.retrieved_at,
                      "retrieved_by": e.retrieved_by, "tier": e.tier} for e in p.evidence],
        "gates": {"verdict": p.verdict, "semantic": p.gates.get("gate3", {}).get("status", "")},
    })
    vf_path.write_text(json.dumps(vf, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    feed_path = ROOT / "site-data" / "new-at-the-museum.json"
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    feed["entries"].append({"id": pid, "slug": p.slug, "date": today, "sentence": p.sentence,
                            "sources": [{"title": (e.title or registrable_domain(e.url))[:160], "url": e.url,
                                         "institution": (sources.note(e.url).split(" (")[0] or registrable_domain(e.url))}
                                        for e in p.evidence]})
    feed_path.write_text(json.dumps(feed, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    build_log = rebuild(p.slug, run_qa=run_qa)
    old = p.status
    p.status = "published"
    store.update(p, p.decision.get("by", reviewer) or "publisher", "published",
                 f"applied to inductees/{p.slug}/copy.md section '{p.section}'", old)
    body = pr_body(p, items)
    (store.root / f"{pid}.pr.md").write_text(body, encoding="utf-8", newline="\n")
    if branch:
        subprocess.run(["git", "add", "-A", "inductees", "site", "site-data", "handover", str(store.root)], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-q", "-F", "-"], input=f"Living Museum: publish {pid} ({p.slug})\n\n{body}",
                       text=True, cwd=ROOT, check=True)
    return {"id": pid, "items": items, "build": build_log, "pr_body": str(store.root / f"{pid}.pr.md")}


def pr_body(p: Proposal, items: list[str]) -> str:
    lines = [f"## Living Museum fact {p.id} for `{p.slug}`", "",
             f"**Proposed sentence** (section *{p.section}*):", "", f"> {p.sentence}", "",
             f"**Approved by:** {p.decision.get('by', '?')} at {p.decision.get('at', '?')}"
             + (f" — {p.decision['reason']}" if p.decision.get("reason") else ""), "",
             f"**Gate verdict:** {p.verdict}", "", "| Gate | Result |", "|---|---|"]
    for g in ("gate1", "gate2", "gate3", "gate4", "gate5"):
        r = p.gates.get(g, {})
        res = r.get("status") or ("passed" if r.get("passed", False) else "not required" if r.get("required") is False else "FAILED")
        lines.append(f"| {g[-1]} | {res} |")
    lines += ["", "**Sources and exact spans:**", ""]
    for e, n in zip(p.evidence, items + [""] * len(p.evidence)):
        lines.append(f"- Source {n} (tier {e.tier}, retrieved by {e.retrieved_by} {e.retrieved_at}): <{e.url}>  ")
        lines.append(f"  “{e.span}”  ")
        lines.append(f"  sha256 `{e.sha256}`")
    lines += ["", "Merging this pull request is the final human approval. MUSEUM READY is never set by the system.",
              "", "🤖 Generated with [Claude Code](https://claude.com/claude-code)", ""]
    return "\n".join(lines)
