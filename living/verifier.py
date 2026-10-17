"""The independent verifier stage.

It receives only what `to_input()` copies out of a proposal: the inductee, the kind, the
proposed sentence, the cited URLs and spans, and media fields. The finder's confidence and
rationale never cross. It re-fetches every URL itself (fresh, not from the finder's cache), runs
the five gates, and records the result. A machine rejection keeps the file and its reasons; it
is never deleted.
"""
from __future__ import annotations

from .config import Sources, check_not_paused, load_sources
from .fetch import Fetcher
from .gates import VerifierInput, run_gates
from .judge import make_judge
from .proposals import Evidence, Proposal, Store


def to_input(p: Proposal) -> VerifierInput:
    return VerifierInput(slug=p.slug, kind=p.kind, sentence=p.sentence,
                         evidence=[(e.url, e.span) for e in p.evidence], media=dict(p.media))


def verify(p: Proposal, fetcher: Fetcher, sources: Sources, judge=None, existing=None) -> Proposal:
    inp = to_input(p)
    pages = {url: fetcher.get(url) for url, _ in inp.evidence}
    if inp.kind == "media" and inp.media.get("stable_item_url") and inp.media["stable_item_url"] not in pages:
        pages[inp.media["stable_item_url"]] = fetcher.get(inp.media["stable_item_url"])
    result = run_gates(inp, pages, sources, judge=judge, existing=existing)
    refreshed = []
    for e in p.evidence:
        page = pages[e.url]
        refreshed.append(Evidence(e.url, e.span, page.retrieved_at, page.sha256, page.retrieved_by,
                                  fetcher.snapshot_path(e.url) if page.retrieved_by == "network" else "",
                                  sources.tier(e.url), page.title or e.title))
    p.evidence = refreshed
    p.verdict = result.verdict
    p.gates = result.gates
    p.reasons = result.reasons
    if result.verdict == "CONFLICT" and result.conflict_with and p.kind == "fact":
        p.kind = "correction"       # a contradiction becomes a correction item, never a replace
        p.related = result.conflict_with
    if result.verdict == "REJECTED":
        p.status = "rejected"
    return p


def verify_pending(store: Store, *, dry_run: bool = False, max_fetches: int | None = None,
                   fixtures=None, actor: str = "verifier") -> list[Proposal]:
    check_not_paused()
    sources = load_sources()
    fetcher = Fetcher(sources, role="verifier", fresh=True, fixtures=fixtures, max_fetches=max_fetches)
    judge = make_judge()
    done = []
    for p in store.all():
        if p.status != "pending" or p.verdict != "NOT_VERIFIED":
            continue
        old = p.status
        verify(p, fetcher, sources, judge)
        if not dry_run:
            why = "; ".join(p.reasons)[:600] or "passed every gate that could run"
            store.update(p, actor, f"verified: {p.verdict}", why, old)
        done.append(p)
    return done
