"""Feasibility-spike gate: allowlist + robots.txt + fetch + the EXISTING verifier gate.

The deterministic evidence checks are not reimplemented here. `deterministic_gate` drives the
real `pipeline.verifier.VerifierAgent._audit` with a stub model that proposes CONFIRMED plus a
candidate span, so the production code decides: span literally present in retrieved text,
>= 24 characters and 4 words, >= 2 shared significant tokens, and the 60,000-character
complete-review ceiling. Only the unit list is pinned to the single claim under test.
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import verifier as _verifier  # noqa: E402
from pipeline.cache import SourceFetcher  # noqa: E402
from pipeline.schema import FetchStatus, ProfileDraft, SourceDocument, Verdict  # noqa: E402

from spike.allowlist import allowed  # noqa: E402

try:  # Windows Python lacks a system CA bundle; certificates are still fully verified.
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

USER_AGENT ="IHH-Profile-Factory/1.0 (+museum research; build-time fetch)"
CACHE = ROOT / "spike" / ".profile-factory-cache"
_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def robots_allows(url: str) -> tuple[bool, str]:
    """Respect robots.txt for OUR user agent, per RFC 9309.

    robots.txt is fetched with the same User-Agent as page fetches (the stdlib
    RobotFileParser.read() sends "Python-urllib", which many sites answer with 403 and which
    the parser then treats as disallow-all). 200: obey the rules. 4xx: no restrictions
    (RFC 9309 s2.3.1.3). 5xx or unreachable: do not fetch (s2.3.1.4).
    """
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(resp.read().decode("utf-8", "replace").splitlines())
                _robots[base] = rp
        except urllib.error.HTTPError as exc:
            _robots[base] = "allow" if 400 <= exc.code < 500 else "deny"
        except Exception:
            _robots[base] = "deny"
    rule = _robots[base]
    if rule == "allow":
        return True, "robots.txt 4xx: no restrictions (RFC 9309)"
    if rule == "deny":
        return False, "robots.txt unreachable or 5xx: not fetched (RFC 9309)"
    return rule.can_fetch(USER_AGENT, url), "robots.txt rules applied"


_fetcher = SourceFetcher(CACHE, timeout=25)
_docs: dict[str, SourceDocument] = {}


def fetch(url: str) -> SourceDocument:
    """Fetch through the production SourceFetcher (SSRF guards, SHA-checked cache)."""
    if url not in _docs:
        ok, note = robots_allows(url)
        if not ok:
            _docs[url] = SourceDocument("S001", url, FetchStatus.FETCH_FAILED, error="robots.txt disallows this URL; not fetched")
        else:
            try:
                _docs[url] = _fetcher.fetch("S001", url)
            except Exception as exc:  # recorded as a pipeline defect, never as evidence
                _docs[url] = SourceDocument("S001", url, FetchStatus.UNPARSED,
                                            error=f"pipeline fetch/parse crashed: {type(exc).__name__}: {exc}"[:300])
    return _docs[url]


class _StubModel:
    """Plays the model's role only to *propose* CONFIRMED + span; the real gate disposes."""

    def __init__(self, span: str) -> None:
        self.span = span

    def complete_json(self, system, user, *, temperature):
        assert temperature == 0.0
        return {"sentences": [{
            "index": 1, "requires_evidence": True, "provenance": "RECORD",
            "verdict": "CONFIRMED", "evidence_source_id": "S001",
            "evidence_span": self.span, "reason": "spike proposal", "suggested_rewrite": "",
        }]}


def deterministic_gate(claim: str, span: str, doc: SourceDocument) -> tuple[bool, str]:
    draft = ProfileDraft("Spike", "spike", [doc.url], ROOT / "profiles" / "spike")
    draft.sources = {"S001": doc}
    agent = _verifier.VerifierAgent(_StubModel(span))
    blocks = agent._source_blocks(draft)
    if not blocks:
        return False, draft.failure_reason or "no retrieved source text"
    original = _verifier.extract_sentences
    _verifier.extract_sentences = lambda markdown: [claim]
    try:
        report = asyncio.run(agent._audit(draft, claim, blocks))
    finally:
        _verifier.extract_sentences = original
    if report is None:
        return False, draft.failure_reason
    c = report.claims[0]
    return c.verdict == Verdict.CONFIRMED, c.verifier_reason


# ---------------------------------------------------------------------------------------
# PROPOSED additions (spike only; candidates for Prompt B). The existing gate is unchanged.
# ---------------------------------------------------------------------------------------
_NUM = re.compile(r"\d[\d,]*")
_INJECTION = re.compile(
    r"ignore (?:all |any )?(?:previous|prior|above) instructions"
    r"|mark (?:this |it |the claim |the following )?(?:as )?confirmed"
    r"|you are (?:an? )?(?:ai|assistant|language model|verifier)", re.I)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip()


def numbers(text: str) -> set[str]:
    return {n.replace(",", "").lstrip("0") or "0" for n in _NUM.findall(text)}


def proposed_gate(claim: str, evidence: list[tuple[str, SourceDocument]]) -> tuple[bool, str]:
    """Existing gate on whitespace-normalized text, plus: every span present, at least one span
    passing the existing gate, every number in the claim present in the spans, and quarantine of
    pages that contain instructions addressed to an AI."""
    for _, doc in evidence:
        if _INJECTION.search(doc.text):
            return False, "page contains instruction-like text addressed to an AI; quarantined"
    passed, reasons = False, []
    for span, doc in evidence:
        ndoc = SourceDocument(doc.source_id, doc.url, doc.status, text=norm(doc.text))
        if norm(span) not in ndoc.text:
            return False, f"span not present after whitespace normalization: {span[:60]!r}"
        ok, why = deterministic_gate(claim, norm(span), ndoc)
        passed = passed or ok
        reasons.append(why)
    if not passed:
        return False, "no span passes the existing gate: " + " / ".join(r[-90:] for r in reasons)
    missing = numbers(claim) - set().union(*(numbers(s) for s, _ in evidence))
    if missing:
        return False, f"numbers in claim absent from evidence spans: {sorted(missing)}"
    return True, "proposed deterministic layers passed"


def evaluate(case: dict, semantic: str | None) -> dict:
    """Layered result for one case. Every layer must pass; missing judgment fails closed."""
    ev = []
    for item in case["evidence"]:
        if case.get("page_text") is not None:  # synthetic page for injection tests: no network
            doc = SourceDocument("S001", item["url"], FetchStatus.RETRIEVED, text=case["page_text"])
        else:
            doc = fetch(item["url"])
        ev.append((item["span"], doc, item["url"]))
    out = {"allowlisted": all(allowed(u) for _, _, u in ev),
           "retrieved": all(d.status == FetchStatus.RETRIEVED for _, d, _ in ev),
           "semantic": semantic or "NOT JUDGED"}
    got = [(s, d) for s, d, _ in ev if d.status == FetchStatus.RETRIEVED]
    if not got:
        errs = "; ".join(f"{d.status.value} {d.error[:90]}" for _, d, _ in ev)
        out.update(existing_gate=False, existing_reason=f"could not retrieve: {errs}",
                   proposed_gate=False, proposed_reason=f"could not retrieve: {errs}")
    else:
        results = [deterministic_gate(case["claim"], s, d) for s, d in got]
        out["existing_gate"] = any(ok for ok, _ in results)
        out["existing_reason"] = " / ".join(why[-110:] for _, why in results)
        if out["retrieved"]:
            out["proposed_gate"], out["proposed_reason"] = proposed_gate(case["claim"], got)
        else:
            out["proposed_gate"], out["proposed_reason"] = False, "could not retrieve every evidence page"
    gates = out["allowlisted"] and out["retrieved"] and out["proposed_gate"]
    out["accepted"] = gates and semantic == "SUPPORTS"
    if not out["allowlisted"]:
        out["reason"] = "domain not on allowlist"
    elif not out["retrieved"]:
        out["reason"] = out["proposed_reason"]
    elif not out["proposed_gate"]:
        out["reason"] = out["proposed_reason"]
    elif semantic != "SUPPORTS":
        out["reason"] = f"semantic judge: {out['semantic']}"
    else:
        out["reason"] = "accepted"
    return out
