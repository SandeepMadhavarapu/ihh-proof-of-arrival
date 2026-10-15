from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from .build_qa import BuildQAAgent
from .media_rights import MediaRightsAgent
from .orchestrator import Orchestrator
from .researcher import ResearcherAgent
from .schema import FetchStatus, ProfileDraft, SourceDocument
from .verifier import VerifierAgent


REPO = Path(__file__).resolve().parents[1]
DEMO_NAME = "Madeleine Albright"
DEMO_SLUG = "madeleine-albright"
DEMO_URLS = [
    "https://history.state.gov/departmenthistory/people/albright-madeleine-korbel",
    "https://www.cbsnews.com/news/albright-renews-her-oath/",
    "https://tile.loc.gov/storage-services/service/gdc/gdcfindingaidpdfs/ms018034/ms018034.pdf",
    "https://www.washingtonpost.com/history/2022/03/23/madeleine-albright-jewish/",
    "https://jweekly.com/2012/08/31/prague-winter-a-searing-account-of-hidden-jewish-family-history/",
]

FIXTURES = {
    DEMO_URLS[0]: """Madeleine Albright. Madeleine Korbel Albright was born on May 15, 1937, in Prague.
She was the first woman to hold the office. She was sworn in on January 23, 1997, as the 64th Secretary of State.
Birth record. Secretary of State.""",
    DEMO_URLS[1]: """Associated Press. Today marks a new beginning in your lives and an ongoing chapter in the story of America which is, above all else, the story of immigrants.""",
    DEMO_URLS[2]: """Papers. Access boundary. The papers of Madeleine Korbel Albright, U.S. secretary of state, diplomat, and educator, were given to the Library of Congress by Albright in 2014 and 2016.
Access to digital content is available onsite only in the Manuscript Reading Room and requires advanced notice.""",
    DEMO_URLS[3]: """Family history. She was raised as a Roman Catholic and was never told by her parents or anyone else that family members had perished in the Holocaust.""",
    DEMO_URLS[4]: """Prague Winter is a source in the broader research record. This small deterministic fixture does not add claims from it.""",
}


class FixtureFetcher:
    def fetch(self, source_id: str, url: str) -> SourceDocument:
        text = FIXTURES[url]
        return SourceDocument(
            source_id=source_id,
            url=url,
            status=FetchStatus.RETRIEVED,
            title="Deterministic offline demo source snapshot",
            retrieved_at="DETERMINISTIC-FIXTURE",
            content_type="text/plain",
            text=text,
            sha256="fixture-" + source_id,
            error="",
            from_cache=False,
        )


class DemoJSONClient:
    """Deterministic fake LLM for the one committed demo.

    It deliberately exercises the real agent boundaries without network or an API key. It is not a
    substitute for the production OpenAI path; API transport has its own offline tests.
    """

    def __init__(self, copy_markdown: str) -> None:
        self.copy_markdown = copy_markdown

    @staticmethod
    def _numbered_units(user: str) -> list[tuple[int, str]]:
        return [(int(i), s.strip()) for i, s in re.findall(r"^\[(\d+)\]\s+(.+)$", user, re.M)]

    @staticmethod
    def _evidence(unit: str) -> tuple[bool, str, str, str]:
        # Return requires_evidence, source_id, exact span, provenance.
        editorial = {
            "Status: REQUIRES HUMAN SIGN-OFF",
            "Which source directly supports each factual sentence?",
            "Which details remain outside this small source set?",
            "Why should a museum distinguish a retrieved source from a failed fetch?",
            "What would a human reviewer check before publication?",
            "What additional primary source would improve this profile?",
            "Trace a claim.",
            "Match one factual sentence to its exact evidence span.",
            "Mark a boundary.",
            "List facts this demo source set does not establish.",
            "No verified anchor photograph is supplied in this deterministic demo profile.",
        }
        if unit in editorial:
            return False, "", "", "UNRESOLVED"
        mapping = {
            "Madeleine Albright": ("S001", "Madeleine Albright", "RECORD"),
            "Madeleine Korbel Albright was born on May 15, 1937, in Prague.": ("S001", "Madeleine Korbel Albright was born on May 15, 1937, in Prague.", "RECORD"),
            "She was the first woman to hold the office.": ("S001", "She was the first woman to hold the office.", "RECORD"),
            "Birth record": ("S001", "Birth record", "RECORD"),
            "Secretary of State": ("S001", "Secretary of State", "RECORD"),
            "She was sworn in on January 23, 1997, as the 64th Secretary of State.": ("S001", "She was sworn in on January 23, 1997, as the 64th Secretary of State.", "RECORD"),
            "Papers": ("S003", "Papers", "RECORD"),
            "The papers of Madeleine Korbel Albright, U.S. secretary of state, diplomat, and educator, were given to the Library of Congress by Albright in 2014 and 2016.": ("S003", "The papers of Madeleine Korbel Albright, U.S. secretary of state, diplomat, and educator, were given to the Library of Congress by Albright in 2014 and 2016.", "RECORD"),
            "Access boundary": ("S003", "Access boundary", "RECORD"),
            "Access to digital content is available onsite only in the Manuscript Reading Room and requires advanced notice.": ("S003", "Access to digital content is available onsite only in the Manuscript Reading Room and requires advanced notice.", "RECORD"),
            "Family history": ("S004", "Family history", "RECORD"),
            "She was raised as a Roman Catholic and was never told by her parents or anyone else that family members had perished in the Holocaust.": ("S004", "She was raised as a Roman Catholic and was never told by her parents or anyone else that family members had perished in the Holocaust.", "RECORD"),
            "Quotation attribution: the Associated Press": ("S002", "Associated Press", "RECORD"),
            "Quotation attribution: Associated Press": ("S002", "Associated Press", "RECORD"),
            "Today marks a new beginning in your lives and an ongoing chapter in the story of America which is, above all else, the story of immigrants.": ("S002", "Today marks a new beginning in your lives and an ongoing chapter in the story of America which is, above all else, the story of immigrants.", "QUOTATION"),
        }
        if unit not in mapping:
            # Unknown units are rejected rather than conveniently confirmed.
            return True, "", "", "UNRESOLVED"
        sid, span, provenance = mapping[unit]
        return True, sid, span, provenance

    def complete_json(self, system: str, user: str, *, temperature: float):
        if "ResearcherAgent" in system:
            return {
                "copy_markdown": self.copy_markdown,
                "provenance_hints": [],
                "media_candidates": [],
                "cannot_complete_reason": "",
            }
        if "MediaRightsAgent" in system:
            rows = []
            for i, url in enumerate(DEMO_URLS, 1):
                rows.append({
                    "source_id": f"S{i:03d}",
                    "kind": "text source",
                    "filename": "(text source - no file)",
                    "title": "Deterministic demo source snapshot",
                    "creator": "",
                    "date_created": "",
                    "institution": "Source institution named by URL",
                    "stable_item_url": url,
                    "download_url": "",
                    "rights_statement_verbatim": "NOT LOCATED IN RETRIEVED SOURCE TEXT",
                    "rights_statement_source": "No rights wording in deterministic fixture snapshot",
                    "our_rights_determination": "No rights determination made.",
                    "our_reasoning": "Fixture contains no rights statement; nothing inferred.",
                    "required_credit": "",
                    "alt_text": "",
                    "long_description": "",
                    "long_description_status": "n/a - not an image",
                    "gloss": "Source used by the deterministic pipeline demo.",
                    "duplicate_or_original": "n/a",
                    "date_checked": "DETERMINISTIC FIXTURE",
                    "status": "FIXTURE SNAPSHOT — REQUIRES HUMAN RE-READ",
                    "recommendation": "RE-READ LIVE SOURCE BEFORE PUBLICATION",
                })
            return {"rows": rows}
        if "corrective editor" in system:
            return {"copy_markdown": self.copy_markdown}
        if "adversarial museum fact verifier" in system:
            rows = []
            for index, unit in self._numbered_units(user):
                requires, sid, span, provenance = self._evidence(unit)
                verdict = "CONFIRMED" if requires and sid and span else ("UNSUPPORTED" if requires else "UNSUPPORTED")
                rows.append({
                    "index": index,
                    "requires_evidence": requires,
                    "provenance": provenance,
                    "verdict": verdict,
                    "evidence_source_id": sid,
                    "evidence_span": span,
                    "reason": "Deterministic fixture evidence." if requires else "Editorial/build-state statement.",
                    "suggested_rewrite": "",
                })
            return {"sentences": rows}
        raise AssertionError("unexpected demo LLM stage")


async def run_demo(out_dir: Path) -> int:
    copy_markdown = (REPO / "profiles" / DEMO_SLUG / "copy.md").read_text(encoding="utf-8")
    llm = DemoJSONClient(copy_markdown)
    draft = ProfileDraft(DEMO_NAME, DEMO_SLUG, DEMO_URLS, out_dir)
    orch = Orchestrator(
        REPO,
        ResearcherAgent(FixtureFetcher(), llm),
        VerifierAgent(llm, max_remediation_rounds=0),
        MediaRightsAgent(llm),
        BuildQAAgent(REPO),
    )
    final, qa = await orch.run(draft)
    if not final.completed or not qa or not qa.passed:
        raise RuntimeError(final.failure_reason or "deterministic demo did not complete")
    print("DEMO PIPELINE COMPLETE")
    print("STATUS: PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF")
    print(f"claims={len(final.claims)} sources={len(final.sources)} qa_commands={len(qa.commands)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the single deterministic offline Profile Factory demo")
    ap.add_argument("--out", default=f"profiles/{DEMO_SLUG}")
    args = ap.parse_args()
    out = (REPO / args.out).resolve()
    return asyncio.run(run_demo(out))


if __name__ == "__main__":
    raise SystemExit(main())
