#!/usr/bin/env python3
"""Living Museum command line.

    python living/run.py status
    python living/run.py find --slug naismith [--limit 5] [--rewrite]
    python living/run.py verify
    python living/run.py review [--port 8765]
    python living/run.py publish --id LM-0007 [--branch]
    python living/run.py watchdog [--simulate living/demo/watchdog-simulation.json]
    python living/run.py eval
    python living/run.py import-snapshot --url URL --file saved-page.html --reviewer "Name"
    python living/run.py import-spike
    python living/run.py export-wp

Kill switch: if the file living/PAUSED exists, every command except `status` stops at once.
Caps: --max-fetches, --max-seconds and --max-llm-calls bound one run; --dry-run writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from living.config import AUDIT_LOG, PAUSED, ROOT, Paused, check_not_paused, load_sources  # noqa: E402
from living.proposals import Evidence, Proposal, Store, verify_chain  # noqa: E402


class CappedJudge:
    """Stops calling the model after N calls; later items fall back to NEEDS HUMAN JUDGMENT."""

    def __init__(self, judge, cap: int) -> None:
        self.inner, self.cap, self.calls = judge, cap, 0

    def judge(self, sentence, windows):
        if self.calls >= self.cap:
            return {"status": "NEEDS HUMAN JUDGMENT", "reason": f"per-run model-call cap ({self.cap}) reached"}
        self.calls += 1
        return self.inner.judge(sentence, windows)


def cmd_status(args, store: Store) -> int:
    items = store.all()
    print(f"Paused: {'YES (' + str(PAUSED.relative_to(ROOT)) + ' exists)' if PAUSED.exists() else 'no'}")
    print(f"Proposals: {len(items)}")
    for p in items:
        print(f"  {p.id}  {p.slug:9} {p.kind:10} {p.status:9} {p.verdict:22} {p.sentence[:70]}")
    ok, msg = verify_chain(store.audit_log)
    print(f"Audit log: {msg}")
    return 0 if ok else 1


def cmd_find(args, store: Store) -> int:
    from living import finder
    from living.judge import make_judge
    client = None
    if args.rewrite:
        judge = make_judge()
        if judge is None:
            print("--rewrite needs ANTHROPIC_API_KEY + ANTHROPIC_MODEL (or the OpenAI pair); using source wording.")
        else:
            client = judge.client
    made, log = finder.run(args.slug, store, limit=args.limit, dry_run=args.dry_run, max_fetches=args.max_fetches,
                           max_seconds=args.max_seconds, rewrite_client=client)
    for line in log:
        print("  fetch:", line)
    for p in made:
        print(f"{'(dry run) ' if args.dry_run else ''}{p.id} {p.slug}: {p.sentence}")
    return 0


def cmd_verify(args, store: Store) -> int:
    from living import verifier
    from living.fetch import Fetcher
    from living.judge import make_judge
    sources = load_sources()
    fetcher = Fetcher(sources, role="verifier", fresh=True, max_fetches=args.max_fetches)
    judge = make_judge()
    if judge is not None:
        judge = CappedJudge(judge, args.max_llm_calls)
    started = time.monotonic()
    for p in store.all():
        if args.id and p.id != args.id:
            continue
        machine_rejected = p.status == "rejected" and not p.decision and p.verdict == "REJECTED"
        if args.recheck and machine_rejected:
            # Re-check after a gate change: only machine rejections with no human decision.
            p.status = "pending"
            if not args.dry_run:
                store.update(p, "verifier", "recheck", "re-verified after a gate change (no human decision existed)", "rejected")
        elif p.status != "pending" or (p.verdict != "NOT_VERIFIED" and not args.id):
            continue
        if time.monotonic() - started > args.max_seconds:
            print("time cap reached; remaining proposals left unverified")
            break
        old = p.status
        verifier.verify(p, fetcher, sources, judge)
        if not args.dry_run:
            store.update(p, "verifier", f"verified: {p.verdict}", "; ".join(p.reasons)[:600] or "passed", old)
        print(f"{p.id} {p.slug}: {p.verdict}")
        for r in p.reasons:
            print("    ", r)
    return 0


def cmd_review(args, store: Store) -> int:
    from living.review_app.server import serve
    serve(args.port)
    return 0


def cmd_publish(args, store: Store) -> int:
    from living.publisher import publish
    if args.dry_run:
        print("--dry-run: publish writes copy.md, the manifest and site/; nothing done.")
        return 0
    out = publish(args.id, store, branch=args.branch, refetch=not args.no_refetch, run_qa=not args.skip_qa)
    print(json.dumps(out, indent=1))
    return 0


def cmd_watchdog(args, store: Store) -> int:
    from living import watchdog
    target = store
    if args.simulate:
        target = Store(ROOT / "living" / ".cache" / "simulation" / "proposals")
        print("SIMULATION: local fixture, separate queue under living/.cache/simulation/ (not the real queue).")
    report = watchdog.run(target, simulate=Path(args.simulate) if args.simulate else None, max_fetches=args.max_fetches)
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=1, ensure_ascii=False))
    return 0


def cmd_eval(args, store: Store) -> int:
    from living.eval import run_eval
    return run_eval.main(write=not args.dry_run)


def cmd_import_snapshot(args, store: Store) -> int:
    from living.fetch import Fetcher
    page = Fetcher(load_sources(), role="human").import_human_snapshot(args.url, Path(args.file), args.reviewer)
    print(f"{page.url}: {page.status}, retrieved_by=human, sha256 {page.sha256[:16]}, {len(page.text)} chars")
    return 0 if page.ok else 1


def cmd_export_wp(args, store: Store) -> int:
    from living import export
    path = export.write()
    print(f"WordPress block for 'New at the Museum' written to {path}")
    print("Each inductee's page block is inductees/<slug>/copy.html (see handover/INSTALL.md).")
    return 0


def cmd_import_spike(args, store: Store) -> int:
    """S7: queue the spike's finder candidates; the NEW verifier re-checks every one."""
    data = json.loads((ROOT / "living" / "demo" / "spike-candidates.json").read_text(encoding="utf-8"))
    keep = {"F-naismith-1R", "F-naismith-2R", "F-naismith-3", "F-naismith-4", "F-naismith-5",
            "F-lamarr-1", "F-lamarr-2", "F-lamarr-3", "F-lamarr-4"}
    existing = {p.finder.get("spike_id") for p in store.all()}
    for c in data:
        if c["id"] not in keep or c["id"] in existing:
            continue
        p = Proposal(id=store.next_id(), kind="fact", slug=c["slug"], section="", sentence=c["claim"], claim=c["claim"],
                     evidence=[Evidence(e["url"], e["span"], tier=None) for e in c["evidence"]],
                     finder={"mode": "spike: Claude Code acting as finder on 2026-10-17 (ws2-spike 88c45ba)",
                             "spike_id": c["id"], "confidence": None,
                             "rationale": [c.get("finder_note", "")] if c.get("finder_note") else [],
                             "needs_editor": True})
        from living.finder import target_section
        p.section = target_section(p.slug, p.sentence)
        if not args.dry_run:
            store.create(p, "import-spike", f"spike candidate {c['id']} queued for re-verification by the new gates")
        print(f"{p.id} <- {c['id']}: {p.sentence}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Living Museum")
    ap.add_argument("--dry-run", action="store_true", help="write nothing")
    ap.add_argument("--max-fetches", type=int, default=40, help="network fetch cap for this run")
    ap.add_argument("--max-seconds", type=float, default=600, help="wall-clock cap for this run")
    ap.add_argument("--max-llm-calls", type=int, default=50, help="model call cap for this run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    f = sub.add_parser("find"); f.add_argument("--slug", required=True); f.add_argument("--limit", type=int, default=5)
    f.add_argument("--rewrite", action="store_true")
    v = sub.add_parser("verify"); v.add_argument("--id")
    v.add_argument("--recheck", action="store_true", help="re-verify machine rejections that have no human decision")
    r = sub.add_parser("review"); r.add_argument("--port", type=int, default=8765)
    pb = sub.add_parser("publish"); pb.add_argument("--id", required=True); pb.add_argument("--branch", action="store_true")
    pb.add_argument("--no-refetch", action="store_true"); pb.add_argument("--skip-qa", action="store_true")
    w = sub.add_parser("watchdog"); w.add_argument("--simulate")
    sub.add_parser("eval")
    s = sub.add_parser("import-snapshot"); s.add_argument("--url", required=True); s.add_argument("--file", required=True)
    s.add_argument("--reviewer", required=True)
    sub.add_parser("import-spike")
    sub.add_parser("export-wp")
    args = ap.parse_args(argv)
    store = Store()
    if args.cmd != "status":
        try:
            check_not_paused()
        except Paused as exc:
            print(exc)
            return 3
    handler = {"status": cmd_status, "find": cmd_find, "verify": cmd_verify, "review": cmd_review,
               "publish": cmd_publish, "watchdog": cmd_watchdog, "eval": cmd_eval,
               "import-snapshot": cmd_import_snapshot, "import-spike": cmd_import_spike,
               "export-wp": cmd_export_wp}[args.cmd]
    return handler(args, store)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    sys.exit(main())
