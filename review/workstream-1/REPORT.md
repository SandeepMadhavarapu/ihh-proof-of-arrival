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
- Pixel check: `1.92 < 4.5 light method kicker: Method` and `1.92 < 4.5 light verify kicker: An interactive exhibit`, repeated for dark preference. The malformed `sectionsection.hero` kicker selector allowed the decorative rule to span the element sampled by QA. Correcting the selector restored the intended layout and the pixel check passed.
- Initial browser attempts returned `net::ERR_CONNECTION_REFUSED`; local servers are now kept alive for each QA command group.
- Initial deterministic pipeline run failed because `/usr/bin/chromium` did not exist. The rerun explicitly sets `CHROMIUM=/tmp/ihh-chromium`.
- `git diff --check` flags pre-existing whitespace in the six newly copied generated HTML/CSV packages. Those bytes intentionally match the existing sources, including their CRLF manifests; they were not normalized.

## 3. Factual changes to profiles

**None.** No `inductees/*/copy.md` or media manifest was edited. The reconciliation files contain proposals only.

One proposal concerns our current Muir draft: “In March 1868 a thirty-year-old Scot landed in San Francisco” → “In March 1868 a twenty-nine-year-old Scot landed in San Francisco”. The NPS chronology gives the birth date as 21 April 1838 and San Francisco arrival as 28 March 1868. The proposed age is date arithmetic; the exact spans and source link are in Muir’s reconciliation. Approval is required before applying it.

Other proposals concern IHH’s source pages: Einstein’s Princeton arrival, Hope’s immigration year, Yosemite’s establishment date, Pei project dates, and Naismith’s role/date boundaries. Each is scoped in its private reconciliation; no live page or repository biography was changed.

## 4. New images or recordings

**None.** Six existing tracked web portraits were copied to the new handover folders byte-for-byte. Existing item URLs, rights wording and credits remain in the copied manifests. The review screenshots are QA evidence, not new historical collection material. No recording, synthetic voice, video or historical image was generated.

## 5. Not done / needs a human

- Actual external research logs remain missing for **muir, einstein, hope, berlin, naismith, strauss**. The team lead must supply them. The packager emits each OPEN ITEM and does not create a replacement log.
- Many IHH facts/awards are **NOT VERIFIED** in the reconciliation. They need exact institutional evidence and editorial review before adoption. Successful software checks do not establish historical correctness.
- Approval is needed for Muir’s age correction and any other change to profile facts. Existing protected Naismith, Strauss, Hope, Berlin and Einstein facts were not replaced.
- Public facts/achievements/honours blocks have not been expanded with unapproved claims. IHH’s structure is preserved in the private inventories; applying supported structured content to public profiles awaits approval.
- Existing media rights/identity questions and all byline placeholders remain. No person has signed; no package is marked museum-ready.
- Actual museum WordPress installation, volunteer usability testing and production configuration remain untested.
- The creator of `fix/four-inductee-rebuild` is **unknown** from accessible evidence. Its ref points to `dbf2476398fdc31e04fc622b5d00e5de8982257b`; the available public creation-event history did not identify its creation. Commit authorship does not prove branch creation. The branch was neither used nor deleted.
- No merge, deployment, live IHH change, email or external message was performed. CI status on the PR is separate from the local evidence.

## 6. Uncertainties and decisions

The new six have fewer source items than the original four and Hope/Strauss omit an optional quotation. The updated checks retain the original minimums for the original profiles, verify every non-dropped manifest row for all ten, and match quotation count to the authored input. They do not manufacture sources or quotations to meet a count.

Blocked retrievals are documented as retrieval failures. In particular, an inaccessible bill page cannot prove either an award or its absence. Naismith appointment dates and playing-season dates are kept distinct; the university account raises a question rather than authorizing replacement of the protected repository interval.

The private review notes and missing logs are not visitor navigation. A new website remains an optional later workstream; the sponsor-meeting report does not authorize deployment.
