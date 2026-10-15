from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

from .build_qa import BuildQAAgent, BuildQAResult
from .media_rights import MediaRightsAgent, render_manifest
from .researcher import ResearcherAgent
from .schema import HandoffRecord, ProfileDraft
from .security import ensure_profile_output, redact_text
from .verifier import VerifierAgent


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Orchestrator:
    def __init__(
        self,
        repo_root: Path,
        researcher: ResearcherAgent,
        verifier: VerifierAgent,
        media_rights: MediaRightsAgent,
        build_qa: BuildQAAgent,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.researcher = researcher
        self.verifier = verifier
        self.media_rights = media_rights
        self.build_qa = build_qa

    def _assert_output_isolated(self, draft: ProfileDraft) -> None:
        ensure_profile_output(self.repo_root, draft.out_dir, draft.slug)

    def _handoff(self, draft: ProfileDraft, sender: str, receiver: str, summary: str, result: str, artifacts: dict[str, str] | None = None) -> None:
        safe_summary = redact_text(summary)
        safe_artifacts = {k: redact_text(v) for k, v in (artifacts or {}).items()}
        draft.handoffs.append(HandoffRecord(_now(), sender, receiver, safe_summary, safe_artifacts, result))

    def _write_log(self, draft: ProfileDraft) -> None:
        self._assert_output_isolated(draft)
        draft.out_dir.mkdir(parents=True, exist_ok=True)
        p = draft.out_dir / "handoff-log.jsonl"
        p.write_text("\n".join(json.dumps(h.to_dict(), ensure_ascii=False) for h in draft.handoffs) + ("\n" if draft.handoffs else ""), encoding="utf-8", newline="\n")

    async def run(self, draft: ProfileDraft) -> tuple[ProfileDraft, BuildQAResult | None]:
        self._assert_output_isolated(draft)
        draft.out_dir.mkdir(parents=True, exist_ok=True)
        draft.completed = False
        draft.status = "REQUIRES HUMAN SIGN-OFF"
        draft.failure_reason = ""
        draft.verification_report = None
        draft.handoffs = []
        # Invalidate a previous successful run before any fallible work. Historical files
        # may remain for diagnosis, but never retain an authoritative PASS state.
        (draft.out_dir / "build-qa-report.json").write_text(
            json.dumps({"passed": False, "static_errors": ["QA not completed for current run"], "commands": []}) + "\n",
            encoding="utf-8",
        )
        self._write_state(draft)
        try:
            return await self._run(draft)
        except Exception as exc:
            draft.completed = False
            draft.status = "REQUIRES HUMAN SIGN-OFF"
            draft.failure_reason = redact_text(f"{type(exc).__name__}: {exc}")
            self._handoff(draft, "Orchestrator", "Human reviewer", draft.failure_reason, "FAIL")
            self._write_log(draft)
            raise RuntimeError(draft.failure_reason) from None
        finally:
            self._write_state(draft)

    def _write_state(self, draft: ProfileDraft) -> None:
        (draft.out_dir / "profile-state.json").write_text(
            json.dumps(draft.to_summary(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )

    async def _run(self, draft: ProfileDraft) -> tuple[ProfileDraft, BuildQAResult | None]:
        self._assert_output_isolated(draft)
        draft.out_dir.mkdir(parents=True, exist_ok=True)

        self._handoff(draft, "Orchestrator", "ResearcherAgent", f"name={draft.name}; seed_sources={len(draft.seed_urls)}", "START")
        await self.researcher.run(draft)
        self._handoff(
            draft, "ResearcherAgent", "Orchestrator",
            f"retrieved={sum(1 for s in draft.sources.values() if s.text)}; total_sources={len(draft.sources)}",
            "FAIL" if draft.failure_reason else "PASS",
            {"draft_copy_sha256": _hash_text(draft.copy_markdown)} if draft.copy_markdown else {},
        )
        self._write_log(draft)
        if draft.failure_reason:
            return draft, None

        self._handoff(draft, "Orchestrator", "VerifierAgent", "independent sentence-level verification; researcher evidence hints excluded", "START")
        await self.verifier.run(draft)
        if draft.verification_report:
            (draft.out_dir / "verification-report.json").write_text(
                json.dumps(draft.verification_report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
            )
        self._handoff(
            draft, "VerifierAgent", "Orchestrator",
            f"claims={len(draft.claims)}; gate={bool(draft.verification_report and draft.verification_report.gate_passed)}",
            "PASS" if draft.verification_report and draft.verification_report.gate_passed else "FAIL",
        )
        self._write_log(draft)
        if not draft.verification_report or not draft.verification_report.gate_passed:
            # Keep the untrusted research draft visibly separate from final copy.md.
            (draft.out_dir / "research-draft.REJECTED.md").write_text(draft.copy_markdown, encoding="utf-8", newline="\n")
            draft.failure_reason = draft.failure_reason or "VerifierAgent gate failed"
            return draft, None

        self._handoff(draft, "Orchestrator", "MediaRightsAgent", "build manifest from retrieved source text; rights wording exact-span checked", "START")
        await self.media_rights.run(draft)
        self._handoff(draft, "MediaRightsAgent", "Orchestrator", f"manifest_rows={len(draft.media_rows)}", "FAIL" if draft.failure_reason else "PASS")
        self._write_log(draft)
        if draft.failure_reason:
            return draft, None

        # Only after all evidence gates pass do final source-of-truth files exist.
        (draft.out_dir / "copy.md").write_text(draft.copy_markdown, encoding="utf-8", newline="\n")
        (draft.out_dir / "media-manifest.csv").write_text(render_manifest(draft.media_rows), encoding="utf-8", newline="\n")
        (draft.out_dir / "HUMAN-SIGNOFF-REQUIRED.txt").write_text(
            "DRAFT — REQUIRES HUMAN SIGN-OFF BEFORE MUSEUM PUBLICATION.\n"
            "The pipeline evidence-gates claims and QA, but it can never mark a profile museum-ready.\n",
            encoding="utf-8",
        )
        source_index = {sid: s.to_dict() for sid, s in draft.sources.items()}
        for meta in source_index.values():
            meta.pop("text", None)
        (draft.out_dir / "source-index.json").write_text(json.dumps(source_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

        self._handoff(draft, "Orchestrator", "BuildQAAgent", "run generic build plus existing QA hard gates", "START")
        qa = self.build_qa.run(draft.out_dir)
        (draft.out_dir / "build-qa-report.json").write_text(json.dumps({
            "passed": qa.passed,
            "static_errors": [redact_text(x) for x in qa.static_errors],
            "commands": [
                {
                    "command": redact_text(c.command.replace(str(self.repo_root), "$REPO")),
                    "returncode": c.returncode,
                    "stdout": redact_text(c.stdout.replace(str(self.repo_root), "$REPO")),
                    "stderr": redact_text(c.stderr.replace(str(self.repo_root), "$REPO")),
                }
                for c in qa.commands
            ],
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        self._handoff(draft, "BuildQAAgent", "Orchestrator", f"commands={len(qa.commands)}; qa_passed={qa.passed}", "PASS" if qa.passed else "FAIL")
        draft.completed = qa.passed
        draft.status = "PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF" if qa.passed else "REQUIRES HUMAN SIGN-OFF"
        if not qa.passed:
            draft.failure_reason = "BuildQAAgent gate failed; see build-qa-report.json"
        else:
            draft.failure_reason = ""
        self._write_log(draft)
        (draft.out_dir / "profile-state.json").write_text(json.dumps(draft.to_summary(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return draft, qa
