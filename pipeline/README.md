# Profile Factory

`pipeline/` is a **build-time-only** multi-agent pipeline for creating one Immigrant Hall of Honor profile from an inductee name and seed source URLs. The shipped visitor page remains static HTML generated from `copy.md` + `media-manifest.csv`: no visitor-side agent, API call, tracker, framework, external font, CDN, or remote script is added.

## Non-negotiable behavior

- **Honesty over completeness.** Failed retrieval means only `could not retrieve`; it is never evidence that a fact, record, image, or source does not exist.
- **Verifier independence.** Researcher provenance hints are not proof. The verifier receives retrieved source text directly and runs at `temperature=0`.
- **Exact evidence is mandatory.** `CONFIRMED` is mechanically downgraded unless the verifier names a retrieved source and provides an exact contiguous source span that is literally present in that source. The span must contain at least 24 characters and four words, with at least two distinct significant words shared with the claim. These lexical checks reject trivial citations; they do not prove entailment. Semantic support is still an LLM judgment, so human review remains mandatory.
- **Every visitor-facing factual surface is in scope.** The verification stream includes the H1 identity, narrative headings, body sentences, quotation text, quotation attribution, factual premises in questions/activities, and other factual copy. Pure structure/build-status language may be classified non-factual.
- **Visitor-visible manifest metadata is evidence too.** A generated source-card title must come from retrieved title metadata or an exact source span. Nonempty creator, date, institution, and gloss fields must be exact retrieved spans; otherwise they remain empty. This prevents the post-verifier media/rights stage from introducing fabricated historical metadata.
- **Source text is untrusted data.** Researcher, verifier, and rights prompts explicitly forbid obeying instructions embedded inside source material. Offline tests plant a prompt-injection string and require the unsupported claim to remain rejected.
- **One evidence-only remediation pass.** Rejected material may be removed or narrowly rewritten from retrieved evidence once; the revised draft must then survive a fresh audit. Remaining unsupported/contradicted/omitted material blocks the build.
- **No silent partial verification.** Verification and rights review have explicit source-size ceilings. If the evidence set exceeds them, the pipeline fails rather than truncating source text and pretending the audit was complete.
- **Rights honesty.** Institutional rights wording must be an exact retrieved source span, an explicitly evidenced `TRANSCRIBED ... NOT re-read` note, or `NOT LOCATED IN RETRIEVED SOURCE TEXT`. A public webpage or government institution is not automatically a rights grant.
- **Subject honesty.** An image subject is not asserted unless the specific retrieved item identifies it. Unverified subjects remain `SUBJECT UNCONFIRMED`; alt text is <=15 words and <=125 characters.
- **Frozen Albright deliverable.** The no-argument `albright-wp/build.py` path remains the legacy Albright builder. New profile output is accepted only at exactly `profiles/<slug>/`.
- **Human sign-off is terminally human.** The pipeline may reach `PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF`; it never automatically sets `MUSEUM READY`.

## Agent and message flow

```text
CLI
  ↓
Orchestrator (owns ProfileDraft + append-only handoff records)
  ↓
ResearcherAgent
  - fetches only supplied seed URLs
  - caches retrieved bytes locally
  - treats source text as untrusted evidence
  - drafts the existing copy.md contract
  ↓
VerifierAgent
  - audits visitor-facing factual units independently
  - temperature 0
  - exact source span required
  - one evidence-only remediation round at most
  - fresh re-audit after any remediation
  - hard stop on remaining non-CONFIRMED factual material
  ↓
MediaRightsAgent
  - emits the existing manifest schema
  - exact-span rights and visitor-visible metadata checks
  - URL, filename, subject and alt-text guardrails
  ↓
copy.md + media-manifest.csv + verification-report.json
  ↓
albright-wp/build.py --profile-dir profiles/<slug>/
  - separate generic path
  - static archival/editorial HTML only
  ↓
BuildQAAgent
  - generic build
  - existing static integrity
  - existing browser QA + nine-defect regression harness
  - generated-profile QA
  ↓
PIPELINE VERIFIED / HUMAN REVIEW REQUIRED
```

## Typed contracts

The dataclasses live in `pipeline/schema.py`.

### `ProfileDraft`

The single orchestration state object: name/slug, seed URLs, retrieved `SourceDocument`s, draft Markdown, claims, sentence audits, manifest rows, `VerificationReport`, handoffs, status, completion state, and failure reason.

### `SourceDocument`

Stores source id, requested URL, retrieval status (`RETRIEVED | FETCH_FAILED | UNPARSED`), title, retrieval time, content type, parsed text, SHA-256, error, and cache flag. Cached evidence is not trusted unless its body SHA-256 still matches metadata.

### `Claim`

A factual visitor-facing unit with:

- `claim_id`
- exact visitor-facing text
- provenance: `RECORD | QUOTATION | PARAPHRASE | INFERENCE | UNRESOLVED`
- source ids
- verdict: `PENDING | CONFIRMED | UNSUPPORTED | CONTRADICTED`
- `evidence_source_id`
- exact `evidence_span`
- verifier reason
- optional narrower rewrite

### `VerificationReport`

Machine-readable verdict counts, every claim, every visitor-facing sentence audit record, exact evidence spans, any removed/rewritten claims, notes, and the hard `gate_passed` result.

### `HandoffRecord`

Timestamp, sender, receiver, safe summary, artifact hashes, and result. Handoffs do not contain environment variables, request headers, or API keys.

## Run a real profile

Create a source URL file containing one public `http://` or `https://` URL per line:

```text
https://example.org/primary-record
https://example.org/credible-secondary-source
```

Then set the API key and an explicit currently supported model id in your shell only:

```sh
export OPENAI_API_KEY='...'
export OPENAI_MODEL='your-current-supported-model-id'
```

There is intentionally **no hard-coded production model default**. Model availability changes over time; requiring `OPENAI_MODEL` or `--model` prevents a once-valid default from silently aging into a broken production path. The selected model must support the parameters used by this pipeline, including verifier calls at `temperature=0`.

Run:

```sh
python -m pipeline.run \
  --name "Inductee Name" \
  --sources urls.txt \
  --out profiles/inductee-name/
```

or pass the model explicitly:

```sh
python -m pipeline.run \
  --name "Inductee Name" \
  --sources urls.txt \
  --out profiles/inductee-name/ \
  --model 'your-current-supported-model-id'
```

`--out` must resolve to exactly one direct child of `profiles/`, and its directory name must equal the slug generated from `--name`. Nested directories, traversal, `albright-wp/`, and arbitrary absolute destinations are rejected in both the CLI/orchestrator and generic builder.

## Build-time network/security boundary

The visitor page does not fetch anything. Build-time source retrieval accepts public HTTP(S) only. The production fetcher rejects localhost, loopback, link-local, RFC1918/private, multicast, reserved, unspecified, credential-bearing, non-HTTP(S), and unsafe redirect targets. The cache is keyed by URL and its retrieved body must match the stored SHA-256 before it can be reused as evidence.

Manifest URLs are independently validated before rendering. A generated media filename must be a safe local basename; path separators and traversal are rejected and resolved media paths must remain under the profile's `media/` directory.

`OPENAI_API_KEY` is read from the environment only. Provider errors are reduced to sanitized structured details and passed through central redaction before logging or CLI display. `.gitignore` excludes `.env`, key material, local browser dependencies, and Profile Factory caches.

## Context honesty

The Researcher may use bounded excerpts to draft, and visibly labels those excerpts when truncated. **The Verifier and MediaRightsAgent do not silently verify truncated evidence.** If a retrieved source is larger than their configured complete-review ceiling, or the total evidence set is too large, the gate fails with an explicit limitation instead of producing a false `CONFIRMED` result.

## Generic build path

```sh
python albright-wp/build.py --profile-dir profiles/inductee-name/
```

The generic path derives the name, opening, credit/source note, standfirst, five narrative sections, first-person quotation/attribution, discussion material, source register, and optional source note from that profile's own `copy.md` and `media-manifest.csv`. It does not copy the Albright-only NARA `445648831` anchor, `Prague Winter` lookup, or 1998 State Department deviation onto another inductee.

The generic visual treatment deliberately keeps the repo's existing archival DNA: warm paper tones, editorial serif type, burgundy/rust accent, restrained rules, native `<details>`, explicit evidence flags, deliberate missing-image states, and source cards. The redesign adds hierarchy and provenance clarity without adding JavaScript, an external font, a framework, or any remote visual dependency.

## Offline tests

All Python tests run with **zero network and zero API calls**:

```sh
python -m unittest discover -s tests -v
```

The suite includes falsifiable attacks on:

- a planted unsupported claim;
- fake/nonexistent evidence spans;
- factual headings and quotation attribution;
- factual premises hidden in questions;
- status-prefix attempts to disguise historical claims as build notices;
- source-text prompt injection;
- remediation followed by mandatory fresh re-audit;
- exact output containment;
- private/local URL fetches;
- corrupted or missing cache bodies / SHA mismatch;
- invented or unsafe manifest URLs;
- invented visitor-visible source metadata;
- media path traversal;
- unconfirmed image subjects;
- non-exact rights wording; and
- API-key leakage in mocked provider errors.

## Deterministic end-to-end demo

There is exactly one demo profile: `profiles/madeleine-albright/`. `pipeline/demo.py` uses deterministic offline source snapshots and a deterministic fake JSON client **through the real ResearcherAgent, VerifierAgent, MediaRightsAgent, Orchestrator, generic builder, and BuildQAAgent**. It makes no web or OpenAI call.

In an environment with the browser QA dependencies installed:

```sh
python -m pipeline.demo
```

The run succeeds only when verification and every relevant build/browser QA hard gate pass. Run-specific JSON/log evidence is generated during the run and uploaded by CI rather than committed as a stale snapshot. The demo proves orchestration and failure gates; it does **not** prove source freshness or substitute for a live production API/source run. Human re-reading of live sources remains required.

## QA

A release review should run:

```sh
npm install --no-save playwright axe-core
npx playwright install --with-deps chromium
python -m unittest discover -s tests -v
python albright-wp/build.py
node qa/integrity.mjs .
for t in dark nojs interact pixels states targets reflow leak incomplete wp repro; do
  node qa/$t.mjs
done
PROFILE_URL=http://127.0.0.1:8741/profiles/madeleine-albright/preview.html node qa/profile-factory.mjs
```

CI additionally archives the current checkout and runs the repo's exact `qa/rebuild.sh` clean-rebuild harness, then runs the deterministic demo and asserts `completed=true`, `verification_gate=true`, and BuildQA `passed=true` on that CI run. The generated-profile browser harness covers light/dark axe checks, no-JS/static-runtime assertions, print, reduced motion, non-inline target sizing, and reflow at 320/360/375/390/412/430/640/768/1024/1280/1440px, and it captures desktop/mobile screenshots for visual inspection.

## Honest limitations

Passing automated gates is not museum publication approval. The following remain outside the machine proof unless separately performed and documented:

- a screen-reader user evaluation;
- teen/visitor usability research;
- a nontechnical IHH volunteer handoff test;
- human item-level rights re-verification;
- independent human fact checking;
- real-host Lighthouse/network performance;
- a real production OpenAI/source run using the operator's selected model and API key; and
- any archival image that has not actually been downloaded and viewed.

A real LLM can still make a semantic judgment error even when it quotes a real source span. That is why the pipeline stops at **human review required**.

## Release hardening contract (2026-10-15)

A rerun invalidates previous completion and QA before research. Early returns and exceptions persist a failed state; `human_signoff` remains `REQUIRED` and `museum_ready` remains false. A successful automated run is not a human approval. Files left from an earlier run are diagnostic history; the current profile-state and QA report govern completion.

Source connections resolve and validate every address, then connect to the selected numeric address without a second DNS lookup. Redirects undergo the same checks. Ambient HTTP proxies are disabled for source retrieval, and HTTPS retains hostname certificate verification. Cache corruption is never accepted as evidence. Research excerpt sizes and truncation are recorded in source-index.json; verification and rights review reject sources over 60,000 characters or sets over 180,000 characters rather than silently reviewing a subset.

The Responses client requires an explicit model, sends JSON mode through `text.format`, disables response storage, requires completed response status, and rejects refusals and redirects. The selected model must support JSON output and the required temperature settings (verification uses 0); unsupported configurations fail rather than retrying with weaker verification. No live model compatibility is asserted by offline transport fixtures. Contract reference: https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses

CI rejects committed demo copy/manifest/HTML drift after an end-to-end rebuild. Four screenshots cover desktop and mobile in both color schemes. The print gate tests disclosures without opening them programmatically.
