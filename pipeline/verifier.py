from __future__ import annotations

import asyncio
import datetime as dt
import re
from typing import Any, Dict, List

from .llm import JSONClient
from .schema import Claim, FetchStatus, ProfileDraft, Provenance, SentenceAudit, Verdict, VerificationReport


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _clearly_nonclaim(sentence: str) -> bool:
    s = sentence.strip()
    if not s:
        return True
    if s.endswith("?"):
        return True
    low = s.lower()
    if low.startswith(("status: requires human sign-off", "no verified anchor photograph", "requires human sign-off")):
        return True
    first = re.sub(r"^[\"“‘(]+", "", s).split(" ", 1)[0].lower().rstrip(":,.!")
    return first in {"find", "match", "list", "compare", "read", "trace", "mark", "record", "identify", "explain", "consider", "review"}


def extract_sentences(markdown: str) -> list[str]:
    """Extract every visitor-facing sentence/question/instruction from copy.md.

    Headings and field labels are structure, not prose. Everything else is presented to the
    verifier, including discussion questions and activity instructions.
    """
    blocks: list[str] = []
    cur: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line or line == "---":
            if cur:
                blocks.append(" ".join(cur)); cur = []
            continue
        if line.startswith("#"):
            if cur:
                blocks.append(" ".join(cur)); cur = []
            continue
        if re.match(r"^\*\*(?:Opening line|Credit|Standfirst|Status|First-person quotation)[^*]*:\*\*$", line):
            if cur:
                blocks.append(" ".join(cur)); cur = []
            continue
        line = re.sub(r"^>\s*", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = re.sub(r"^\*\*\d+\.\s*([^*]+)\.\*\*\s*", r"\1. ", line)
        line = re.sub(r"\*\*|\*|`", "", line)
        cur.append(line)
    if cur:
        blocks.append(" ".join(cur))
    out: list[str] = []
    for block in blocks:
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“‘(])", block):
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                out.append(s)
    return out


class VerifierAgent:
    def __init__(self, llm: JSONClient) -> None:
        self.llm = llm

    async def run(self, draft: ProfileDraft) -> ProfileDraft:
        sentences = extract_sentences(draft.copy_markdown)
        source_blocks: list[str] = []
        for sid, src in draft.sources.items():
            if src.status == FetchStatus.RETRIEVED and src.text:
                source_blocks.append(f"SOURCE {sid}\nURL: {src.url}\nTEXT:\n{src.text}")
        if not source_blocks:
            draft.failure_reason = "VerifierAgent has no retrieved source text"
            return draft

        indexed = "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sentences))
        system = """You are an adversarial museum fact verifier. You are independent from the researcher.
Judge each supplied sentence ONLY against the retrieved source TEXT below, never against any
researcher assertion. Return JSON only.

For EVERY numbered sentence return one object with:
index, requires_evidence, provenance, verdict, evidence_source_id, evidence_span, reason,
suggested_rewrite.

requires_evidence=false only for a pure editorial instruction/question that introduces NO factual
premise about the subject, source, date, institution, quotation, event, or historical context.
Everything factual, including a factual premise embedded in a question, requires evidence.

For an evidence-requiring sentence:
- CONFIRMED only when one retrieved source directly supports the sentence and you can copy an EXACT
  contiguous source span into evidence_span.
- QUOTATION requires the exact quoted words in the source text.
- PARAPHRASE must not be broader or more certain than the span.
- UNSUPPORTED when the source does not establish it or evidence is missing.
- CONTRADICTED when retrieved source text directly conflicts with it.
- INFERENCE and UNRESOLVED are never shortcuts to CONFIRMED; if the visitor-facing sentence asserts
  them as fact without a directly supporting span, mark UNSUPPORTED.
- A fetch failure is not evidence that something does not exist.

provenance is one of RECORD, QUOTATION, PARAPHRASE, INFERENCE, UNRESOLVED.
If unsupported/contradicted, suggested_rewrite may contain a narrower sentence only if the supplied
source text directly supports it; otherwise leave it empty. Do not invent.

Temperature for this verifier is fixed by the caller at 0."""
        user = (
            "SENTENCES:\n" + indexed + "\n\nRETRIEVED SOURCES:\n\n" + "\n\n=====\n\n".join(source_blocks)
        )
        result = await asyncio.to_thread(self.llm.complete_json, system, user, temperature=0.0)
        rows = result.get("sentences")
        if not isinstance(rows, list):
            draft.failure_reason = "VerifierAgent returned no sentences array"
            return draft

        by_index = {int(r.get("index", 0)): r for r in rows if str(r.get("index", "")).isdigit()}
        claims: list[Claim] = []
        audits: list[SentenceAudit] = []
        malformed: list[str] = []
        for i, sentence in enumerate(sentences, 1):
            r = by_index.get(i)
            if not r:
                malformed.append(f"sentence {i} missing from verifier response")
                c = Claim(f"C{i:03d}", sentence, Provenance.UNRESOLVED, verdict=Verdict.UNSUPPORTED,
                          verifier_reason="Verifier omitted this sentence")
                claims.append(c)
                audits.append(SentenceAudit(f"T{i:03d}", sentence, True, c.claim_id, "verifier omission"))
                continue
            requires = bool(r.get("requires_evidence", True))
            # Do not let the model bypass verification by labelling an ordinary declarative
            # sentence "editorial". Only an obviously non-assertive question/instruction or
            # build-status notice may skip evidence.
            if not requires and not _clearly_nonclaim(sentence):
                requires = True
            if not requires:
                audits.append(SentenceAudit(f"T{i:03d}", sentence, False, "", str(r.get("reason", "editorial/nonclaim"))))
                continue
            try:
                prov = Provenance(str(r.get("provenance", "UNRESOLVED")))
            except ValueError:
                prov = Provenance.UNRESOLVED
            try:
                verdict = Verdict(str(r.get("verdict", "UNSUPPORTED")))
            except ValueError:
                verdict = Verdict.UNSUPPORTED
            sid = str(r.get("evidence_source_id", ""))
            span = str(r.get("evidence_span", ""))
            reason = str(r.get("reason", ""))
            rewrite = str(r.get("suggested_rewrite", ""))
            # Mechanical independence gate: a CONFIRMED verdict is invalid unless the exact
            # quoted span is literally present in the retrieved source text named by the verifier.
            src = draft.sources.get(sid)
            if verdict == Verdict.CONFIRMED:
                if not sid or not span or not src or src.status != FetchStatus.RETRIEVED or span not in src.text:
                    verdict = Verdict.UNSUPPORTED
                    reason = (reason + " | ").strip(" |") + "CONFIRMED downgraded: exact evidence span was not found in retrieved source text"
            claim = Claim(
                claim_id=f"C{i:03d}",
                sentence=sentence,
                provenance=prov,
                source_ids=[sid] if sid else [],
                verdict=verdict,
                evidence_source_id=sid,
                evidence_span=span,
                verifier_reason=reason,
                suggested_rewrite=rewrite,
            )
            claims.append(claim)
            audits.append(SentenceAudit(f"T{i:03d}", sentence, True, claim.claim_id, ""))

        gate = bool(claims) and not malformed and all(c.verdict == Verdict.CONFIRMED for c in claims)
        report = VerificationReport(
            profile_name=draft.name,
            generated_at=_now(),
            gate_passed=gate,
            claims=claims,
            sentence_audit=audits,
            notes=["Every CONFIRMED claim has an exact span mechanically checked against retrieved source text."] + malformed,
        )
        draft.claims = claims
        draft.sentence_audit = audits
        draft.verification_report = report
        if not gate:
            draft.failure_reason = "VerifierAgent gate failed: one or more factual sentences are not CONFIRMED"
        return draft
