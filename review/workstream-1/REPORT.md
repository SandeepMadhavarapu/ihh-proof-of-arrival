# Workstream 1 review — 17 October 2026

Status: PR review requested; **not approved for museum publication**. Base: `preview-muir-homepage`, `4fab8601a2cdd1f474e592da38833b131f71d61c`. Workstream 2 has not started.

## 1. Changes

| Files | Change and purpose |
|---|---|
| `tools/build_profile.py` | Use the existing, nonempty tracked `media/web/` derivative when the full-resolution original is absent; do not recompress it. |
| `tools/package_handover.sh` | Assemble all ten packages, preserve editorial notes, report absent logs, reject stale orphan logs, avoid nested media on repeat runs and produce a deterministic ZIP. |
| `tools/open_items.py`, `handover/OPEN-ITEMS.md` | Explicit six missing-log items, editorial/reconciliation sign-off and Muir correction approval. |
| `handover/{berlin,einstein,hope,muir,naismith,strauss}/` | Copy the existing generated profiles, manifests and tracked web images into the same handover format as the original four. |
| `handover/*/ihh-content-reconciliation.md` | Ten private inventories preserving IHH facts, achievements and honours; scoped evidence, proposed corrections, failed retrievals and unresolved checks. |
| `handover/INSTALL.md` | Ten-profile installation guidance; private notes, missing research records and publication approval requirements. |
| `qa/catalog.mjs`, `qa/{dark,incomplete,integrity,nojs,pixels,reflow,repro,states,targets,wp}.mjs` | Discover all ten profiles and all twenty pages. Preserve original four-profile minimums; assess newer profiles against authored optional quotations and exact non-dropped manifest row counts. Parse CRLF CSV headers correctly and count both HTTP and HTTPS source links. |
| `qa/rebuild.sh` | Compare generated text, handover manifests/logs and all three copies of tracked profile media for all ten. |
| `qa/handover.py` | Check package/media parity, private reconciliation sections and explicit missing-log disclosures. |
| `qa/secrets.py` | Check all tracked text formats, including Markdown, for key-like strings without printing matched secrets. |
| `tests/test_web_fallback.py` | Regression tests for absent originals and absent/empty derivatives. |
| `.github/workflows/profile-factory-ci.yml` | Include workstream/preview pushes and the all-ten handover and tracked-file secret checks. Existing browser and pipeline gates remain. |
| `site/sitemap.xml` | Include six additional exhibit URLs, retaining the nonproduction example.invalid host. |
| `site/assets/site.css` | Repair the malformed hero-kicker selector; remove its unintended pseudo-element rule across text. No contrast threshold was relaxed. |
| `site/{FINDINGS.md,SITE-README.md,TESTS-RUN.md,method.html}` | Update the obsolete aggregate site weight/page-count claim to the measured twenty-page package. |
| `POSITIONING.md`, `ROADMAP.md` | Record openness to a new website as reported by the team lead from the sponsor meeting, not a written IHH commitment. |
| `review/workstream-1/` | Actual terminal outputs, screenshots and this report. These are dated review evidence, not a claim about future revisions. |

## 2. Evidence

The raw final outputs are in `QA-OUTPUTS.md` and individual `.txt` files beside this report. Browser: local Chromium 153.0.8010.0 through Playwright. Standard Playwright browser download failed in this environment; the Chromium binary came from the installed `@sparticuz/chromium` package. No browser binary or dependency directory is committed.

A separate `git clone --no-local` of the implementation commit had no full-resolution originals. Its rebuild and package checks are recorded in `fresh-clone-rebuild.txt`. Source biography Markdown and `.gitignore` retain their original bytes. The ten handovers use existing media; no original was added.

Screenshots are viewport captures with reduced motion, at 1280×900 and 375×900. They document the homepage, Muir exhibit and simulated WordPress handover. They do not establish compatibility with IHH’s actual WordPress theme.

| Page | Desktop | 375 px phone |
|---|---|---|
| Homepage | [Screenshot](homepage-1280.jpg) | [Screenshot](homepage-375.png) |
| Muir exhibit | [Screenshot](muir-1280.jpg) | [Screenshot](muir-375.png) |
| Muir handover | [Screenshot](handover-muir-1280.png) | [Screenshot](handover-muir-375.png) |

Failures encountered and resolved:

- `1 FAILED of 148`: the new source-count check initially read CRLF `recommendation` headers incorrectly; the parser now strips the record-ending CR, preserving manifest bytes.
- `1 FAILED of 308`: `albright: 12 evidence links cover the source register`. Three existing source URLs use HTTP. The browser selector now includes HTTP and HTTPS; no link was fabricated or source minimum reduced.
- Pixel check: `1.92 < 4.5 light method kicker: Method` and `1.92 < 4.5 light verify kicker: An interactive exhibit`, repeated for dark preference. The malformed hero kicker selector (a doubled `section` prefix) allowed the decorative rule to span the element sampled by QA. Correcting the selector restored the intended layout and the pixel check passed.
- Initial browser attempts returned `net::ERR_CONNECTION_REFUSED`; local servers are now kept alive for each QA command group.
- Initial deterministic pipeline run failed because `/usr/bin/chromium` did not exist. The rerun explicitly sets `CHROMIUM=/tmp/ihh-chromium`.
- `git diff --check` flags pre-existing whitespace in the six newly copied generated HTML/CSV packages. Those bytes intentionally match the existing sources, including their CRLF manifests; they were not normalized.

## 3. Factual changes to profiles

**One, approved.** `inductees/muir/copy.md` line 4: “In March 1868 a thirty-year-old Scot landed in San Francisco” → “In March 1868 a twenty-nine-year-old Scot landed in San Francisco”. The NPS chronology gives the birth date as 21 April 1838 and San Francisco arrival as 28 March 1868; the age is date arithmetic. The team lead approved the change; it was applied in commit a43f408 and the built outputs, `handover/muir/*` and `site/muir.html` were regenerated. No other `copy.md` or media manifest was edited. The reconciliation files otherwise contain proposals only.

Other proposals concern IHH’s source pages: Einstein’s Princeton arrival, Hope’s immigration year, Yosemite’s establishment date, Pei project dates, and Naismith’s role/date boundaries. Each is scoped in its private reconciliation; no live page or repository biography was changed.

## 4. New images or recordings

**None.** Six existing tracked web portraits were copied to the new handover folders byte-for-byte. Existing item URLs, rights wording and credits remain in the copied manifests. The review screenshots are QA evidence, not new historical collection material. No recording, synthetic voice, video or historical image was generated.

## 5. Not done / needs a human

- Search logs for **muir, einstein, hope, berlin, naismith, strauss** now exist but are partial (section 7). The original 2026-10-16 search terms for Muir, Einstein, Hope and Berlin were not preserved; each of those logs declares the gap as a FOLLOW UP item rather than reconstructing queries.
- 23 IHH facts/awards remain **NOT VERIFIED** in the reconciliation (section 7). They need exact institutional evidence and editorial review before adoption. Successful software checks do not establish historical correctness.
- Approval is needed for any further change to profile facts (Muir’s age correction is approved and applied). Existing protected Naismith, Strauss, Hope, Berlin and Einstein facts were not replaced.
- Public facts/achievements/honours blocks have not been expanded with unapproved claims. IHH’s structure is preserved in the private inventories; applying supported structured content to public profiles awaits approval.
- Existing media rights/identity questions and all byline placeholders remain. No person has signed; no package is marked museum-ready.
- Actual museum WordPress installation, volunteer usability testing and production configuration remain untested.
- The creator of `fix/four-inductee-rebuild` is **unknown** from accessible evidence. Its ref points to `dbf2476398fdc31e04fc622b5d00e5de8982257b`; the available public creation-event history did not identify its creation. Commit authorship does not prove branch creation. The branch was neither used nor deleted.
- No merge, deployment, live IHH change, email or external message was performed. CI status on the PR is separate from the local evidence.

## 6. Uncertainties and decisions

The new six have fewer source items than the original four and Hope/Strauss omit an optional quotation. The updated checks retain the original minimums for the original profiles, verify every non-dropped manifest row for all ten, and match quotation count to the authored input. They do not manufacture sources or quotations to meet a count.

Blocked retrievals are documented as retrieval failures. In particular, an inaccessible bill page cannot prove either an award or its absence. Naismith appointment dates and playing-season dates are kept distinct; the university account raises a question rather than authorizing replacement of the protected repository interval.

The private review notes and missing logs are not visitor navigation. A new website remains an optional later workstream; the sponsor-meeting report does not authorize deployment.

## 7. Review fixes — second pass, 17 October 2026

### Muir arrival age (approved)

Applied as described in section 3 (commit a43f408).

### Hero CSS scoping

In `site/assets/site.css`, every hero selector is now scoped as `section.hero:not(.arrival-hero) …`. That covers `.lede::first-letter` (two places), `.kicker`, `.kicker::after`, `h1` and `.cta`. The homepage arrival hero is unchanged; the verify and method pages get the centred kicker and drop cap. A repository-wide search for the doubled `section` selector typo returns nothing.

| Viewport | Before / after |
|---|---|
| 1280 px | [Screenshot](css-hero-before-after-1280.jpg) |
| 375 px | [Screenshot](css-hero-before-after-375.jpg) |

### Reconciliation regenerated from evidence

`tools/write_reconciliation.py` renders each `handover/<slug>/ihh-content-reconciliation.md` from `review/workstream-1/evidence/<slug>.json`. Every row now has its IHH claim, a per-row status, the source label and URL, the exact quoted span(s), retrieval date 2026-10-17 and a specific note, replacing the 190 boilerplate NOT VERIFIED rows. The existing header, open items, the `## Facts`, `## Achievements` and `## Honours` headings and `REQUIRES HUMAN SIGN-OFF` are kept. `qa/rebuild.sh` now also proves each note regenerates byte-identically from its evidence file. The notes remain private; `git grep -n "ihh-content-reconciliation" site/` returns nothing.

Span verification: every quoted span was checked against the live page text after collapsing whitespace (`innerText` or `textContent`). Batches vb0–vb5 were checked in the previous session; vb6–vb9 (22 URLs) were checked in this session, and every span was found. No page was blocked. The Haus der Bayerischen Geschichte biography is a PDF; its two spans were checked against the PDF text layer.

| Profile | Rows | CONFIRMED | PARTLY CONFIRMED | CORRECTION SUGGESTED | NOT VERIFIED | NO CLAIM |
|---|---|---|---|---|---|---|
| Albright | 21 | 9 | 5 | 1 | 6 | 0 |
| Berlin | 21 | 13 | 2 | 4 | 1 | 1 |
| Cruz | 19 | 6 | 3 | 4 | 5 | 1 |
| Einstein | 21 | 16 | 2 | 3 | 0 | 0 |
| Hope | 26 | 13 | 3 | 3 | 7 | 0 |
| Lamarr | 14 | 9 | 3 | 0 | 2 | 0 |
| Muir | 19 | 10 | 4 | 3 | 2 | 0 |
| Naismith | 20 | 14 | 1 | 5 | 0 | 0 |
| Pei | 24 | 19 | 1 | 4 | 0 | 0 |
| Strauss | 14 | 9 | 2 | 2 | 0 | 1 |
| **Total** | **199** | **118** | **26** | **29** | **23** | **3** |

Status audit: CONFIRMED now means every component of the IHH claim is in a quoted span. Rows revised on that basis: Albright L15, Hope L27, Naismith L31, Strauss L29 and L30 → PARTLY CONFIRMED; Hope L46, Strauss L31 and L32 → CORRECTION SUGGESTED; Strauss L15 → NO CLAIM. Strauss L13 (place of death) and L17 (citizenship) are CONFIRMED with an added Haus der Bayerischen Geschichte span.

Key corrections suggested to IHH (all in the private notes, with spans):

- **Naismith:** BA 1887 in philosophy and Hebrew (KU Libraries), not 1888 physical education; football headgear fall 1891, not 1893; instructor (not head) at the YMCA Training School; coached Kansas until 1907; KU News says he chaired the department until 1924 (one account; flagged for KU Archives).
- **Muir:** “1903” is a passport application, not his citizenship date; Yosemite became a national park in 1890; Grand Canyon National Park 1919 (1908 was the monument); the Wisconsin Historical Society holds his clockwork desk, not the bed; Muir wrote “hygrometers”.
- **Einstein:** ETH diploma July 1900 (1911 was the school’s renaming); general relativity paper 1916; einsteinium discovered 1952, announced 1955.
- **Hope:** Academy honours were honorary or special only, never a competitive Oscar; Golden Globes record one win (1958), DeMille year unconfirmed; Congressional Gold Medal authorized 8 June 1962 and presented 9/11/63; the Bob Hope Humanitarian Award was first given to Oprah Winfrey in 2002.
- **Berlin:** born Israel Beilin (estate) / Baline (Encyclopedia.com), not “Berlin”; citizenship 6 February 1918; “over 1000 songs”; 17 complete Broadway scores plus material for 6 more; Kennedy Center Honor not verified.
- **Cruz:** the Congressional Gold Medal bill H.R.149 was introduced but never enacted; the quarter is 2024; three Grammys, not two.
- **Pei:** JFK Library 1979, Texas Commerce Tower 1982, Louvre pyramid 1989, East Building 1978.
- **Albright:** born “Marie Jean ‘Madlenka’ Korbel” (State Department historian).
- **Strauss:** the 2023 company revenue and The Wild One (1953) are the brand’s story, not his achievements.

Notes on our own profiles, for human review only (no `copy.md` changed): LS&Co.’s company history implies Strauss emigrated about 1848, while our copy (and the HdBG biography) say 1847. The Berlin estate spells his birth name “Beilin”, while our copy uses “Baline” only.

### Search logs written

`inductees/<slug>/search-log.csv` now exists for **muir, einstein, hope, berlin, naismith and strauss**, using the existing header and LF line endings. Researcher: `Claude (AI) — for team review`. Rows come only from the real record:

- the 22 preserved research calls of 2026-10-16/17: 16 are Naismith or Strauss research and are logged under those profiles; the IHH homepage, Founding Voices, mission, tell-your-story pages and the challenge brief belong to no single inductee and are not logged;
- one row per source in each evidence file (the 2026-10-17 reconciliation retrievals), with the rows it supports, or DEAD END where a tried page did not contain the claim.

Declared gap: for Muir, Einstein, Hope and Berlin, a FOLLOW UP row states that the original 2026-10-16 search terms were not preserved and only the sources recorded in `media-manifest.csv` are known. No query was invented or reconstructed. These rows now appear in `handover/OPEN-ITEMS.md` in place of the former missing-log items. The Muir “profile correction approval required” item is gone because the correction is applied.

### QA, second pass

| Check | Result | Output |
|---|---|---|
| `python -m unittest discover -s tests` | 50 tests, OK | `python-tests.txt` |
| `python qa/handover.py` | PASS all ten handover packages | `handover.txt` |
| `python qa/secrets.py` | PASS | `secrets.txt` |
| `bash qa/rebuild.sh` | ALL GENERATED FILES MATCH THEIR SOURCES (174 files, including the ten reconciliation notes) | `rebuild.txt` |
| `node qa/integrity.mjs .` | ALL 148 INTEGRITY CHECKS PASSED | `integrity.txt` |
| `node qa/catalog.mjs .` | exit 0 | — |
| `git grep -n "ihh-content-reconciliation" site/` | no matches | — |
| Playwright harnesses (`dark`, `pixels`, `reflow`, `states`, `targets`, …) | **Not run in this pass:** Playwright is not installed on this machine. The earlier outputs in this folder predate these changes; CI runs the browser gates. | — |

Run on Windows with Python 3.12 in UTF-8 mode (`PYTHONUTF8=1`); without it, `qa/handover.py` and `tools/open_items.py` read and write files in the cp1252 code page and fail on curly quotes.
