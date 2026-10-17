"""Feasibility spike harness: run the existing verifier gate over the golden reconciliation set.

    python spike/eval_verifier.py golden      # Q2: drift/blocked/timing over every golden span
    python spike/eval_verifier.py cases       # Q3/Q4: adversarial, positive and semantic cases

Fetches go through the production SourceFetcher and are cached (SHA-checked) under
spike/.profile-factory-cache/ (gitignored). Delete that folder for a cold run.
Results are written to spike/results/.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.schema import FetchStatus  # noqa: E402
from spike.allowlist import allowed  # noqa: E402
from spike.gate import deterministic_gate, fetch  # noqa: E402

EVIDENCE = ROOT / "review" / "workstream-1" / "evidence"
RESULTS = ROOT / "spike" / "results"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def golden_rows():
    for path in sorted(EVIDENCE.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for line, row in doc["rows"].items():
            for key, span in row["evidence"]:
                label, url = doc["sources"][key]
                yield {"slug": doc["slug"], "line": line, "status": row["status"],
                       "claim": row["claim"], "source": label, "url": url, "span": span}


def run_golden() -> dict:
    t0 = time.perf_counter()
    rows = list(golden_rows())
    urls = sorted({r["url"] for r in rows})
    fetch_times = {}
    for url in urls:
        t = time.perf_counter()
        fetch(url)
        fetch_times[url] = round(time.perf_counter() - t, 2)
    t_fetch = time.perf_counter() - t0
    out = []
    for r in rows:
        doc = fetch(r["url"])
        ok = doc.status == FetchStatus.RETRIEVED
        rec = dict(r, retrieved=ok, fetch_status=doc.status.value, fetch_error=doc.error[:200],
                   from_cache=doc.from_cache, allowlisted=allowed(r["url"]),
                   raw_present=ok and r["span"] in doc.text,
                   normalized_present=ok and norm(r["span"]) in norm(doc.text))
        if ok and r["status"] == "CONFIRMED":
            rec["gate_accepts"], rec["gate_reason"] = deterministic_gate(r["claim"], r["span"], doc)
        out.append(rec)
    total = time.perf_counter() - t0
    pages = {u: fetch(u) for u in urls}
    summary = {
        "spans": len(out), "pages": len(urls),
        "pages_retrieved": sum(d.status == FetchStatus.RETRIEVED for d in pages.values()),
        "pages_not_retrieved": {u: f"{d.status.value}: {d.error[:160]}" for u, d in pages.items()
                                if d.status != FetchStatus.RETRIEVED},
        "spans_on_retrieved_pages": sum(r["retrieved"] for r in out),
        "spans_raw_present": sum(r["raw_present"] for r in out),
        "spans_normalized_present": sum(r["normalized_present"] for r in out),
        "spans_missing_after_normalization": [
            {k: r[k] for k in ("slug", "line", "url", "span")}
            for r in out if r["retrieved"] and not r["normalized_present"]],
        "confirmed_spans_gated": sum("gate_accepts" in r for r in out),
        "confirmed_spans_gate_accepts": sum(r.get("gate_accepts", False) for r in out),
        "seconds_fetch_phase": round(t_fetch, 1),
        "seconds_total": round(total, 1),
        "fetched_from_cache": sum(d.from_cache for d in pages.values()),
        "slowest_fetches": sorted(fetch_times.items(), key=lambda x: -x[1])[:5],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "golden.json").write_text(json.dumps({"summary": summary, "rows": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return summary


def run_cases() -> dict:
    from spike.cases import build_cases
    from spike.gate import evaluate
    judgments = json.loads((ROOT / "spike" / "semantic_judgments.json").read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    ech = "https://case.edu/ech/articles/h/hope-leslie-townes-bob"
    cases = build_cases(lambda u: fetch(u).status == FetchStatus.RETRIEVED, fetch(ech).text)
    results = []
    for case in cases:
        res = evaluate(case, judgments.get(case["id"], {}).get("verdict"))
        results.append(dict({k: v for k, v in case.items() if k != "page_text"},
                            synthetic_page=case.get("page_text") is not None, **res))
    elapsed = time.perf_counter() - t0

    def of(kind):
        return [r for r in results if r["kind"] == kind]

    neg, pos, over = of("negative"), of("positive"), of("overclaim")
    summary = {
        "negatives": len(neg),
        "negative_false_accepts_full_gate": [r["id"] for r in neg if r["accepted"]],
        "negative_accepts_existing_gate_alone": [r["id"] for r in neg if r["existing_gate"]],
        "negative_accepts_proposed_deterministic_layers": [
            r["id"] for r in neg if r["allowlisted"] and r["retrieved"] and r["proposed_gate"]],
        "negatives_rejected_only_because_not_retrieved": [
            r["id"] for r in neg if r["allowlisted"] and not r["retrieved"]],
        "positives": len(pos),
        "positives_accepted_full_gate": sum(r["accepted"] for r in pos),
        "positives_accepted_existing_gate_alone": sum(r["existing_gate"] for r in pos),
        "positive_false_rejects_full_gate": [{"id": r["id"], "reason": r["reason"]} for r in pos if not r["accepted"]],
        "overclaim_rows": len(over),
        "overclaims_caught_by_semantic_judge": [r["id"] for r in over if r["semantic"] == "DOES_NOT_SUPPORT"],
        "overclaims_passing_existing_gate": [r["id"] for r in over if r["existing_gate"]],
        "overclaims_caught_by_proposed_number_check": [
            r["id"] for r in over if "numbers in claim" in r.get("proposed_reason", "")],
        "unjudged_cases_reaching_semantic_layer": [
            r["id"] for r in results
            if r["allowlisted"] and r["retrieved"] and r["proposed_gate"] and r["semantic"] == "NOT JUDGED"],
        "seconds": round(elapsed, 1),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "cases.json").write_text(json.dumps({"summary": summary, "cases": results}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "golden"
    summary = run_golden() if mode == "golden" else run_cases()
    print(json.dumps(summary, ensure_ascii=False, indent=1))
