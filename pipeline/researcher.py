from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from .cache import SourceFetcher
from .llm import JSONClient
from .schema import FetchStatus, ProfileDraft, Provenance, SourceDocument


REQUIRED_COPY_MARKERS = [
    "**Opening line",
    "**Credit",
    "**Standfirst:**",
    "## Five discussion questions",
    "## Two activities",
]


def validate_copy_shape(markdown: str) -> list[str]:
    errors: list[str] = []
    if not markdown.lstrip().startswith("# "):
        errors.append("copy.md must begin with one H1 containing the inductee name")
    for marker in REQUIRED_COPY_MARKERS:
        if marker not in markdown:
            errors.append(f"copy.md missing required marker: {marker}")
    # The Albright source format has exactly five narrative sections between the first
    # horizontal rule and the quotation block. Keep that contract for generated profiles.
    parts = markdown.split("---")
    if len(parts) < 3:
        errors.append("copy.md must contain the existing horizontal-rule section boundaries")
    else:
        narrative = parts[1]
        n = len(re.findall(r"^##\s+", narrative, flags=re.M))
        if n != 5:
            errors.append(f"copy.md must contain exactly 5 narrative sections; found {n}")
    if not re.search(r"\*\*First-person quotation \(.+?\):\*\*\s*\n>\s+\S", markdown, re.S):
        errors.append("copy.md must contain one sourced first-person quotation in the existing format")
    q = re.search(r"## Five discussion questions\n(.*?)\n## Two activities", markdown, re.S)
    if not q or len(re.findall(r"^\d+\.\s+", q.group(1), re.M)) != 5:
        errors.append("copy.md must contain exactly 5 numbered discussion questions")
    a = re.search(r"## Two activities\n(.*)$", markdown, re.S)
    if not a or len(re.findall(r"^\*\*\d+\.\s+.+?\*\*", a.group(1), re.M)) != 2:
        errors.append("copy.md must contain exactly 2 activities")
    return errors


class ResearcherAgent:
    def __init__(self, fetcher: SourceFetcher, llm: JSONClient, max_chars_per_source: int = 18000) -> None:
        self.fetcher = fetcher
        self.llm = llm
        self.max_chars_per_source = max_chars_per_source

    async def _fetch_all(self, urls: list[str]) -> dict[str, SourceDocument]:
        async def one(i: int, url: str):
            sid = f"S{i:03d}"
            return sid, await asyncio.to_thread(self.fetcher.fetch, sid, url)
        pairs = await asyncio.gather(*(one(i + 1, u) for i, u in enumerate(urls)))
        return dict(pairs)

    async def run(self, draft: ProfileDraft) -> ProfileDraft:
        draft.sources = await self._fetch_all(draft.seed_urls)
        retrieved = [s for s in draft.sources.values() if s.status == FetchStatus.RETRIEVED and s.text]
        if not retrieved:
            draft.failure_reason = "ResearcherAgent could not retrieve any source text"
            return draft

        blocks: list[str] = []
        for s in draft.sources.values():
            if s.status == FetchStatus.RETRIEVED:
                txt = s.text[: self.max_chars_per_source]
                blocks.append(
                    f"SOURCE {s.source_id}\nURL: {s.url}\nTITLE: {s.title}\nSHA256: {s.sha256}\nTEXT:\n{txt}"
                )
            else:
                blocks.append(
                    f"SOURCE {s.source_id}\nURL: {s.url}\nSTATUS: {s.status.value}\nERROR: {s.error}\n"
                    "IMPORTANT: a failed fetch means only 'could not retrieve'; it is not evidence of nonexistence."
                )

        system = """You are the ResearcherAgent for a museum profile factory.
HONESTY OVER COMPLETENESS. Use ONLY the retrieved source text supplied below. Never invent a fact,
date, quotation, source, image, rights statement, or historical detail. A failed fetch proves only
that retrieval failed. Return JSON only.

Draft copy.md in the exact existing IHH profile shape:
# Name
**Status:** REQUIRES HUMAN SIGN-OFF
**Opening line (sits above the photograph):**
...

**Credit (sits immediately beneath the photograph):**
...

**Standfirst:**
...

---

exactly five ## narrative sections

---

**First-person quotation (one, as reported by SOURCE DESCRIPTION):**
> exact quotation present in a retrieved source

---

## Five discussion questions
1. ... through 5.
## Two activities
**1. Title.** ...
**2. Title.** ...

If a required first-person quotation cannot be sourced exactly, do not fabricate one: return
`cannot_complete_reason` and leave `copy_markdown` empty. Keep questions/activities free of new
historical assertions beyond facts already stated in the sourced profile.

Also return `provenance_hints`: an array of objects with sentence, provenance
(RECORD|QUOTATION|PARAPHRASE|INFERENCE|UNRESOLVED), and source_ids. These are hints only; the
VerifierAgent will independently verify against source text.
Return keys: copy_markdown, provenance_hints, media_candidates, cannot_complete_reason.
media_candidates may only identify a photograph if the supplied source text itself identifies the
image/item and its source URL. Do not invent image URLs or rights wording."""
        user = f"INDUCTEE: {draft.name}\n\n" + "\n\n=====\n\n".join(blocks)
        result = await asyncio.to_thread(self.llm.complete_json, system, user, temperature=0.2)
        if result.get("cannot_complete_reason"):
            draft.failure_reason = "ResearcherAgent: " + str(result["cannot_complete_reason"])
            return draft
        copy_md = str(result.get("copy_markdown", "")).strip() + "\n"
        shape_errors = validate_copy_shape(copy_md)
        if shape_errors:
            draft.failure_reason = "ResearcherAgent produced invalid copy.md: " + "; ".join(shape_errors)
            return draft
        draft.copy_markdown = copy_md
        # Preserve hints on the draft only as initial provenance labels. They are never treated
        # as evidence and never supplied as proof to the verifier.
        hints: dict[str, tuple[Provenance, list[str]]] = {}
        for h in result.get("provenance_hints", []) or []:
            try:
                prov = Provenance(str(h.get("provenance", "UNRESOLVED")))
            except ValueError:
                prov = Provenance.UNRESOLVED
            hints[str(h.get("sentence", "")).strip()] = (prov, [str(x) for x in h.get("source_ids", [])])
        setattr(draft, "_researcher_hints", hints)
        setattr(draft, "_media_candidates", result.get("media_candidates", []) or [])
        return draft
