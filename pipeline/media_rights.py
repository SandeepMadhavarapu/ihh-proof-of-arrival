from __future__ import annotations

import asyncio
import csv
import io
from typing import Any, Dict, List

from .llm import JSONClient
from .schema import FetchStatus, ProfileDraft


MANIFEST_COLUMNS = [
    "item_no","kind","filename","title","creator","date_created","institution",
    "stable_item_url","download_url","rights_statement_verbatim","rights_statement_source",
    "our_rights_determination","our_reasoning","required_credit","alt_text","alt_text_chars",
    "long_description","long_description_status","gloss","duplicate_or_original","date_checked",
    "status","recommendation",
]


def validate_alt(text: str) -> bool:
    return len(text) <= 125 and len(text.split()) <= 15


class MediaRightsAgent:
    def __init__(self, llm: JSONClient) -> None:
        self.llm = llm

    async def run(self, draft: ProfileDraft) -> ProfileDraft:
        source_blocks = []
        for sid, src in draft.sources.items():
            if src.status == FetchStatus.RETRIEVED:
                source_blocks.append(f"SOURCE {sid}\nURL: {src.url}\nTITLE: {src.title}\nTEXT:\n{src.text}")
            else:
                source_blocks.append(f"SOURCE {sid}\nURL: {src.url}\nSTATUS: {src.status.value}\nERROR: {src.error}")
        media_candidates = getattr(draft, "_media_candidates", [])
        system = """You are the MediaRightsAgent for a museum profile. Return JSON only.
Create media-manifest.csv rows in the exact existing schema supplied by the caller. Include every
retrieved seed source as a source row, plus only those image/media candidates that are actually
identified in retrieved source text.

HONESTY RULES:
- rights_statement_verbatim must be copied EXACTLY from retrieved source text. If no rights wording
  was located, use exactly `NOT LOCATED IN RETRIEVED SOURCE TEXT` and do not infer a license.
- Never turn 'US government', 'publicly viewable', or a collection-level statement into a rights
  grant for a specific item unless the retrieved item text says it.
- If wording came from prior notes rather than a re-read source, use the existing pattern
  `TRANSCRIBED FROM RESEARCH NOTES; NOT re-read at the source during this run.` This may be used only
  when such prior-note status is explicitly present in retrieved input; never invent that history.
- An image subject is CONFIRMED only when retrieved source text identifies that specific item as the
  subject. Otherwise put `SUBJECT UNCONFIRMED` in long_description_status and do not name the person
  in alt text.
- alt_text: <=15 words and <=125 characters. If subject unconfirmed, describe only what metadata can
  safely establish (e.g. `Archival photograph; subject unconfirmed.`).
- A failed fetch means `could not retrieve`, never `does not exist`.
- Do not invent creator, dates, institutions, download URLs, identifiers, credits, or rights.
- For missing values use empty string or an explicit NOT LOCATED/UNCONFIRMED status, not guesses.

Return {"rows": [...]} with every column requested by the caller. Add `source_id` as an extra field
for internal validation; it will not be written to CSV."""
        user = (
            "COLUMNS:\n" + ",".join(MANIFEST_COLUMNS) +
            "\n\nMEDIA CANDIDATES FROM RESEARCHER (NOT TRUSTED AS EVIDENCE):\n" + repr(media_candidates) +
            "\n\nRETRIEVED SOURCES:\n\n" + "\n\n=====\n\n".join(source_blocks)
        )
        result = await asyncio.to_thread(self.llm.complete_json, system, user, temperature=0.0)
        rows = result.get("rows")
        if not isinstance(rows, list) or not rows:
            draft.failure_reason = "MediaRightsAgent returned no manifest rows"
            return draft

        clean: list[dict[str, str]] = []
        errors: list[str] = []
        used_source_ids: list[str] = []
        for i, raw in enumerate(rows, 1):
            row = {k: str(raw.get(k, "")) for k in MANIFEST_COLUMNS}
            row["item_no"] = str(i)
            sid = str(raw.get("source_id", ""))
            if sid:
                used_source_ids.append(sid)
            src = draft.sources.get(sid)
            rights = row["rights_statement_verbatim"].strip()
            if rights.startswith("TRANSCRIBED FROM RESEARCH NOTES"):
                if not src or src.status != FetchStatus.RETRIEVED or "TRANSCRIBED FROM RESEARCH NOTES" not in src.text:
                    errors.append(f"row {i}: prior-note transcription status is not supported by retrieved source {sid}")
            elif rights and rights != "NOT LOCATED IN RETRIEVED SOURCE TEXT":
                if not src or src.status != FetchStatus.RETRIEVED or rights not in src.text:
                    errors.append(f"row {i}: rights wording is not an exact span of source {sid}")
            alt = row["alt_text"].strip()
            if alt and not validate_alt(alt):
                errors.append(f"row {i}: alt text exceeds 15 words or 125 characters")
            row["alt_text_chars"] = str(len(alt)) if alt else ""
            if "UNCONFIRMED" in row["long_description_status"].upper():
                if draft.name.lower() in alt.lower():
                    errors.append(f"row {i}: unconfirmed image subject is asserted in alt text")
                if alt and "subject unconfirmed" not in alt.lower():
                    errors.append(f"row {i}: unconfirmed image alt text must explicitly say subject unconfirmed")
            clean.append(row)

        # Every successfully retrieved seed source is part of the provenance record. The LLM
        # may not silently omit an inconvenient source from the manifest.
        required_source_ids = {sid for sid, src in draft.sources.items() if src.status == FetchStatus.RETRIEVED}
        missing_source_ids = sorted(required_source_ids - set(used_source_ids))
        if missing_source_ids:
            errors.append("manifest omitted retrieved source(s): " + ", ".join(missing_source_ids))
        unknown_source_ids = sorted(set(used_source_ids) - set(draft.sources))
        if unknown_source_ids:
            errors.append("manifest referenced unknown source(s): " + ", ".join(unknown_source_ids))
        if errors:
            draft.failure_reason = "MediaRightsAgent validation failed: " + "; ".join(errors)
            return draft
        draft.media_rows = clean
        return draft


def render_manifest(rows: list[dict[str, str]]) -> str:
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({k: row.get(k, "") for k in MANIFEST_COLUMNS})
    return out.getvalue()
