"""Blind evaluation of the semantic judge (GATE 3). Needs a key; costs real money.

    set ANTHROPIC_API_KEY and ANTHROPIC_MODEL (e.g. claude-opus-5-5), optionally ANTHROPIC_EFFORT=high
    python living/eval/run_judge_eval.py --repeats 3

For every eval case whose quoted spans are present in the offline fixtures, the judge gets ONLY
the sentence and the +/-2,000-character windows (exactly what Gate 3 sees in production). It
never sees the case id, family, note, expected answer or any reviewer status.

A negative is caught when the judge says PARTLY or NOT SUPPORTED; a positive is correct when it
says SUPPORTED. Answers that are errors or inconsistent count as NEEDS HUMAN JUDGMENT (neither).
With --repeats N each case is judged N times and disagreement is reported.

Writes living/eval/JUDGE-RESULTS.md and judge-results.json. Until this has been run with a key,
the semantic gate's accuracy is NOT YET MEASURED and every document says so.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from living.config import load_sources  # noqa: E402
from living.config import registrable_domain  # noqa: E402
from living.eval.run_eval import load, pages_for  # noqa: E402
from living.fetch import Fetcher  # noqa: E402
from living.gates import JUDGE_WINDOW, span_window  # noqa: E402
from living.judge import make_judge  # noqa: E402
from living.textnorm import norm  # noqa: E402

EVAL = ROOT / "living" / "eval"


def windows_for(case, pages):
    out = []
    for e in case["evidence"]:
        page = pages[e["url"]]
        if not page.ok:
            return None
        text = norm(page.text)
        try:
            start, end = span_window(text, e["span"], JUDGE_WINDOW)
        except LookupError:
            return None        # the span is not on the page: Gate 1 already rejects; nothing to judge
        out.append({"source": registrable_domain(e["url"]), "span": norm(e["span"]), "window": text[start:end]})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--max-calls", type=int, default=400, help="hard cap on model calls")
    args = ap.parse_args()
    judge = make_judge()
    if judge is None:
        print("No judge configured: set ANTHROPIC_API_KEY and ANTHROPIC_MODEL (or OPENAI_API_KEY and OPENAI_MODEL).")
        print("Semantic gate accuracy remains NOT YET MEASURED. Nothing was written.")
        return 2
    sources = load_sources()
    cases, fixtures = load()
    fetcher = Fetcher(sources, fixtures=fixtures)
    rows, calls, started = [], 0, time.perf_counter()
    for c in cases:
        w = windows_for(c, pages_for(c, fetcher, fixtures))
        if w is None:
            continue
        answers = []
        for _ in range(args.repeats):
            if calls >= args.max_calls:
                break
            calls += 1
            answers.append(judge.judge(c["sentence"], w))
        if not answers:
            break
        statuses = [a["status"] for a in answers]
        majority = Counter(statuses).most_common(1)[0][0]
        good = (majority in ("PARTLY", "NOT SUPPORTED")) if c["kind"] == "negative" else (majority == "SUPPORTED")
        rows.append({"id": c["id"], "kind": c["kind"], "statuses": statuses, "majority": majority, "correct": good,
                     "consistent": len(set(statuses)) == 1,
                     "unsupported_words": answers[0].get("unsupported_words", []), "reason": answers[0].get("reason", "")})
    neg = [r for r in rows if r["kind"] == "negative"]
    pos = [r for r in rows if r["kind"] == "positive"]
    s = {"judge": judge.label, "repeats": args.repeats, "calls": calls,
         "negatives_judged": len(neg), "negatives_caught": sum(r["correct"] for r in neg),
         "negatives_judged_supported": [r["id"] for r in neg if r["majority"] == "SUPPORTED"],
         "positives_judged": len(pos), "positives_supported": sum(r["correct"] for r in pos),
         "inconsistent_across_repeats": [r["id"] for r in rows if not r["consistent"]],
         "seconds": round(time.perf_counter() - started, 1)}
    (EVAL / "judge-results.json").write_text(json.dumps({"summary": s, "rows": rows}, ensure_ascii=False, indent=1) + "\n",
                                             encoding="utf-8")
    md = ["# Semantic judge evaluation (blind)", "", f"Judge: {s['judge']}; repeats: {s['repeats']}; calls: {s['calls']}.", "",
          "| Measurement | Result |", "|---|---|",
          f"| Negatives caught (PARTLY or NOT SUPPORTED) | {s['negatives_caught']} / {s['negatives_judged']} |",
          f"| Negatives the judge called SUPPORTED | {', '.join(s['negatives_judged_supported']) or 'none'} |",
          f"| Positives judged SUPPORTED | {s['positives_supported']} / {s['positives_judged']} |",
          f"| Cases that changed across repeats | {', '.join(s['inconsistent_across_repeats']) or 'none'} |", "",
          "| Case | Kind | Answers | Unsupported words |", "|---|---|---|---|"]
    md += [f"| {r['id']} | {r['kind']} | {', '.join(r['statuses'])} | {', '.join(r['unsupported_words'])[:120]} |" for r in rows]
    (EVAL / "JUDGE-RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(s, indent=1))
    return 1 if s["negatives_judged_supported"] else 0


if __name__ == "__main__":
    sys.exit(main())
