from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

from .build_qa import BuildQAAgent
from .cache import SourceFetcher
from .llm import OpenAIJSONClient
from .media_rights import MediaRightsAgent
from .orchestrator import Orchestrator
from .researcher import ResearcherAgent
from .schema import ProfileDraft
from .security import ensure_profile_output, redact_text, validate_public_http_url
from .verifier import VerifierAgent


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s:
        raise ValueError("name does not produce a usable slug")
    return s


def read_sources(path: Path) -> list[str]:
    urls: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        validate_public_http_url(line, resolve_dns=False)
        urls.append(line)
    if not urls:
        raise ValueError("sources file contains no URLs")
    return urls


async def _main(args) -> int:
    repo = Path(__file__).resolve().parents[1]
    expected_slug = slugify(args.name)
    requested_out = (repo / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    requested_out = ensure_profile_output(repo, requested_out, expected_slug)

    urls = read_sources(Path(args.sources))
    llm = OpenAIJSONClient(model=args.model)
    fetcher = SourceFetcher(repo / ".profile-factory-cache")
    draft = ProfileDraft(args.name, expected_slug, urls, requested_out)
    orch = Orchestrator(
        repo,
        ResearcherAgent(fetcher, llm),
        VerifierAgent(llm),
        MediaRightsAgent(llm),
        BuildQAAgent(repo),
    )
    final, _qa = await orch.run(draft)
    print(f"Profile Factory: {final.name}")
    for h in final.handoffs:
        print(f"  {h.at}  {h.sender} -> {h.receiver}: {h.result} — {h.summary}")
    if final.completed:
        print(f"DONE: {requested_out}")
        print("STATUS: PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF BEFORE MUSEUM PUBLICATION")
        return 0
    print("FAILED / UNVERIFIED: " + (final.failure_reason or "unknown gate failure"), file=sys.stderr)
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Build one evidence-gated Immigrant Hall of Honor profile")
    ap.add_argument("--name", required=True)
    ap.add_argument("--sources", required=True, help="text file containing one seed URL per line")
    ap.add_argument("--out", required=True, help="must be exactly profiles/<slug>/")
    ap.add_argument("--model", default=None, help="OpenAI model; defaults to OPENAI_MODEL or gpt-5.6-sol")
    args = ap.parse_args()
    try:
        return asyncio.run(_main(args))
    except Exception as e:
        # Never print environment contents, request headers, or unredacted provider errors.
        safe = redact_text(f"{type(e).__name__}: {e}")
        print("Profile Factory error: " + safe, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
