# Profile Factory

`pipeline/` is a **build-time-only** multi-agent pipeline for creating one Immigrant Hall of Honor profile from an inductee name and seed source URLs. It does not add an agent, API call, tracker, framework, external font, or remote dependency to the visitor-facing page. The shipped profile remains static HTML generated from `copy.md` + `media-manifest.csv`.

## Non-negotiable behavior

- **Honesty over completeness.** A failed fetch means only `could not retrieve`. The pipeline never treats it as evidence that a source/fact/image does not exist.
- **Verifier independence.** The verifier receives retrieved source text, not the researcher's claimed evidence. A factual sentence is `CONFIRMED` only when the verifier supplies an exact source span and the Python gate mechanically finds that span in the retrieved source text. Verification runs at `temperature=0`.
- **Hard gate with one evidence-only repair pass.** The verifier may remove or narrowly rewrite rejected claims once, then independently re-audits the revised draft from source text. Any factual claim still `UNSUPPORTED`/`CONTRADICTED`, any verifier omission, any unchanged rejected sentence, or any missing/non-matching evidence span blocks the build. On a failed verification run the untrusted draft is written only as `research-draft.REJECTED.md`; it is never promoted to `copy.md`.
- **Rights honesty.** Rights wording is either an exact span of retrieved source text, an explicitly documented prior-note transcription, or `NOT LOCATED IN RETRIEVED SOURCE TEXT`. Unconfirmed image subjects remain `UNCONFIRMED`; alt text is capped at 15 words / 125 characters.
- **Frozen Albright deliverable.** New output lives only under `profiles/<slug>/`. The existing `albright-wp/` content is never used as a profile output directory.
- **Human sign-off.** Every generated profile is visibly marked `REQUIRES HUMAN SIGN-OFF`. Passing machine gates does not make a profile museum-ready.

## Agent/message flow

```text
CLI
  ↓
Orchestrator (owns ProfileDraft + append-only handoff log)
  ↓
ResearcherAgent
  - fetches seed URLs
  - caches retrieved bytes on disk
  - drafts copy.md shape
  - may suggest media candidates, never as proof
  ↓
VerifierAgent  ← retrieves evidence directly from ProfileDraft.sources
  - audits every visitor-facing sentence
  - distinguishes factual claims from pure editorial questions/instructions
  - CONFIRMED requires an exact quoted source span
  - may remove/narrow rejected claims once using only retrieved source text
  - independently re-audits the revised draft
  - any factual claim still non-CONFIRMED => hard stop
  ↓
MediaRightsAgent
  - builds media-manifest.csv using the existing column schema
  - exact-span checks rights wording
  - enforces subject/alt-text guardrails
  ↓
write copy.md + media-manifest.csv + verification-report.json
  ↓
albright-wp/build.py --profile-dir profiles/<slug>/
  - separate generic path
  - no-argument Albright path remains unchanged
  ↓
BuildQAAgent
  - existing repo integrity + browser QA harnesses
  - generated-profile QA
  ↓
DONE only if every hard gate passes
```

## Message contracts

The contracts live in `pipeline/schema.py`.

### `ProfileDraft`

Single state object owned by the Orchestrator. It contains name/slug, seed URLs, retrieved `SourceDocument`s, draft Markdown, `Claim`s, sentence audit records, manifest rows, `VerificationReport`, handoffs, and final completion/failure state.

### `SourceDocument`

Stores URL, retrieval status (`RETRIEVED`, `FETCH_FAILED`, `UNPARSED`), retrieval time, content type, SHA-256, parsed source text, and error text. Cache metadata stores the same status honestly; failures are not reinterpreted.

### `Claim`

A factual visitor-facing assertion with:

- `claim_id`
- exact `sentence`
- provenance: `RECORD | QUOTATION | PARAPHRASE | INFERENCE | UNRESOLVED`
- source IDs
- verdict: `PENDING | CONFIRMED | UNSUPPORTED | CONTRADICTED`
- `evidence_source_id`
- **exact `evidence_span`**
- verifier reason
- optional narrower suggested rewrite

Researcher provenance is only a hint. It is never accepted as evidence.

### `VerificationReport`

Machine-readable JSON containing every factual claim, every sentence audit record, verdict counts, exact evidence spans, any claims removed/rewritten during the one corrective pass, notes, and `gate_passed`. A report can fail, and a failed report blocks final `copy.md`, manifest, build, and QA.

### `HandoffRecord`

Timestamp, sender, receiver, summary, artifact hashes, and result. Handoffs never contain environment variables, request headers, or the API key.

## Run a real profile

Create a URL file:

```text
https://example.org/primary-record
https://example.org/credible-secondary-source
```

Set the key in your shell only:

```sh
export OPENAI_API_KEY='...'
# optional
export OPENAI_MODEL='gpt-5.6'
```

Then:

```sh
python -m pipeline.run \
  --name "Inductee Name" \
  --sources urls.txt \
  --out profiles/inductee-name/
```

The API key is read from `OPENAI_API_KEY`; it is never written to the profile, cache metadata, verification report, QA report, or handoff log. `.gitignore` excludes `.env`, key files, `node_modules/`, and `.profile-factory-cache/`.

## Build path

The existing builder now has an **add-only generic entry point**:

```sh
python albright-wp/build.py --profile-dir profiles/inductee-name/
```

That path delegates to `pipeline.generic_build` and derives the name, opening, credit/source note, standfirst, five sections, quotation attribution, discussion material, source register, and optional source note from the new profile's own `copy.md` + `media-manifest.csv`.

It never copies the Albright-only NARA `445648831` anchor, `Prague Winter` lookup, or the 1998 State Department documented-deviation text into another profile. Running `python albright-wp/build.py` with **no arguments** still executes the original Albright code path.

## Offline tests

The Python test suite makes **zero network requests and zero API calls**. LLM behavior is replaced with deterministic fake clients and all source content is local/in-memory.

```sh
python -m unittest discover -s tests -v
```

The falsification tests include:

- a planted unsupported factual sentence that must make the verifier gate fail;
- a supported sentence that passes only with an exact retrieved evidence span;
- a fake/nonexistent evidence span that mechanically downgrades `CONFIRMED` to `UNSUPPORTED`;
- a factual question that cannot bypass evidence simply because the model calls it editorial; and
- one rejected claim being rewritten from retrieved evidence, followed by a fresh independent audit before the gate can pass.

## QA requirements

A successful real run requires the existing QA stack and Chromium. As documented by the repo:

```sh
npm i playwright axe-core
export CHROMIUM=/path/to/chromium
```

`BuildQAAgent` runs `qa/integrity.mjs`, the existing browser harnesses (`dark`, `pixels`, `states`, `reflow`, `wp`, `nojs`, `targets`, `leak`, `interact`, `incomplete`), and the added `qa/profile-factory.mjs` against the generated profile. Missing QA dependencies are a **failed/unverified build gate**, never a pass.

## Cache

Fetched bytes and metadata live in `.profile-factory-cache/`, keyed by SHA-256 of the URL. Successful reruns use the cache. A cached failure remains explicitly `FETCH_FAILED`; it does not become an absence claim. Cached `UNPARSED` bytes are re-parsed on future runs, so installing a local parser such as `pdftotext` can recover a previously unparsed source without another network fetch.

## Honest limitations

- The current production researcher fetches the supplied seed URLs; it does **not** claim to be an autonomous exhaustive web search engine. Better seed sources improve the result.
- HTML/plain text are parsed with standard-library code. PDFs use local `pdftotext` when available; otherwise the source is recorded `UNPARSED` and cannot support a claim.
- LLM verification can still make judgment errors. The exact-span gate prevents unsupported citations from being silently accepted, and a repaired draft is independently re-audited, but neither proves that a supporting sentence was interpreted perfectly. Human sign-off remains mandatory.
- Rights text extraction is not legal advice. The agent preserves wording and uncertainty rather than manufacturing a license conclusion.
- Browser QA requires local Playwright, axe-core, and Chromium. If those dependencies cannot run, the profile is not marked done.
- The committed demo profile is a deterministic offline fixture demonstration, not proof that the live OpenAI path was exercised. It remains explicitly non-museum-ready and requires human sign-off.
