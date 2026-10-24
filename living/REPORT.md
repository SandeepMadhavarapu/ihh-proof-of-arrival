# Living Museum: build report

Branch `ws2-living-museum`, started from the local feasibility-spike branch `ws2-spike` (88c45ba). The branch has no upstream, and nothing has been pushed. 17 October 2026.

## What was built

| Part | Files | What it does |
|---|---|---|
| Source allowlist | `living/sources.yaml`, `living/config.py` | Lists domains with a trust tier (1 = official or primary, 2 = established reference), the inductees' names and aliases, and the finder's seed pages. A strict parser needs no third-party package. Holds the kill switch (`living/PAUSED`) and the protected-path list. |
| Retrieval | `living/fetch.py`, `pipeline/cache.py` | Sends an identifying User-Agent and uses the same one for robots.txt (RFC 9309). Waits 3 s between requests to the same host. Keeps SHA-checked snapshots in the gitignored `living/.cache/`. Imports human snapshots (`retrieved_by=human`) and serves offline fixtures. Never rotates user agents or IPs, solves challenges or uses headless tricks. |
| Deterministic rules | `living/textnorm.py` | Whitespace normalization. Extracts numbers, written-out numbers ("twenty-nine" = 29), ordinals, months next to a number, and three numeric date formats. Detects superlatives and award words. |
| Five gates | `living/gates.py`, `living/judge.py` | **Gate 1** runs the *existing* `pipeline.verifier` span, length and token checks (through the real `VerifierAgent`) on the full fetched text. It also checks the allowlist, injection quarantine, that every number and superlative is quoted, the ±1,500-character entity window, and wrong-person names; every span must pass on its own. **Gate 2** requires two independent registrable domains, at least one tier 1, and every number stated by both. **Gate 3** is the blind judge: sentence plus ±2,000-character windows only, NEEDS HUMAN JUDGMENT without a key. **Gate 4** catches sources that disagree and contradictions with existing facts, turning them into a CONFLICT or correction item. **Gate 5** applies the `pipeline.media_rights` rules (exact rights wording). |
| Verifier | `living/verifier.py` | Takes only the sentence, URLs, spans and media fields, never the finder's reasoning. Re-fetches every URL itself. |
| Finder | `living/finder.py` | Extractive, no model needed. Reads seed pages, keeps block-bounded sentences that name the inductee and state a date or honour, de-duplicates against `copy.md`, verified facts and the queue, and looks for corroboration on other domains. Optional `--rewrite` with a model key. |
| Proposals and audit | `living/proposals.py`, `living/proposals/` | One JSON file per proposal, never deleted. The append-only `audit.log.jsonl` is SHA-256 hash-chained, so edits and deletions are detectable. |
| Review dashboard | `living/review_app/server.py` | Private and bound to 127.0.0.1. Works without JavaScript and is CSRF-protected. Shows the claim against highlighted spans, tier badges, corroboration count, gate table and change diff. Approve, Approve-and-branch and Reject (with reason) write the decision and an audit entry. |
| Publisher | `living/publisher.py` | The **only** writer of `copy.md`, manifests and `site/`. Refuses anything unapproved or any correction. Re-checks gates 1–2 against fresh fetches. Appends to the section with a `{verified:ID}` marker, adds cited-reference manifest rows (existing bytes kept), and stores evidence forever in `inductees/<slug>/verified-facts.json`. Adds a "New at the Museum" entry, rebuilds, and runs `qa/rebuild.sh`. Optionally creates branch `living/<ID>`, commits, and writes a PR body. Never sets MUSEUM READY and never pushes. |
| Watchdog | `living/watchdog.py`, `living/health.json`, `living/demo/` | Re-checks every source of every published fact. Drift opens a re-verification item; content is never deleted. `--simulate` uses a clearly labelled local fixture in a separate queue. |
| CLI | `living/run.py` | `find`, `verify` (`--recheck`), `review`, `publish`, `watchdog`, `eval`, `import-snapshot`, `import-spike`, `export-wp`, `status`. The kill switch stops everything except `status`. Supports `--max-fetches`, `--max-seconds`, `--max-llm-calls` and `--dry-run`. |
| WordPress export | `living/export.py` | Writes "New at the Museum" as one copy-paste Custom HTML block. Profiles were already copy-paste blocks (`copy.html`). |
| Anthropic provider (S3) | `pipeline/llm.py` | `AnthropicJSONClient`: official SDK imported lazily, key from `ANTHROPIC_API_KEY`, model from `ANTHROPIC_MODEL` (no default), structured JSON output. Refusals and truncation fail closed. No silent model fallback. See the limits below on temperature. |
| Public site | `tools/build_profile.py`, `tools/build_site_pages.py`, `site-data/`, `site/new.html`, `site/assets/site.css` | **Verified badge** ("✓ Verified · Sources N · Last checked [date]", linking to the page's own source cards) only on facts approved through the Living Museum. Profiles without one are byte-identical to before. **New at the Museum** page with an honest empty state. Publishing only from the slug allowlist `site-data/published.json`. |
| Publish safety (S6) | `site-src/`, `.github/CODEOWNERS`, `living/BRANCH-PROTECTION.md`, `.gitignore` | Moved `gen.py`, `cases.py`, `FINDINGS.md`, `SITE-README.md`, `TESTS-RUN.md` and the manifest README out of `site/`, keeping `verify.html` byte-identical. Untracked `site/__pycache__/*.pyc`. Added CODEOWNERS and written branch-protection settings; no GitHub setting was changed. |
| Evaluation | `living/eval/` | `suite.py` (cases), `fixtures.json` (excerpts of pages fetched over the network), `run_eval.py` (in CI; fails on any false accept or undeclared negative route), `run_judge_eval.py` (blind judge eval, needs a key), `RESULTS.md`. |
| CI and workflow | `.github/workflows/profile-factory-ci.yml`, `.github/workflows/living-museum.yml` | CI now runs the gate eval. The Living Museum workflow is manual (`workflow_dispatch`), with its cron commented out. It needs a secret you add, honours the kill switch, opens a draft PR with proposals only, and never pushes to `main`. |
| Docs | `living/README-FOR-IHH.md`, `living/DEMO-SCRIPT.md`, this report | |

## Evaluation (`living/eval/RESULTS.md`)

All figures are offline and deterministic, with no network and no key, run on 75 negative and 56 positive cases.

| Measurement | Result |
|---|---|
| **False accepts** | **0 / 75** |
| Negatives rejected by the deterministic gates alone | **72 / 75** |
| Negatives sent to conflict review (sources disagree) | 2: Berlin Congressional Gold Medal 1955 vs 1954; Naismith honorary MA 1911 vs 1910 |
| Negatives routed to a person (declared) | 1: "Madeleine Albright was a politician and an author" (no number or award; meaning only) |
| Positives reaching the human queue (deterministic recall) | 20 / 56 = 0.357 |
| Deterministic precision | 0.952 (20 positives, plus 1 declared negative) |
| Positives passing Gate 1 (evidence) alone | 49 / 56 |
| S2 recall: existing gate on IHH `Field: value` labels, then full Gate 1 on visitor sentences | 34 / 48, then **41 / 48** |
| Semantic gate | **Not yet measured** (no API key) |

**S1 against target.** The target was that the deterministic gates alone reject 100% of negatives, routing anything they can't decide to a person. The result is 72 of 75 rejected, 2 routed to conflict review and 1 routed to human judgment. **None accepted.** The family breakdown, including the four known IHH errors and the 15 human-reviewed over-claims, is in `RESULTS.md`.

**S2.** Recall rose from 34 to 41 of 48, with no new false accept (the suite re-runs on every change). The 36 positives that don't reach the queue are almost all Gate 2 doing its job: one source, or no tier-1 source, for a date or award. They are listed with reasons.

## Demo results (real network, 17 October 2026)

- **Finder** ran live on **naismith, lamarr and muir**. It fetched 12 seed pages and all were retrieved. The first run's splitter glued page blocks together, so I fixed it (block-aware v2). The 7 malformed v1 candidates were marked rejected with that reason by "Claude Code (developer housekeeping)", not deleted. The audit log records this.
- **Spike candidates (S7):** 9 imported, including the 1910-vs-1911 item, and re-run through the new gates.
- **Queue now: 36 proposals, 6 pending human decision, 0 approved.**

| ID | Kind | Verdict | Sentence |
|---|---|---|---|
| LM-0021 | correction | CONFLICT | Encyclopedia.com: "She was born Hedwig Kiesler in 1913 in Vienna…". This contradicts our copy's 9 November 1914. |
| LM-0030 | fact | CONFLICT | Naismith honorary MA in 1911 (DCB) vs 1910 (FIBA). This is the S7 conflict item; it cannot be approved by button. |
| LM-0033 | fact | NEEDS HUMAN JUDGMENT | The U.S. Navy did not use Lamarr and Antheil's frequency-hopping invention during World War II. (si.edu + encyclopedia.com) |
| LM-0034 | fact | NEEDS HUMAN JUDGMENT | Frequency hopping based on the Lamarr-Antheil concept was used in U.S. military communications during the Cuban Missile Crisis in 1962. (si.edu + encyclopedia.com) |
| LM-0035 | fact | NEEDS HUMAN JUDGMENT | Lamarr starred in the films Ziegfeld Girl and Samson and Delilah. (invent.org + encyclopedia.com) |
| LM-0036 | fact | NEEDS HUMAN JUDGMENT | Neither Lamarr nor Antheil ever earned money from their invention. (invent.org + encyclopedia.com) |

- **Rejected spike candidates:** The four other Naismith candidates (France 1917–19, LLD 1938, McGill 1889, Denver 1895) were rejected by Gate 2. Each has two independent domains, but both are tier 2 (biographi.ca, fiba.basketball, ku.edu).
- **Rejected finder candidates:** Every new finder candidate except LM-0021 was rejected, mostly for having a single source for a date.
- **Watchdog simulation:** It caught the deliberately edited span and opened a re-verification item in the separate simulation queue. The real watchdog reports 0 published facts (`living/health.json`).
- **Not done yet:** publishing, the badge and New at the Museum entries. Those wait for your approvals in chat.

## Limitations, stated plainly

1. **The semantic judge is unmeasured.** No key was set, so Claude Code did not act as the judge in the shipped system. Every proposal that passes the deterministic gates is NEEDS HUMAN JUDGMENT until `living/eval/run_judge_eval.py` is run with a key.
2. **Temperature 0 is not available on current Claude models.** Opus 4.7 and later, and the 5.x family, reject sampling parameters with HTTP 400. The client sends `temperature=0` only to models that accept it (`claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`) and otherwise records "model default sampling". Consistency must be measured with `run_judge_eval.py --repeats 3`.
3. **Corroboration is strict by design.** Under the tiers in `sources.yaml`, no dated Naismith fact can pass, because every Naismith source is tier 2. Whether a university archive (e.g. KU Libraries) should count as tier 1 is a policy decision for you; I did not re-tier anything to make the demo pass.
4. **"Independent" domains can copy each other.** The Songwriters Hall of Fame biography of Berlin largely reproduces the estate's text, yet the two disagree on the Congressional Gold Medal year. Domain independence is not proven independence.
5. **Allowlisted pages contain errors and copied prose.** FIBA lists McGill "1983-1987"; walkoffame.com carries copied biography text and a death date of "-0001-11-30". Two sources plus a human remain necessary.
6. **Some references refuse the fetcher** (HTTP 403 from Britannica, Congress.gov and parts of si.edu). They are recorded as "could not retrieve". The human-snapshot import is the honest route; there is no workaround. Two eval cases (Cruz bill, Einstein-Britannica) are rejected only because of this, so they do not test the logic.
7. **The finder is extractive.** Without a model it proposes the source's own sentence, flagged "needs editor" for ages 12–18. It found few corroborated candidates. Its sentence splitting and duplicate checks are heuristics (e.g. it proposed John Muir College catalogue text, which the gates rejected).
8. **Gate 4 topic matching is a heuristic** (shared significant words). It can miss conflicts phrased differently and can flag false ones; flagged items only go to a person.
9. **The injection check is a phrase list.** It cannot catch every injection, and a compromised allowlisted page that states a false fact plainly would pass Gates 1–2. That risk is why Gate 2 needs two domains and a human approves.
10. **Fixtures are excerpts** (about ±2,500 characters around cited spans) of pages fetched on 17 October 2026. `living/eval/build_fixtures.py` needs a local fetch cache to rebuild them; the spike cache it once read was deleted with `spike/`.
11. **The "Last checked" date on the public badge is the approval date.** The watchdog's ongoing checks go to the private `living/health.json`. Refreshing a public date means a new approved PR.
12. **Browser harnesses were not run.** Playwright isn't installed here, so `qa/*.mjs` axe, contrast, reflow and no-JS checks for `new.html` and the badge are unverified locally. CI runs them. `qa/integrity.mjs` (no browser) passes 149 / 149.
13. **No `gh` CLI here.** When you say "push" I can push the branch, but you will have to open the draft PR yourself.

## QA run for this report

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 98 tests, OK (was 50: +4 PDF regression, +4 Anthropic client, +40 Living Museum) |
| `python living/eval/run_eval.py` | EVAL PASSED: 0 false accepts |
| `bash qa/rebuild.sh` | ALL GENERATED FILES MATCH THEIR SOURCES (now includes `site/new.html`) |
| `python qa/handover.py` | PASS all ten handover packages |
| `python qa/secrets.py` | PASS |
| `node qa/integrity.mjs .` | ALL 149 INTEGRITY CHECKS PASSED (site weight restated: 466 KB, twenty-one pages) |
| Playwright `qa/*.mjs` browser checks | **Not run** (Playwright not installed) |
| `git grep "ihh-content-reconciliation" site/` | no matches |

## Files changed

See `git diff --stat ws2-spike..ws2-living-museum`. Summary:

- **New:**
  - `living/` (all of the above);
  - `site-data/published.json`, `site-data/new-at-the-museum.json`;
  - `site/new.html`;
  - `.github/CODEOWNERS`, `.github/workflows/living-museum.yml`;
  - `tests/test_living.py`, `tools/__init__.py`.
- **Moved:** `site/{gen.py,cases.py,FINDINGS.md,SITE-README.md,TESTS-RUN.md,media-manifest.README.txt}` to `site-src/`.
- **Modified:**
  - `pipeline/cache.py` (PDF fix, User-Agent parameter);
  - `pipeline/llm.py` (Anthropic client);
  - `tools/build_profile.py` (badge), `tools/build_site_pages.py` (allowlist, new page);
  - `qa/rebuild.sh`, `qa/integrity.mjs`;
  - `site/assets/site.css`, `site/inductees.html`, `site/sitemap.xml`, `site/method.html`;
  - `.github/workflows/profile-factory-ci.yml`, `.gitignore`;
  - `CONTRIBUTING.md`, `README.md`;
  - `tests/test_cache.py`, `tests/test_llm.py`.
- **Removed:** `spike/` (its useful code is folded into `living/`; its candidates are kept in `living/demo/spike-candidates.json`), and the tracked `site/__pycache__/*.pyc`.
