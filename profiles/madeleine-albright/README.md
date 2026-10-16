# Profile Factory deterministic demo — Madeleine Albright

**Status: REQUIRES HUMAN SIGN-OFF. NOT MUSEUM-READY.**

This is the single demo profile for the Profile Factory. It exercises the real `ResearcherAgent → VerifierAgent → MediaRightsAgent → generic builder → BuildQAAgent` chain with deterministic offline source snapshots and a deterministic fake JSON client. It makes **zero live web requests and zero OpenAI API calls** during the demo. That proves orchestration, hard gates, rendering, and QA behavior; it does **not** prove source freshness or substitute for a real production run.

The five fixture snapshots are deliberately small and derived from material already represented in this repository. The verifier still treats them as untrusted source data, audits visitor-facing factual units independently, and requires an exact evidence span. The rights stage makes no rights grant from those fixtures; missing rights wording remains `NOT LOCATED IN RETRIEVED SOURCE TEXT`.

## Where current run evidence lives

Run-specific artifacts are **generated, not committed**. This prevents an old timestamped `profile-state.json`, `verification-report.json`, `build-qa-report.json`, `source-index.json`, or `handoff-log.jsonl` from sitting in Git and pretending to describe the current code.

The feature-branch GitHub Actions workflow runs:

```sh
python -m pipeline.demo
```

on the current checkout. It then asserts that the generated state says:

- `completed=true`
- `verification_gate=true`
- BuildQA `passed=true`

and uploads the complete run-specific evidence bundle plus rendered desktop-light, desktop-dark, and mobile screenshots as a workflow artifact. A failed demo leaves the workflow red; it is never relabelled as a pass.

## What is committed here

The stable demo source/output files remain reviewable in this directory:

- `copy.md`
- `media-manifest.csv`
- generated static `copy.html`
- generated `copy-full.md`
- generated `preview.html`
- `HUMAN-SIGNOFF-REQUIRED.txt`

The CI run regenerates the static artifacts before testing them. Once the visual system is finalized, CI also checks those stable generated artifacts for drift.

## Boundary

This demo does **not** replace or alter `albright-wp/`. The existing Albright deliverable remains frozen; its no-argument builder is byte-compared in CI and the repository's exact `qa/rebuild.sh` clean-rebuild harness is run from a fresh archive.

A passing demo still stops at **PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF**. A named human must re-open the live sources, review rights, fact-check the authored draft, and approve museum publication.
