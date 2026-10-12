# Profile Factory deterministic demo — Madeleine Albright

**Status: REQUIRES HUMAN SIGN-OFF. NOT MUSEUM-READY.**

This is the single demo profile requested for the Profile Factory implementation. It was generated through the real orchestration / researcher / verifier / media-rights / generic-build path, but with deterministic offline fixture clients and five source-text snapshots derived from material already documented in this repository. It did **not** call the OpenAI API and did **not** freshly retrieve the live URLs. It therefore proves the pipeline contracts and hard gates, not freshness of the sources or the live API path.

The verification gate passed because every factual sentence marked `CONFIRMED` includes an exact evidence span that the verifier code mechanically found in its retrieved fixture text. The manifest makes no rights grant from those fixtures; it says `NOT LOCATED IN RETRIEVED SOURCE TEXT`.

On the local execution environment used for this implementation, `qa/integrity.mjs` passed all 37 checks, but browser QA could not be completed because `axe-core` was not installed and Chromium local HTTP navigation was later blocked by the environment's administrator policy. `build-qa-report.json` records that hard gate failure rather than pretending success. The feature-branch GitHub Actions workflow separately installs Playwright + axe-core and has run the existing browser harnesses plus `qa/profile-factory.mjs` successfully against this generated profile.

This demo does **not** replace or alter `albright-wp/`. The existing Albright deliverable remains frozen and its no-argument build is checked byte-for-byte.
