"""The museum checks itself.

For every published fact (inductees/*/verified-facts.json) the watchdog re-fetches every source
and checks that the exact span is still there. A missing span, a changed page or a page that can
no longer be retrieved opens a re-verification item in the review queue. It never edits or
deletes published content: a person decides what to do. Results go to living/health.json.

Simulation (for demos and tests): `--simulate` reads facts and page texts from a local fixture
file instead of the live site and writes to a separate, clearly labelled output. Nothing in a
simulation touches the real queue or living/health.json.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .config import HEALTH, ROOT, check_not_paused, load_sources
from .fetch import Fetcher
from .proposals import Evidence, Proposal, Store
from .textnorm import norm


def published_facts(root: Path = ROOT) -> list[tuple[str, dict]]:
    out = []
    for vf in sorted((root / "inductees").glob("*/verified-facts.json")):
        for fact in json.loads(vf.read_text(encoding="utf-8"))["facts"]:
            out.append((vf.parent.name, fact))
    return out


def check(facts: list[tuple[str, dict]], fetcher: Fetcher) -> dict:
    results, drift = [], []
    for slug, fact in facts:
        sources_ok = True
        for ev in fact["evidence"]:
            page = fetcher.get(ev["url"])
            problem = ""
            if not page.ok:
                problem = f"could not retrieve ({page.status}: {page.error[:100]})"
            elif norm(ev["span"]) not in norm(page.text):
                problem = "the quoted span is no longer on the page"
            changed = bool(page.ok and ev.get("sha256") and page.sha256 and page.sha256 != ev["sha256"])
            if problem:
                sources_ok = False
                drift.append({"fact": fact["id"], "slug": slug, "url": ev["url"], "problem": problem,
                              "page_changed": changed})
            results.append({"fact": fact["id"], "url": ev["url"], "ok": not problem,
                            "page_changed_since_approval": changed, "problem": problem})
        fact["_ok"] = sources_ok
    return {"checked_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "facts_total": len(facts), "facts_verified": sum(1 for _, f in facts if f.get("_ok")),
            "sources_checked": len(results), "drift_found": len(drift), "drift": drift, "results": results}


def open_reverify_items(report: dict, facts: list[tuple[str, dict]], store: Store, actor: str = "watchdog") -> list[str]:
    by_id = {f["id"]: (slug, f) for slug, f in facts}
    open_items = {(p.related, e.url) for p in store.all() if p.kind == "reverify" and p.status == "pending"
                  for e in p.evidence}
    made = []
    for d in report["drift"]:
        if (d["fact"], d["url"]) in open_items:
            continue
        slug, fact = by_id[d["fact"]]
        ev = next(e for e in fact["evidence"] if e["url"] == d["url"])
        p = Proposal(id=store.next_id(), kind="reverify", slug=slug, section=fact["section"],
                     sentence=fact["sentence"], claim=fact["sentence"],
                     evidence=[Evidence(ev["url"], ev["span"], ev.get("retrieved_at", ""), ev.get("sha256", ""),
                                        ev.get("retrieved_by", ""), tier=ev.get("tier"))],
                     verdict="NEEDS_HUMAN_JUDGMENT", related=d["fact"],
                     reasons=[f"Watchdog: {d['problem']}. The published fact is unchanged; a person decides."])
        store.create(p, actor, f"source drift on {d['fact']}: {d['problem']}")
        made.append(p.id)
    return made


def run(store: Store, *, simulate: Path | None = None, max_fetches: int | None = 200) -> dict:
    check_not_paused()
    sources = load_sources()
    if simulate:
        fx = json.loads(Path(simulate).read_text(encoding="utf-8"))
        facts = [(f["slug"], f) for f in fx["facts"]]
        fetcher = Fetcher(sources, fixtures=fx["pages"])
        report = check(facts, fetcher)
        report["simulation"] = fx.get("label", "SIMULATION")
        report["reverify_items"] = open_reverify_items(report, facts, store)
        for _, f in facts:
            f.pop("_ok", None)
        return report
    facts = published_facts()
    fetcher = Fetcher(sources, role="watchdog", fresh=True, max_fetches=max_fetches)
    report = check(facts, fetcher)
    report["reverify_items"] = open_reverify_items(report, facts, store)
    for _, f in facts:
        f.pop("_ok", None)
    HEALTH.write_text(json.dumps({k: v for k, v in report.items() if k != "results"} |
                                 {"results": report["results"]}, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8", newline="\n")
    return report
