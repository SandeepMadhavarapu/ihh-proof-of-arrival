"""The five gates. A proposal passes only if every gate passes; any failure means REJECTED.

GATE 1 deterministic evidence (cannot be overridden)
  allowlisted domain; page retrieved; no instruction-like text addressed to an AI on the page;
  span literally present in the FULL fetched text (whitespace-normalized on both sides); the
  existing pipeline.verifier checks (span >= 24 chars and 4 words, >= 2 shared significant tokens)
  run through the real VerifierAgent code; every number, date, month and ordinal and every
  superlative in the sentence appears in a quoted span; the inductee's name appears on the page and
  within +/-1,500 characters of each span; no span names a different inductee instead.
GATE 2 corroboration
  a date, number, award, "first" or superlative needs spans from two independent registrable
  domains, at least one tier 1, and each such date/number must itself appear in spans from two
  of those domains.
GATE 3 semantic (blind judge, see living/judge.py)
  sees only the sentence and +/-2,000-character windows around the spans. No key configured, or
  the judge cannot answer: NEEDS HUMAN JUDGMENT, never a pass.
GATE 4 conflict
  sources that give a different year, or an existing verified fact (copy.md, approved facts,
  human-confirmed reconciliation rows) that gives a different year for the same topic: CONFLICT.
  A conflict becomes a correction item for a person. Nothing is silently replaced.
GATE 5 media rights (media proposals only)
  pipeline.media_rights rules: rights wording must be an exact retrieved span, safe item URL,
  safe filename, alt text <= 15 words and <= 125 characters.
"""
from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pipeline import verifier as _pv
from pipeline.media_rights import _require_source_span, _safe_manifest_url, validate_alt
from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument, Verdict
from pipeline.security import SecurityValidationError, validate_media_filename

from .config import ROOT, Sources, registrable_domain
from .fetch import Page
from .textnorm import facts, needs_corroboration, norm, superlatives, years

# Words too common in biographies to identify a topic for the conflict check.
GENERIC_TOPIC_WORDS = frozenset("""became become becomes received receive given gave named called made
served began begun united states america american year years later early during after award awarded
honor honored honour honoured first home work worked life""".split())

ENTITY_WINDOW = 1500
JUDGE_WINDOW = 2000
INJECTION = re.compile(
    r"ignore (?:all |any )?(?:previous|prior|above|earlier) instructions"
    r"|disregard (?:all |any )?(?:previous|prior|above) (?:instructions|rules)"
    r"|mark (?:this |it |the claim |the following(?: claim)? )?(?:as )?(?:confirmed|verified|supported)"
    r"|you are (?:an? )?(?:ai|assistant|language model|verifier|fact[- ]checker)"
    r"|system prompt|developer message", re.I)


@dataclass
class VerifierInput:
    """Everything the verifier is allowed to see. No finder confidence or rationale."""
    slug: str
    kind: str
    sentence: str
    evidence: list[tuple[str, str]]          # (url, span)
    media: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    verdict: str                              # PASSED_ALL_GATES | NEEDS_HUMAN_JUDGMENT | CONFLICT | REJECTED
    gates: dict[str, Any]
    reasons: list[str]
    conflict_with: str = ""

    @property
    def deterministic_rejected(self) -> bool:
        return any(not self.gates.get(g, {}).get("passed", True) for g in ("gate1", "gate2", "gate5"))


# -- helpers ---------------------------------------------------------------------------------

def pipeline_lexical_gate(sentence: str, span: str, text: str) -> tuple[bool, str]:
    """Run the EXISTING pipeline.verifier evidence checks on one span.

    A stub model proposes CONFIRMED + span; VerifierAgent._audit decides. The unit list is pinned
    to the one sentence. Whole-page size ceilings are deliberately not applied here: this check
    runs against the full fetched text (S5); only the semantic judge gets bounded windows.
    """
    class _Stub:
        def complete_json(self, system, user, *, temperature):
            return {"sentences": [{"index": 1, "requires_evidence": True, "provenance": "RECORD",
                                   "verdict": "CONFIRMED", "evidence_source_id": "S001",
                                   "evidence_span": span, "reason": "", "suggested_rewrite": ""}]}

    draft = ProfileDraft("Living Museum", "living", [], ROOT / "profiles" / "living")
    draft.sources = {"S001": SourceDocument("S001", "about:blank", FetchStatus.RETRIEVED, text=text)}
    original = _pv.extract_sentences
    _pv.extract_sentences = lambda markdown: [sentence]
    try:
        report = asyncio.run(_pv.VerifierAgent(_Stub())._audit(draft, sentence, ["<window>"]))
    finally:
        _pv.extract_sentences = original
    claim = report.claims[0]
    return claim.verdict == Verdict.CONFIRMED, claim.verifier_reason.replace("spike proposal", "").strip(" |")


def _alias_positions(text: str, aliases: list[str]) -> list[int]:
    return [m.start() for a in aliases if a for m in re.finditer(r"(?<!\w)" + re.escape(a) + r"(?!\w)", text)]


def span_window(text: str, span: str, radius: int) -> tuple[int, int]:
    """(start, end) of a window around the first occurrence of span in normalized text."""
    t, s = norm(text), norm(span)
    pos = t.find(s)
    if pos < 0:
        raise LookupError(f"cannot build a window: span not found in fetched text: {span[:60]!r}")
    return max(0, pos - radius), min(len(t), pos + len(s) + radius)


# -- gates -----------------------------------------------------------------------------------

def gate1(inp: VerifierInput, pages: dict[str, Page], sources: Sources) -> dict[str, Any]:
    checks: list[dict] = []
    reasons: list[str] = []
    aliases = sources.entities.get(inp.slug, [])
    others = {s: a for s, a in sources.entities.items() if s != inp.slug}
    any_lexical = False
    span_facts: set[str] = set()
    span_words = ""
    for url, span in inp.evidence:
        page = pages[url]
        c = {"url": url, "tier": sources.tier(url), "retrieved_by": page.retrieved_by}
        if c["tier"] is None:
            reasons.append(f"{url}: domain not on the allowlist")
        elif not page.ok:
            reasons.append(f"{url}: could not retrieve ({page.status}: {page.error[:120]})")
        elif INJECTION.search(page.text):
            c["injection"] = True
            reasons.append(f"{url}: page contains instruction-like text addressed to an AI; quarantined for a person")
        else:
            text = norm(page.text)
            s = norm(span)
            c["span_present"] = s in text
            if not c["span_present"]:
                reasons.append(f"{url}: span not found in the freshly fetched text: {span[:70]!r}")
            else:
                ok, why = pipeline_lexical_gate(inp.sentence, s, text)
                c["pipeline_gate"] = ok
                if not ok:
                    c["pipeline_reason"] = why[-160:]
                    # Every span, corroborating ones included, must pass on its own: a second
                    # source that only shares a year (a different medal in 1995) is not support.
                    reasons.append(f"{url}: span fails the existing pipeline evidence check: {why[-120:]}")
                any_lexical = any_lexical or ok
                start, end = span_window(text, s, ENTITY_WINDOW)
                window = text[start:end]
                pos = text.find(s)
                c["context"] = text[max(0, pos - 320):pos + len(s) + 320]   # for the review dashboard
                c["entity_on_page"] = bool(_alias_positions(text, aliases))
                c["entity_near_span"] = bool(_alias_positions(window, aliases))
                if not (c["entity_on_page"] and c["entity_near_span"]):
                    reasons.append(f"{url}: {inp.slug}'s name is not within {ENTITY_WINDOW} characters of the span")
                # Only full names ("Celia Cruz"), so "Berlin-based" or "hope" never count as a person.
                foreign = [o for o, a in others.items() if _alias_positions(s, [x for x in a if " " in x])]
                if foreign and not _alias_positions(s, aliases):
                    reasons.append(f"{url}: span names a different inductee ({', '.join(foreign)})")
                span_facts |= facts(s)
                span_words += " " + s
        checks.append(c)
    if inp.evidence and not reasons and not any_lexical:
        reasons.append("no span passes the existing pipeline evidence check (>=24 chars, 4 words, 2 shared significant words)")
    missing = sorted(facts(inp.sentence) - span_facts)
    if missing and not any("could not retrieve" in r or "allowlist" in r for r in reasons):
        reasons.append(f"numbers/dates in the sentence not found in any span: {missing}")
    sup_missing = sorted(superlatives(inp.sentence) - superlatives(span_words))
    if sup_missing and not any("could not retrieve" in r or "allowlist" in r for r in reasons):
        reasons.append(f"superlatives in the sentence not found in any span: {sup_missing}")
    if not inp.evidence:
        reasons.append("no evidence supplied")
    return {"passed": not reasons, "reasons": reasons, "checks": checks,
            "numbers_missing": missing, "superlatives_missing": sup_missing}


def gate2(inp: VerifierInput, sources: Sources) -> dict[str, Any]:
    why = needs_corroboration(inp.sentence)
    if not why:
        return {"passed": True, "required": False, "reasons": []}
    by_domain: dict[str, str] = {}
    tiers: dict[str, int] = {}
    for url, span in inp.evidence:
        d = registrable_domain(url)
        by_domain[d] = by_domain.get(d, "") + " " + norm(span)
        tiers[d] = min(tiers.get(d, 9), sources.tier(url) or 9)
    reasons = []
    if len(by_domain) < 2:
        reasons.append(f"needs two independent domains ({'; '.join(why)}); has {len(by_domain)}: {sorted(by_domain)}")
    if not any(t == 1 for t in tiers.values()):
        reasons.append(f"needs at least one tier-1 source ({'; '.join(why)}); tiers: {tiers}")
    per_fact = {}
    for f in sorted(facts(inp.sentence)):
        doms = sorted(d for d, text in by_domain.items() if f in facts(text))
        per_fact[f] = doms
        if len(doms) < 2:
            reasons.append(f"'{f}' is not stated by two independent domains (found in: {doms or 'none'})")
    for w in sorted(superlatives(inp.sentence)):
        doms = sorted(d for d, text in by_domain.items() if w in superlatives(text))
        if len(doms) < 2:
            reasons.append(f"'{w}' is not stated by two independent domains (found in: {doms or 'none'})")
    return {"passed": not reasons, "required": True, "why": why, "domains": sorted(by_domain),
            "tiers": tiers, "per_fact": per_fact, "reasons": reasons}


def existing_facts(slug: str) -> list[tuple[str, str]]:
    """(origin, sentence) for every fact the museum already stands behind for this inductee."""
    out: list[tuple[str, str]] = []
    copy = ROOT / "inductees" / slug / "copy.md"
    if copy.exists():
        out += [("copy.md", s) for s in _pv.extract_sentences(copy.read_text(encoding="utf-8"))]
    vf = ROOT / "inductees" / slug / "verified-facts.json"
    if vf.exists():
        out += [("verified-facts.json", f["sentence"]) for f in json.loads(vf.read_text(encoding="utf-8"))["facts"]]
    ev = ROOT / "review" / "workstream-1" / "evidence" / f"{slug}.json"
    if ev.exists():
        rows = json.loads(ev.read_text(encoding="utf-8"))["rows"]
        out += [(f"reconciliation {line}", r["claim"]) for line, r in rows.items() if r["status"] == "CONFIRMED"]
    return out


def gate4(inp: VerifierInput, sources: Sources, existing: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    reasons, conflict_with = [], ""
    sentence_years = years(inp.sentence)
    # (a) sources that disagree: a domain none of whose spans states the sentence's year, but
    # which states a different one. (A second span from the same site giving, say, a lifespan
    # is not a disagreement when another span from that site states the year.)
    by_domain: dict[str, set[int]] = {}
    agrees: dict[str, bool] = {}
    for url, span in inp.evidence:
        d, sy = registrable_domain(url), years(span)
        by_domain.setdefault(d, set()).update(sy)
        agrees[d] = agrees.get(d, False) or bool(sy & sentence_years)
    for d, sy in by_domain.items():
        if sentence_years and sy and not agrees[d]:
            reasons.append(f"sources disagree: {d} gives {sorted(sy)} where the sentence says {sorted(sentence_years)}")
    # (b) an existing verified fact on the same topic with a different year
    aliases = {w.lower() for a in sources.entities.get(inp.slug, []) for w in re.findall(r"\w+", a)}
    ignore = aliases | GENERIC_TOPIC_WORDS
    topic = _pv._significant_tokens(inp.sentence) - ignore
    for origin, other in (existing if existing is not None else existing_facts(inp.slug)):
        oy = years(other)
        other_topic = _pv._significant_tokens(other) - ignore
        shared = topic & other_topic
        same_topic = len(shared) >= 3 and len(shared) >= 0.75 * min(len(topic), len(other_topic))
        if sentence_years and oy and same_topic and not (oy & sentence_years):
            reasons.append(f"conflicts with an existing fact ({origin}): {other[:140]!r} gives {sorted(oy)}; shared topic words {sorted(shared)}")
            conflict_with = conflict_with or f"{origin}: {other}"
    return {"passed": not reasons, "reasons": reasons, "conflict_with": conflict_with}


def gate5(inp: VerifierInput, pages: dict[str, Page]) -> dict[str, Any]:
    if inp.kind != "media":
        return {"passed": True, "required": False, "reasons": []}
    m = inp.media
    errors: list[str] = []
    texts = [norm(p.text) for p in pages.values() if p.ok]
    joined = "\n".join(texts)
    rights = norm(m.get("rights_statement_verbatim", ""))
    if not rights:
        errors.append("rights wording is missing; media without exact rights wording is rejected")
    else:
        _require_source_span(rights, joined, "rights wording", errors, 1)
    item_url = m.get("stable_item_url", "")
    if not item_url or item_url not in pages:
        errors.append("stable_item_url must be one of the fetched evidence pages")
    else:
        _safe_manifest_url(item_url, joined, item_url, "stable_item_url", errors, 1)
    try:
        validate_media_filename(m.get("filename", ""))
    except SecurityValidationError as exc:
        errors.append(f"unsafe filename: {exc}")
    if not validate_alt(m.get("alt_text", "")) or not m.get("alt_text"):
        errors.append("alt text must be present, <= 15 words and <= 125 characters")
    return {"passed": not errors, "required": True, "reasons": errors}


def run_gates(inp: VerifierInput, pages: dict[str, Page], sources: Sources, judge=None,
              existing: list[tuple[str, str]] | None = None) -> GateResult:
    g1 = gate1(inp, pages, sources)
    g2 = gate2(inp, sources)
    g5 = gate5(inp, pages)
    g4 = gate4(inp, sources, existing)
    gates: dict[str, Any] = {"gate1": g1, "gate2": g2, "gate4": g4, "gate5": g5}
    g1_reasons = [f"Gate 1: {r}" for r in g1["reasons"]]
    later = [f"Gate 2: {r}" for r in g2["reasons"]] + [f"Gate 5: {r}" for r in g5["reasons"]]
    conflict = [f"Gate 4: {r}" for r in g4["reasons"]]
    if g1_reasons:   # the evidence itself failed: nothing else is trustworthy
        gates["gate3"] = {"status": "NOT RUN", "reason": "an earlier deterministic gate failed"}
        return GateResult("REJECTED", gates, g1_reasons + later + conflict)
    if conflict:     # real evidence that disagrees goes to a person as a conflict/correction item,
        # even when corroboration also failed (a disagreement is usually WHY it failed)
        gates["gate3"] = {"status": "NOT RUN", "reason": "conflict goes to a person first"}
        return GateResult("CONFLICT", gates, conflict + later, g4["conflict_with"])
    if later:
        gates["gate3"] = {"status": "NOT RUN", "reason": "an earlier deterministic gate failed"}
        return GateResult("REJECTED", gates, later)
    if judge is None:
        gates["gate3"] = {"status": "NEEDS HUMAN JUDGMENT", "reason": "no semantic judge configured (no API key)"}
        return GateResult("NEEDS_HUMAN_JUDGMENT", gates, ["Gate 3: no semantic judge configured; a person must judge meaning"])
    windows = []
    for url, span in inp.evidence:
        text = norm(pages[url].text)
        start, end = span_window(text, span, JUDGE_WINDOW)   # raises loudly; never truncates silently
        windows.append({"source": registrable_domain(url), "span": norm(span), "window": text[start:end]})
    g3 = judge.judge(inp.sentence, windows)
    gates["gate3"] = g3
    if g3["status"] == "SUPPORTED":
        return GateResult("PASSED_ALL_GATES", gates, [])
    if g3["status"] in ("PARTLY", "NOT SUPPORTED"):
        words = ", ".join(g3.get("unsupported_words", [])) or "not named"
        return GateResult("REJECTED", gates, [f"Gate 3: {g3['status']} (unsupported words: {words}). {g3.get('reason', '')}"])
    return GateResult("NEEDS_HUMAN_JUDGMENT", gates, [f"Gate 3: {g3.get('reason', 'judge could not answer')}"])
