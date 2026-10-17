"""Q5 finder dry run: candidate NEW facts for naismith and lamarr, run through the gate.

Candidates were found by Claude Code acting as the finder (mode b) on allowlisted domains on
2026-10-17. Each candidate is checked here for:
  - novelty: none of its key terms already appear in inductees/<slug>/copy.md
  - the proposed deterministic gate (existing gate + normalization + numbers + injection)
  - the second-source rule: a claim containing a date/number, or an award, needs evidence from
    two different registrable domains, and EVERY number in the claim must appear in EACH span
  - the logged semantic judgment (spike/semantic_judgments.json), failing closed
Output: spike/candidates.json. copy.md is never written.

    python spike/finder.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.schema import FetchStatus  # noqa: E402
from spike.allowlist import allowed  # noqa: E402
from spike.gate import fetch, numbers, proposed_gate  # noqa: E402

DCB = "https://www.biographi.ca/en/bio.php?id=9082"
FIBA = "https://about.fiba.basketball/en/fiba-hall-of-fame/hall-of-famers/james-naismith"
KU1880 = "https://exhibits.lib.ku.edu/exhibits/show/naismith150/introduction/1880s"
NIHF = "https://www.invent.org/inductees/hedy-lamarr"
NASM = "https://airandspace.si.edu/stories/editorial/gps-%E2%80%93-hollywood-actress-player-piano-and-hip-hop"
ENC = "https://www.encyclopedia.com/women/encyclopedias-almanacs-transcripts-and-maps/lamarr-hedy-1913-2000"

CANDIDATES = [
    {"id": "F-naismith-1", "slug": "naismith", "section": "Achievements", "award": False,
     "claim": "McGill University appointed James Naismith its Instructor in Gymnastics for 1889-1890.",
     "key_terms": ["Instructor in Gymnastics", "gymnasium at McGill", "1889"],
     "evidence": [(KU1880, "continuing James Naismith’s appointment as Instructor in Gymnastics for 1889-1890"),
                  (DCB, "While there, in 1889, he took on the directorship of McGill’s gymnasium")]},
    {"id": "F-naismith-2", "slug": "naismith", "section": "Achievements", "award": False,
     "claim": "Naismith was director of physical education at the YMCA in Denver, Colorado, from 1895 to 1898.",
     "key_terms": ["YMCA in Denver", "Denver YMCA", "1895"],
     "evidence": [(FIBA, "Physical Education Director in the YMCA in Denver, Colorado, U.S.A.: 1895-1898"),
                  (DCB, "In 1895, with a family to support, he accepted the directorship of physical education at the large YMCA in Denver, Colo.")]},
    {"id": "F-naismith-3", "slug": "naismith", "section": "Achievements", "award": False,
     "claim": "Naismith worked for the YMCA in France during the First World War, from 1917 to 1919.",
     "key_terms": ["France", "YMCA Secretary", "1917"],
     "finder_note": "Novelty key terms corrected after the first run: 'First World War' matched an unrelated copy.md sentence.",
     "evidence": [(FIBA, "YMCA Secretary in France: 1917-1919"),
                  (DCB, "On leave from his university, he did an American tour with the YMCA in 1917 during the First World War. He was in France from the fall of that year until 1919, organizing sports for American soldiers")]},
    {"id": "F-naismith-4", "slug": "naismith", "section": "Honours", "award": True,
     "claim": "Naismith received an honorary doctorate (LLD) from McGill University in 1938.",
     "key_terms": ["honorary", "LLD", "1938"],
     "evidence": [(DCB, "He was awarded honorary degrees by McGill (lld) in 1938 and the Presbyterian College of Montreal (dd) in April 1939."),
                  (FIBA, "Legum Doctorate Degree of the McGill University: 1938")]},
    {"id": "F-naismith-5", "slug": "naismith", "section": "Honours", "award": True,
     "claim": "The International YMCA Training School granted Naismith an honorary MA in physical education in 1911.",
     "key_terms": ["honorary ma", "honorary MA", "Honorary Master"],
     "evidence": [(DCB, "In recognition of his contributions, the International YMCA Training School had granted him an honorary ma in physical education in 1911."),
                  (FIBA, "Honorary Master in Physical Education: 1910")],
     "finder_note": "Sources conflict on the year (DCB 1911, FIBA 1910); expected to fail the second-source rule."},
    {"id": "F-naismith-1R", "slug": "naismith", "section": "Achievements", "award": False, "remediation_of": "F-naismith-1",
     "claim": "In 1889 James Naismith took charge of the gymnasium at McGill University.",
     "key_terms": ["Instructor in Gymnastics", "McGill’s gymnasium", "1889"],
     "evidence": [(DCB, "While there, in 1889, he took on the directorship of McGill’s gymnasium"),
                  (KU1880, "continuing James Naismith’s appointment as Instructor in Gymnastics for 1889-1890")],
     "finder_note": "Evidence-only narrowing of F-naismith-1: end year dropped because only one source gives it."},
    {"id": "F-naismith-2R", "slug": "naismith", "section": "Achievements", "award": False, "remediation_of": "F-naismith-2",
     "claim": "In 1895 Naismith became director of physical education at the YMCA in Denver, Colorado.",
     "key_terms": ["YMCA in Denver", "Denver YMCA", "1895"],
     "evidence": [(DCB, "In 1895, with a family to support, he accepted the directorship of physical education at the large YMCA in Denver, Colo."),
                  (FIBA, "Physical Education Director in the YMCA in Denver, Colorado, U.S.A.: 1895-1898")],
     "finder_note": "Evidence-only narrowing of F-naismith-2: end year dropped because only one source gives it."},
    {"id": "F-lamarr-1", "slug": "lamarr", "section": "Achievements", "award": False,
     "claim": "The U.S. Navy did not use Lamarr and Antheil's frequency-hopping invention during World War II.",
     "key_terms": ["Navy", "did not use", "shunned"],
     "evidence": [(NASM, "The Navy did not use her invention during World War II."),
                  (ENC, "Although shunned by the U.S. Navy, the basic Lamarr-Antheil concept had been a sound one")]},
    {"id": "F-lamarr-2", "slug": "lamarr", "section": "Achievements", "award": False,
     "claim": "Frequency hopping based on the Lamarr-Antheil concept was used in U.S. military communications during the Cuban Missile Crisis in 1962.",
     "key_terms": ["Cuba", "1962", "missile crisis"],
     "evidence": [(NASM, "The technology was later used for military communications, including during the Cuban Missile Crisis in 1962"),
                  (ENC, "It was installed in time to be utilized on American ships sent to enforce a blockade on Cuba in 1962 during the missile crisis")]},
    {"id": "F-lamarr-3", "slug": "lamarr", "section": "Achievements", "award": False,
     "claim": "Lamarr starred in the films Ziegfeld Girl and Samson and Delilah.",
     "key_terms": ["Ziegfeld", "Samson", "Delilah"],
     "evidence": [(NIHF, "starring in films such as \"Ziegfeld Girl\" and \"Samson and Delilah\""),
                  (ENC, "In one of her best-known roles, as Delilah in Cecil B. De Mille's 1949 Biblical epic Samson and Delilah")],
     "finder_note": "Year (1949) dropped: no second allowlisted, retrievable domain gave it."},
    {"id": "F-lamarr-4", "slug": "lamarr", "section": "Achievements", "award": False,
     "claim": "Neither Lamarr nor Antheil ever earned money from their invention.",
     "key_terms": ["profit", "earn a cent", "never earned"],
     "evidence": [(NIHF, "Although Lamarr and Antheil never profited from their invention during their lifetime"),
                  (ENC, "Neither Lamarr nor Antheil, who died in 1959, would ever earn a cent from their invention.")]},
    {"id": "F-lamarr-5", "slug": "lamarr", "section": "Achievements", "award": False,
     "claim": "Lamarr met the composer George Antheil in 1940.",
     "key_terms": ["in 1940", "met George Antheil", "met the composer"],
     "evidence": [(NASM, "In 1940, Lamarr met the American avant-garde composer George Antheil.")],
     "finder_note": "Only one allowlisted, retrievable source gives 1940; expected to fail the second-source rule."},
]


def domain(url: str) -> str:
    return ".".join((urlparse(url).hostname or "").split(".")[-2:])


def main() -> None:
    judgments = json.loads((ROOT / "spike" / "semantic_judgments.json").read_text(encoding="utf-8"))
    out = []
    for c in CANDIDATES:
        copy = (ROOT / "inductees" / c["slug"] / "copy.md").read_text(encoding="utf-8").lower()
        already = [t for t in c["key_terms"] if t.lower() in copy]
        ev = []
        for url, span in c["evidence"]:
            doc = fetch(url)
            ev.append({"url": url, "domain": domain(url), "allowlisted": allowed(url),
                       "retrieved": doc.status == FetchStatus.RETRIEVED,
                       "retrieval_date": (doc.retrieved_at or "")[:10] or "2026-10-17",
                       "span": span, "_doc": doc})
        usable = [e for e in ev if e["allowlisted"] and e["retrieved"]]
        gate_ok, gate_reason = (proposed_gate(c["claim"], [(e["span"], e["_doc"]) for e in usable])
                                if usable and len(usable) == len(ev) else (False, "an evidence page is not allowlisted or not retrieved"))
        needs_two = bool(numbers(c["claim"])) or c["award"]
        domains = {e["domain"] for e in usable}
        nums = numbers(c["claim"])
        per_span = {e["domain"]: sorted(nums - numbers(e["span"])) for e in usable}
        second_ok = (not needs_two) or (len(domains) >= 2 and all(not m for m in per_span.values()))
        sem = judgments.get(c["id"], {}).get("verdict", "NOT JUDGED")
        status = "PROPOSE FOR HUMAN REVIEW" if (not already and gate_ok and second_ok and sem == "SUPPORTS") else "REJECTED"
        reasons = []
        if already:
            reasons.append(f"not new: copy.md already contains {already}")
        if not gate_ok:
            reasons.append(gate_reason)
        if not second_ok:
            reasons.append("second-source rule failed: " + json.dumps({"domains": sorted(domains), "numbers_missing_per_source": per_span}))
        if sem != "SUPPORTS":
            reasons.append(f"semantic judge: {sem}")
        out.append({k: v for k, v in c.items() if k not in ("evidence", "key_terms")}
                   | {"evidence": [{k: v for k, v in e.items() if k != "_doc"} for e in ev],
                      "novelty_terms_found_in_copy": already, "gate": gate_ok, "gate_reason": gate_reason,
                      "needs_second_source": needs_two, "second_source_ok": second_ok,
                      "semantic": sem, "status": status, "reasons": reasons})
    (ROOT / "spike" / "candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for c in out:
        print(c["id"], c["status"], "|", "; ".join(c["reasons"])[:220])


if __name__ == "__main__":
    main()
