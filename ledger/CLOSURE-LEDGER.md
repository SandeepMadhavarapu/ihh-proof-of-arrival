# Closure ledger

**116 findings.** Generated 11 October 2026 by `emit.py` from `findings.py`.
Machine-readable copies: `CLOSURE-LEDGER.json`, `CLOSURE-LEDGER.csv`.

| Status | Count |
|---|---|
| FIXED&ndash;VERIFIED | 110 |
| BLOCKED&ndash;EXTERNAL | 2 |
| NOT APPLICABLE&ndash;JUSTIFIED | 3 |
| OPEN | 1 |

> **This ledger does not close the 72-finding audit.** `IHH-V3-DEEP-AUDIT.md` was named as
> required reading but was not supplied to this session; only the evidence ZIP arrived. See
> META-01. Any of those 72 findings not independently rediscovered here remains unaddressed.

---


## P0 &mdash; Privacy / false claim (29)

### META-01 &mdash; BLOCKED-EXTERNAL

**Concern.** IHH-V3-DEEP-AUDIT.md containing 72 findings was listed as required reading.
**Source of the concern.** Task instruction §1
**Affected.** `n/a`
**Our reproduction / verification.** Searched the uploads directory and the entire filesystem: only 129d3ced-IHH-V3-AUDIT-EVIDENCE.zip was supplied. No file named IHH-V3-DEEP-AUDIT.md or containing 72 enumerated findings exists in this session.
**Root cause.** Attachment not transmitted.
**Correction.** Proceeded with every independently verifiable source: the 9 findings in the evidence ZIP (all reproduced), the 6 residual defects named in task §4, and the findings from three independent verification passes commissioned for this repair. This ledger holds 116 findings, not 72.
**Evidence of closure.** ledger/missing-attachment.txt records the filesystem search.
**Remaining limitation.** Any of the 72 findings not independently rediscovered remains unaddressed. This ledger must not be read as closing that audit.

### R-01 &mdash; FIXED-VERIFIED

**Concern.** The story form submitted email and story text through a GET URL.
**Source of the concern.** Task §4 (privacy)
**Affected.** `share.html`
**Our reproduction / verification.** Reviewer's browser-results.json captured formURL with email=audit%40example.invalid and story=SYNTHETIC+AUDIT+TEXT in the query string. Reproduced here before fixing.
**Root cause.** <form> had no method and no action, so the browser defaulted to GET against the same URL, placing personal data in the address bar, history and any referrer. There is also no submission backend of any kind.
**Correction.** Removed the collection form entirely. Replaced with an honest explanation that this demonstration cannot receive submissions, plus a link to IHH's real submission route and the consent terms they actually use today.
**Evidence of closure.** qa/integrity.mjs asserts no form on any page can submit by GET, and that share.html contains no input element.

### R-03 &mdash; FIXED-VERIFIED

**Concern.** The photograph description did not match the actual image.
**Source of the concern.** Task §4 / §7
**Affected.** `albright.html, media-manifest.csv`
**Our reproduction / verification.** The long description asserts 'rows of chairs', 'small United States flags', 'pale stone wall and tall columns'. No image file exists in the package, so nobody writing it had seen the photograph.
**Root cause.** Description written from the catalogue title rather than from the image.
**Correction.** Replaced with a description derived strictly from NARA's own catalogue title and file-unit metadata, explicitly labelled as metadata-derived and NOT a visual description, with an instruction to replace it after viewing the file.
**Evidence of closure.** media-manifest.csv column long_description_status = 'METADATA-DERIVED, NOT VERIFIED AGAINST THE IMAGE'.
**Remaining limitation.** A true visual description requires the file (R-02).

### FA-01 &mdash; FIXED-VERIFIED

**Concern.** My own Einstein 'correction' was itself wrong. The exhibit claimed IHH's Ph.D. date of 1906 was contradicted, and that the correct date was 1905.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py, verify.html, FINDINGS.md`
**Our reproduction / verification.** University of Zurich states the doctorate and certificate 'were conferred in January 1906'; AIP's chronology gives approval 27 July 1905 and the degree 'formally awarded January 15, 1906'. IHH's 1906 matches the conferring institution. My correction was wrong.
**Root cause.** Three distinct events — dissertation completed 30 April 1905, faculty approval 27 July 1905, conferral 15 January 1906 — were flattened into one date, and nobelprize.org's own 1905 was treated as decisive.
**Correction.** Case rewritten. The verdict on the Ph.D. date is withdrawn. The claim now examined is the flattening itself, and the genuine error — '1911' for a diploma ETH dates to 28 July 1900 — is separated from it. nobelprize.org is presented as a source that disagrees with the awarding institutions, not as the authority.
**Evidence of closure.** ETH Zurich library (Abgangszeugnis 28.07.1900); UZH News 'Doctor Einstein'; AIP Center for History of Physics chronology. All opened.
**Remaining limitation.** The UZH Philosophy Faculty II promotion file was not inspected directly.

### FA-02 &mdash; OPEN

**Concern.** The 1998 State Department statement has never been opened by anyone on this project, yet it was quoted at length, dated, and used to source the arrival date and a first-person quotation.
**Source of the concern.** Task §5 + independent verification
**Affected.** `site/albright.html, site/cases.py`
**Our reproduction / verification.** 1997-2001.state.gov is refused by the egress proxy on every route including web archives. The document has NOT been read by anyone on this project. The filename is 981110 and the indexed page title reads '11/10/98', i.e. 10 November. AP (CBS News, 10 Nov 1998, 2:26pm EST) reports the ceremony happening 'Tuesday' — 10 November 1998 was a Tuesday.
**Root cause.** A citation was treated as a reading. Nobody opened the primary document.
**Correction.** All quotation of this document is now explicitly marked UNVERIFIED — NOT READ AT SOURCE, with the date conflict stated rather than resolved. The first-person quotation required by the page spec is NOT printed as archival; the shorter wording actually carried by AP is printed instead, attributed to AP as a secondary source, with the discrepancy shown.
**Evidence of closure.** ledger/source-conflicts.md records the 10-vs-11 November date conflict and the 86-vs-97 new-citizens conflict, both unresolved.
**Remaining limitation.** The assertions drawn from it have all been removed and the retractions are on the pages. What remains OPEN is the underlying gap: UNBLOCK by reading the statement from an unblocked network or requested from NARA's web-archive holdings. Until then the page spec's 'exact first-person quotation' requirement is NOT satisfied, and is documented as a deviation rather than quietly met.

### FA-03 &mdash; FIXED-VERIFIED

**Concern.** FINDINGS.md led with 'Two contradictory copyright regimes' as 'the most serious finding', and advised the team to open their pitch with it.
**Source of the concern.** Task §5 + independent verification
**Affected.** `FINDINGS.md, rights.html, method.html`
**Our reproduction / verification.** Re-read all four live intake forms. /tell-your-story/, /tell-your-story/first-gen-immigrants/ and /tell-your-story/genealogists/ now all carry 'I retain ownership of my copyright and grant the Project a non-exclusive, royalty-free license...'. The 'donate and convey ... all rights, title, and interest' wording is GONE — explicit string check returned not-present.
**Root cause.** The finding was true when recorded on 2 October 2026 and IHH has since corrected it. Republishing it would have been a false accusation.
**Correction.** Criticism WITHDRAWN. FINDINGS.md §2 rewritten to record that IHH fixed it, with the narrower residual point (the 2nd-gen form grants broad use rights while stating no copyright position) stated at its true weight.
**Evidence of closure.** Independent re-read of four live forms, with verbatim current wording.
**Remaining limitation.** Quotations are WebFetch-extraction-mediated; byte-level HTML was blocked.

### FA-04 &mdash; FIXED-VERIFIED

**Concern.** Celia Cruz: exhibit asserted 'more than 70 albums' against 'Produced 70 songs'.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Both IHH figures are repeated round numbers; neither is sourced.
**Correction.** Claim reframed around what IS sourceable: Smithsonian NMAH gives 'more than 80 albums and songs'; her estate gives 'over 80 albums and 1,000 songs'. The exhibit no longer endorses 70 as the correct figure.
**Evidence of closure.** Smithsonian NMAH 'Celia Cruz, Queen of Salsa'; celiacruz.com/biography. Both opened.

### FA-05 &mdash; FIXED-VERIFIED

**Concern.** Exhibit stated Cruz 'settled in the United States and was naturalised in 1961'.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** No source verifies a naturalisation year.
**Correction.** Naturalisation claim removed. Now: left Cuba 1960 on tour to Mexico, never returned; arrived in the United States 20 November 1961.
**Evidence of closure.** Smithsonian NMAH gives arrival 'Nov. 20, 1961'; LoC Music Division blog corroborates the 1960 departure. Both opened.

### FA-06 &mdash; FIXED-VERIFIED

**Concern.** Bob Hope: exhibit listed five Academy honours with years 1940/1944/1952/1959/1965.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** List came from a tertiary aggregator, not the Academy.
**Correction.** Reduced to the three the Academy's own site confirms (Honorary 1952; Jean Hersholt Humanitarian 1959; Honorary 1965, with its verbatim citation from the Academy's acceptance-speech database). The two pre-1951 special awards are named as reported but explicitly marked not confirmed at the Academy. Note added that IHH's own years (1941,1945,1953,1960,1966) are ceremony years, not award years.
**Evidence of closure.** oscars.org/governors/honorary; oscars.org/governors/hersholt; aaspeechesdb.oscars.org/link/038-28/. All opened.
**Remaining limitation.** awardsdatabase.oscars.org is client-side rendered and could not be queried.

### FA-07 &mdash; FIXED-VERIFIED

**Concern.** Exhibit asserted Hope was 'never nominated in a competitive category'.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** A negative claim rested on absence from a tertiary list.
**Correction.** Downgraded. The exhibit now says no competitive nomination appears in the Academy honours lists consulted, names them, and states that establishing the negative requires a null result in the Academy Awards Database recorded with a search date.
**Evidence of closure.** Reasoning recorded on the page itself.
**Remaining limitation.** The negative is not established; the page says so.

### ST-01 &mdash; FIXED-VERIFIED

**Concern.** sitemap.xml asserted https://immigranthallofhonor.org/ for pages that do not exist at that domain, and two entries were bare relative paths.
**Source of the concern.** Repair pass / task §8
**Affected.** `sitemap.xml`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Written for a deployment that does not exist, using the real museum's hostname.
**Correction.** Replaced with a deployment template on example.invalid listing all 10 indexable pages (404 excluded), with a comment explaining it must be edited or deleted before serving.
**Evidence of closure.** qa/integrity.mjs asserts no sitemap entry names the live museum's domain.

### ST-07 &mdash; FIXED-VERIFIED

**Concern.** FINDINGS.md told the team to open their pitch with the copyright finding.
**Source of the concern.** Repair pass / task §8
**Affected.** `FINDINGS.md`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Advice built on a finding that is now withdrawn.
**Correction.** Closing section rewritten: lead with the nomination form instead, and correct the slide if it has already been shown.
**Evidence of closure.** Read in the shipped file.

### AR-02 &mdash; FIXED-VERIFIED

**Concern.** The byline claimed 'every factual claim on this page carries a named source above'. Several did not: the 1939 flight, Josef Korbel's career, Denver, the 1957 citizenship year and the 1993 UN appointment.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A blanket sourcing claim written without auditing the body text against the source set.
**Correction.** Byline rewritten to state exactly what is sourced to the items, what rests on her own memoir and the standard public record, and the two things explicitly NOT established.
**Evidence of closure.** Read in the shipped copy.html and copy-full.md.

### BR-01 &mdash; FIXED-VERIFIED

**Concern.** site/albright.html carried a verbatim 'Transcription — opening paragraph' of the 1998 press statement, with a highlighted passage, for a document the rest of the package states nobody has opened.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The factual repair pass rewrote cases.py and built albright-wp/ but never touched the exhibit page, so the package contradicted itself in the most damaging possible place.
**Correction.** The panel now states that we have not read the document, names the hosts that refused us, and sets out the unresolved date conflict. No transcription remains.
**Evidence of closure.** grep across the package: zero occurrences of the transcribed sentence, including inside the exhibit-mode JavaScript, which is where a later review found the surviving copy.

### BR-02 &mdash; FIXED-VERIFIED

**Concern.** The same page printed the long 'warmest congratulations' quotation attributed to that unread statement, plus '86 new citizens', Judge Paul L. Friedman and the oath renewal — all sourced only to the document nobody opened.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Same cause as BR-01.
**Correction.** Replaced with the shorter AP-reported wording, attributed to AP and CBS News, with the withdrawal of the longer version stated on the page and the 86-versus-97 discrepancy named.
**Evidence of closure.** Read in the shipped file. source-conflicts.md §2 records the 86-versus-97 conflict and §3 the two quotation wordings; the page now agrees with both.

### BR-03 &mdash; FIXED-VERIFIED

**Concern.** The page carried an invented visual description of the anchor photograph — chairs, flags, stone columns — for an image file the package does not contain. Ledger R-03 claimed this had been fixed.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** R-03 was applied to the manifest and the WordPress profile but not to the exhibit page, and the ledger entry named albright.html anyway. The ledger was wrong.
**Correction.** Replaced with what the catalogue record actually states, plus an instruction to write the description after downloading the file.
**Evidence of closure.** grep: the invented description is gone; R-03's evidence field corrected.

### CR-01 &mdash; FIXED-VERIFIED

**Concern.** The exhibit-mode JavaScript carried its own copy of the verbatim transcription of the 1998 press statement, dated and sourced, and surfaced it to visitors. BR-01 claimed the transcription had been removed.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** BR-01 edited the static markup. The panel data for exhibit mode is assembled in a script block further down the file and was never searched. The fix was reported as complete after checking only the part that had been edited.
**Correction.** The panel now states that we have not read the document and why, and names the unresolved date. Verified by grepping the whole file, not the edited region.
**Evidence of closure.** grep across the package: zero occurrences of the transcribed sentence.

### CR-02 &mdash; FIXED-VERIFIED

**Concern.** A second verbatim quotation of the same unread statement survived in the body text: the Korbels were 'forced from their homeland'.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Same cause as CR-01 — one occurrence found and fixed, the file not swept.
**Correction.** The sentence is rewritten in our own words, with the withdrawal stated inline.
**Evidence of closure.** grep: zero occurrences.

### CR-03 &mdash; FIXED-VERIFIED

**Concern.** The standfirst still said 'alongside eighty-six people taking it for the first time' — the retracted, sourceless figure, spelled out — on a page that says twenty lines later that neither number appears on it.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The numeral '86' was searched for; the figure was written in words.
**Correction.** Removed, with the 97-versus-86 discrepancy stated where the number used to be.
**Evidence of closure.** grep for both the numeral and the spelled form: zero.

### CR-04 &mdash; FIXED-VERIFIED

**Concern.** The Denver section asserted 'The family landed in New York on 11 November 1948' citing the unread statement — the exact claim the Verification Desk stamps NOT SUPPORTED, for that exact reason.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The exhibit page and the Verification Desk were written at different times and never cross-checked against each other.
**Correction.** The page now gives the month, says the day rests on a document we have not read, and points at its own Not-supported verdict.
**Evidence of closure.** The two pages now agree; checked by reading both.

### DR-01 &mdash; FIXED-VERIFIED

**Concern.** Two places still asserted 11 November 1948 as the arrival date — the timeline entry and the journey-map panel data in JavaScript — on the authority of the State Department statement nobody has read. The same page says three times that the day is not supported.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** CR-04 fixed the Denver body text. The timeline and the journey-map script data were not searched, for the third round running: a sweep of the prose, not of the file.
**Correction.** Both now give the month alone. The journey-map panel adds the sentence that the day is usually given as 11 November on the authority of a document we have not read, and points at the panel that explains why.
**Evidence of closure.** Package-wide grep for '11 November': every surviving occurrence sits inside a retraction, an unresolved-date note, or a pointer to ledger/source-conflicts.md. Verified in the shipped file, not the patch log.

### DR-02 &mdash; FIXED-VERIFIED

**Concern.** The standfirst said she took the oath 'fifty years to the day after that second arrival' — a claim that silently asserts both dates, the 1948 arrival day and the 1998 ceremony day, when the package states that neither is settled.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** A rhetorical phrase written before either date was known to be in conflict, and not recognised as a factual assertion because it contains no numerals.
**Correction.** Rewritten as 'Fifty years after that second arrival, almost to the day'.
**Evidence of closure.** Read in the shipped file. source-conflicts.md §1 and §2 now agree with the page.

### DR-03 &mdash; FIXED-VERIFIED

**Concern.** The source list gave the Library of Congress papers as 'acquired 2015', contradicting the finding aid that this project actually opened, which records the gift years as 2014 and 2016.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** cases.py was corrected when the finding aid was read; the exhibit page's source list was not updated from it.
**Correction.** The entry now names finding aid ms018034, gives 2014 and 2016 as the gift years of record, says 2015 is the announcement year, and states the collection is not digitised at item level.
**Evidence of closure.** Matches the quotation in site/cases.py claim a2, which quotes the finding aid verbatim. Package-wide grep: 'acquired 2015' survives only where cases.py analyses where that figure came from.

### DR-04 &mdash; FIXED-VERIFIED

**Concern.** A citation note read 'neither number appears on this page' twenty lines after the page printed 97. The retraction was true of 86 and false of 97, so the page contained a verifiably false statement about itself.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/albright.html, ledger/source-conflicts.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** CR-03 removed the 86 figure and wrote the retraction in a form that over-claimed, then source-conflicts.md was written to match the over-claim rather than the page.
**Correction.** The note now says the 86 figure is withdrawn and that where a figure appears it is the wire report's, attributed to it. source-conflicts.md §2 restated to match.
**Evidence of closure.** Both read in the shipped files and checked against each other.

### ER-01 &mdash; FIXED-VERIFIED

**Concern.** Three places summarised the Albright profile's provenance as '13 sources, 7 catalogued images' (FINDINGS), 'Thirteen sources. Seven images' (the exhibit-mode panel) and 'eleven sources, seven catalogued images' (the homepage) — three different figures for one manifest, none of them matching it. The manifest holds fourteen items: six photographs and eight text sources.
**Source of the concern.** Verification sweep, round 5
**Affected.** `site/albright.html, site/index.html, site/FINDINGS.md`
**Our reproduction / verification.** Found by recounting every stated figure against the file it describes, after the round-4 fixes had passed the full harness suite.
**Root cause.** Summary prose written against the manifest as it stood at three different moments, and never derived from it. method.html and INSTALL.md were corrected in round 3; these three were not in that sweep.
**Correction.** All three now state fourteen source items, six archival photographs and eight text sources, matching the manifest row for row.
**Evidence of closure.** Counted from albright-wp/media-manifest.csv with a CSV reader: 14 rows, kind=photograph on 6. qa/integrity.mjs independently parses the same column.

### ER-02 &mdash; FIXED-VERIFIED

**Concern.** The same three summaries claimed 'two documents that do not exist in the public record'. The excluded-sources section on the same page says the correct thing — that neither the 1948 arrival manifest nor the 1957 naturalisation record is described at item level in the National Archives Catalog. Absence from a catalogue's item-level description is not non-existence, and task §5 forbids exactly this substitution.
**Source of the concern.** Verification sweep, round 5
**Affected.** `site/albright.html, site/index.html, site/FINDINGS.md`
**Our reproduction / verification.** Found by recounting every stated figure against the file it describes, after the round-4 fixes had passed the full harness suite.
**Root cause.** A summary compressed a careful statement about catalogue coverage into a claim about the historical record.
**Correction.** All three now say the National Archives Catalog does not describe the two records at item level, and name them.
**Evidence of closure.** The summaries now match the excluded-sources section verbatim in substance. Package-wide grep for 'do not exist in the public': zero occurrences.

### FR-01 &mdash; FIXED-VERIFIED

**Concern.** The contrast claim was not reproducible from the package. qa/pixels.mjs only captured screenshots and exited 0; the script that computed the WCAG ratios (px.py) lived in a scratch directory and was never shipped. The documentation nevertheless cited '150 runs, zero failures, 5.11:1' as evidence.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `qa/pixels.mjs, site/TESTS-RUN.md, site/FINDINGS.md`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** The sampler was split into a shipped capturer and an unshipped analyser during development, and the analyser was never folded back in. The prose was written from the analyser's output, which the package could not reproduce.
**Correction.** The WCAG maths are now inside qa/pixels.mjs (ported into the browser-side pass over the composited screenshot pixels). It samples all eleven pages in both schemes, ASSERTS zero failures, and exits nonzero otherwise. The prose now says 'run it yourself' and quotes the harness's own output. On its first full-coverage run it caught a genuine 2.51:1 failure on a filename chip, which was fixed — proof the test can fail.
**Evidence of closure.** node qa/pixels.mjs: 339 runs, 0 failures, tightest 5.11:1, exit 0; forcing a low-contrast element makes it exit 1.

### FR-04 &mdash; FIXED-VERIFIED

**Concern.** media-manifest.csv alt_text for the three RG 59 items asserted Madeleine Albright as the subject ('Secretary of State Madeleine Albright…') while the same rows are flagged SUBJECT UNCONFIRMED / USE ONLY AFTER VIEWING.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/media-manifest.csv`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** The alt text predated the discovery that the series subject is unconfirmed, and asserted what the catalogue does not.
**Correction.** Rewritten to describe only what the catalogue states — a photograph from a State Department series relating to her, subject not confirmed — within the 15-word / 125-char limit.
**Evidence of closure.** Each new alt text: <=100 chars, <=14 words, asserts no unverified subject; qa/integrity.mjs re-parses the column and passes.

### FR-12 &mdash; FIXED-VERIFIED

**Concern.** The single first-person quotation needed to be the Associated Press wording, not the unread State Department statement's. It was attributed to AP but had not been checked against a reachable copy, and it carried a comma the source does not.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `site/albright.html, albright-wp/copy.md`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** The quotation had been re-attributed to AP when the longer State-Department version was withdrawn, but the AP text itself had not been read.
**Correction.** Verified against the CBS News copy of the AP report (a reachable host, unlike the blocked state.gov archive): the sentence is present essentially verbatim, the date is 10 November 1998, the figures are 97 citizens / 31 countries, and 'warmest congratulations' does NOT appear — confirming the withdrawn longer version was not AP's. The inserted comma after 'America' was removed to match the source.
**Evidence of closure.** WebFetch of cbsnews.com/news/albright-renews-her-oath/ returned the sentence and all four cross-checks; quotation now matches.


## P1 &mdash; Missing content or assets (7)

### R-02 &mdash; BLOCKED-EXTERNAL

**Concern.** The ZIP contained no archival image files.
**Source of the concern.** Task §4 / §7
**Affected.** `(whole package)`
**Our reproduction / verification.** `find site -iregex '.*\.(jpg|png|...)$'` on a fresh extraction of ihh-site-v4.zip returns 0 files.
**Root cause.** catalog.archives.gov and diplomacy.state.gov are refused by this environment's egress proxy: HTTP 403 to CONNECT, logged in the proxy's recentRelayFailures. Not a code defect.
**Correction.** Could not be fixed from this environment. Every required file is specified at item level in media-manifest.csv with its stable URL and direct download URL, and INSTALL.md gives a volunteer the exact steps. The page renders a labelled 'not yet obtained' placeholder rather than a broken image.
**Evidence of closure.** ledger/fetch-attempts.txt (5 URLs, all 000) and ledger/proxy-denial.txt (CONNECT denials logged for catalog.archives.gov, diplomacy.state.gov, 1997-2001.state.gov and web.archive.org).
**Remaining limitation.** UNBLOCK: run `albright-wp/media/fetch-media.sh` from any network that can reach catalog.archives.gov and diplomacy.state.gov, then `python3 albright-wp/verify-media.py` to confirm what arrived. Six files, roughly ten minutes.

### ST-08 &mdash; FIXED-VERIFIED

**Concern.** No clear separation between the required WordPress deliverable and the optional standalone site.
**Source of the concern.** Repair pass / task §8
**Affected.** `(package layout)`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Both were in one directory with one README.
**Correction.** Package restructured: albright-wp/ is the required deliverable with its own INSTALL.md; site/ is labelled optional throughout; the root README states which is which in its first two lines.
**Evidence of closure.** Verified against the final ZIP in the acceptance pass.

### AR-01 &mdash; FIXED-VERIFIED

**Concern.** copy.html emitted six live <img src="media/*.jpg"> for files the package does not contain, so six broken images render the moment the block is pasted.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/copy.html, build.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Only the anchor image had a placeholder path; the source-set thumbnails did not.
**Correction.** Absent images now render a labelled dashed slot naming the file to save, with the real <img> tag left commented out beside it.
**Evidence of closure.** qa/integrity.mjs asserts no <img> in the fragment points at a file missing from media/.

### AR-03 &mdash; FIXED-VERIFIED

**Concern.** INSTALL.md routed WordPress.com users to copy.md, which contains none of the source set, rights statements, required credits, deviation panel or byline. That route would publish an uncredited page.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/INSTALL.md, copy.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** copy.md was authored as editorial text only but documented as a publishing fallback.
**Correction.** build.py now emits copy-full.md carrying the complete page in Markdown. INSTALL.md points there and says why copy.md is not the right file.
**Evidence of closure.** copy-full.md is 16 KB and contains all 14 source items, every rights line and the byline.

### AR-11 &mdash; FIXED-VERIFIED

**Concern.** Three source items carried identical glosses and identical alt text.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/media-manifest.csv`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Filler written to reach the 10-15 item count.
**Correction.** Each of the three RG 59 items now has its own gloss and alt text, and each still says the subject is unconfirmed.
**Evidence of closure.** Read in the manifest; alt-text limits still pass.

### BR-06 &mdash; FIXED-VERIFIED

**Concern.** Two manifests existed and disagreed: site/media-manifest.csv named different subjects for the same NARA identifiers, a different commission date, and still claimed the rights wording had been read at each record.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/media-manifest.csv`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A stale copy left in place when the authoritative manifest was rewritten.
**Correction.** Deleted. site/media-manifest.README.txt explains why and points to the one manifest.
**Evidence of closure.** One manifest in the package.

### FR-05 &mdash; FIXED-VERIFIED

**Concern.** In the WordPress deliverable the anchor image's 'uncomment this' comment wrapped an explanatory sentence together with the <img>, so a volunteer following INSTALL literally ('remove the <!-- and -->') would publish the sentence 'When the file is present… use this:' as visible text.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** The anchor used a multi-line comment holding both prose and the tag; the thumbnails already used a clean single-line img comment.
**Correction.** The anchor now matches the thumbnails: a separate instruction comment, then the <img> on its own single-line comment, so uncommenting yields a clean tag.
**Evidence of closure.** copy.html regenerated; the anchor comment contains only the <img>.


## P2 &mdash; Source traceability (37)

### FA-08 &mdash; FIXED-VERIFIED

**Concern.** Hope naturalisation given as a bare year.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Mechanism omitted.
**Correction.** Now: became a US citizen in December 1920 derivatively, when his father was naturalised — which is why 1920 appears on the IHH page as an immigration year.
**Evidence of closure.** Encyclopedia of Cleveland History, Case Western Reserve University. Opened.

### FA-09 &mdash; FIXED-VERIFIED

**Concern.** John Muir's death date printed as 24 December 1914 as a verified correction.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Widely repeated; no institutional source located.
**Correction.** The argument no longer depends on the exact day. It rests on the year of death (1914, given by both NPS and the Sierra Club) against the park's establishment on 26 February 1919 — a five-year gap either way.
**Evidence of closure.** NPS 'Who Was John Muir?'; Sierra Club John Muir Exhibit (1838-1914). Both opened.
**Remaining limitation.** Day-level death date deliberately not asserted.

### FA-10 &mdash; FIXED-VERIFIED

**Concern.** Grand Canyon monument/park dates given as bare years.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Imprecise.
**Correction.** Now: National Monument 11 January 1908 by Proclamation No. 794; National Park 26 February 1919 by act of Congress (40 Stat. 1175).
**Evidence of closure.** NPS, Ronald F. Lee, 'The Proclamation of National Monuments Under the Antiquities Act' Table II; NPS Grand Canyon Park Profile 2025 PDF. Both opened.

### FA-11 &mdash; FIXED-VERIFIED

**Concern.** Yosemite establishment given as 1890.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Imprecise.
**Correction.** Now 1 October 1890, cited to the NPS Geodiversity Atlas.
**Evidence of closure.** nps.gov/articles/nps-geodiversity-atlas-yosemite-national-park.htm. Opened.

### FA-12 &mdash; FIXED-VERIFIED

**Concern.** Albright papers described as going to the Library of Congress in 2015.
**Source of the concern.** Task §5 + independent verification
**Affected.** `albright-wp/copy.md, site/albright.html`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** 2015 is the announcement year.
**Correction.** Corrected to the finding aid's own words: 'given to the Library of Congress by Albright in 2014 and 2016'. Collection title corrected to 'Madeleine Korbel Albright Papers', ID ms018034. Not digitised at item level; access onsite only.
**Evidence of closure.** LoC finding aid PDF ms018034 via tile.loc.gov. Opened and quoted verbatim.

### FA-13 &mdash; FIXED-VERIFIED

**Concern.** 'More than twenty relatives died in the Holocaust' attributed generally.
**Source of the concern.** Task §5 + independent verification
**Affected.** `albright profile`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Attribution imprecise; figures differ between sources.
**Correction.** Now attributed to Albright's own words as quoted in a review of Prague Winter. The Washington Post's separate finding — her three surviving grandparents died in the camps — is attributed to the Post. A 1997 JTA wire report giving 'more than a dozen' is named as a divergence rather than harmonised away.
**Evidence of closure.** j. the Jewish News of Northern California, 31 Aug 2012; Washington Post, 23 Mar 2022; JTA archive, 15 Jul 1997. All opened.

### FA-14 &mdash; FIXED-VERIFIED

**Concern.** The 'perhaps Trawniki' hedge risked being hardened.
**Source of the concern.** Task §5 + independent verification
**Affected.** `albright profile`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** —
**Correction.** Hedge reproduced verbatim and the reason for it stated: the Post records that several different Anna Spieglovas died in the camps. A JTA report saying the grandmother's fate is simply unknown is shown alongside it.
**Evidence of closure.** j. review (verbatim 'perhaps Trawniki'); Washington Post 2022. Opened.
**Remaining limitation.** Deliberately unresolved.

### FA-15 &mdash; FIXED-VERIFIED

**Concern.** Albright's birth name rendered as 'Marie Jana Korbelová' as fact.
**Source of the concern.** Task §5 + independent verification
**Affected.** `albright profile`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Czech form not verified at any Czech institutional source.
**Correction.** The US State Department Office of the Historian rendering 'Marie Jean' is printed and cited; the Czech form is shown as the commonly used variant, explicitly marked unverified.
**Evidence of closure.** history.state.gov departmenthistory people entry. Opened.
**Remaining limitation.** Czech-source verification outstanding.

### FA-16 &mdash; FIXED-VERIFIED

**Concern.** 'Standard reference biographies, in agreement' used as a citation 6 times.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Not a source.
**Correction.** Every instance replaced with a named source carrying a stable URL and a locator, or the claim was removed.
**Evidence of closure.** grep for the phrase returns 0 in the shipped package.

### FA-17 &mdash; FIXED-VERIFIED

**Concern.** Exhibit asserted how IHH's authors made their errors ('somebody searched a congressional database and mistook the proposal').
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Invented causal explanation about identifiable people.
**Correction.** All speculation about how an error arose removed. The exhibit states what the record shows and stops.
**Evidence of closure.** grep: no remaining 'somebody' / 'copied without reading' claims.

### FA-18 &mdash; FIXED-VERIFIED

**Concern.** H.R. 149 described only as 'referred to subcommittee 23 Feb 2005'.
**Source of the concern.** Task §5 + independent verification
**Affected.** `cases.py`
**Our reproduction / verification.** Verified against the named sources; each marked opened or snippet-only in the verification record.
**Root cause.** Incomplete legislative history.
**Correction.** Now: introduced 4 January 2005 by Rep. Menendez as the Congressional Tribute to Celia Cruz Act; referred to Financial Services the same day; referred to the Subcommittee on Domestic and International Monetary Policy, Trade and Technology on 23 February 2005; no further action. Cruz appears nowhere in the CRS list of Congressional Gold Medal recipients.
**Evidence of closure.** govinfo.gov BILLS-109hr149ih and BILLSTATUS-109hr149.xml; CRS RL30076. All opened.
**Remaining limitation.** CRS edition consulted runs to 2016; as-of date stated on the page.

### ST-13 &mdash; NOT-APPLICABLE-JUSTIFIED

**Concern.** The page spec requires a scan beside a transcription. No scan exists.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** No scan of the 1998 statement is published anywhere located, and the statement itself could not be opened.
**Correction.** An explicitly labelled 'Documented deviation' panel states that this is not a scan, that nothing is transcribed from the document, and that the date is unresolved. The genuine-scan requirement is NOT marked satisfied.
**Evidence of closure.** Visible on the page; recorded here as a deviation, not a closure.
**Remaining limitation.** The scan requirement remains unsatisfied and is declared as such.

### AR-04 &mdash; FIXED-VERIFIED

**Concern.** The only first-person quotation's attribution rendered as 'as reported by one, as reported by the Associated Press'.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The template already said 'as reported by' and the captured group carried the 'one, as reported by' counter from copy.md's slot label.
**Correction.** The counter is stripped before interpolation.
**Evidence of closure.** Rendered cite reads 'as reported by the Associated Press, 10 November 1998'.

### AR-05 &mdash; FIXED-VERIFIED

**Concern.** META-01 stated a hardcoded finding total that no longer matched the ledger it described - in the one finding whose subject is not overclaiming.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Stale number in the one finding about not overclaiming.
**Correction.** The total is no longer written by hand: findings.py carries a 116 token and emit.py substitutes len(F) at generation time, so it cannot go stale again.
**Evidence of closure.** grep the generated ledger for the total; it equals the JSON count field.

### AR-06 &mdash; FIXED-VERIFIED

**Concern.** Three ledger entries cited evidence files that did not exist (qa/privacy.mjs, ledger/source-conflicts.md) or wrong paths (evidence/ for ledger/).
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Evidence named aspirationally while writing the fix, never checked against the tree.
**Correction.** Paths corrected; source-conflicts.md written for real and now records seven unresolved conflicts including two corrections to our own earlier work.
**Evidence of closure.** Every evidence path in the ledger resolves to a file in the package.

### AR-08 &mdash; FIXED-VERIFIED

**Concern.** Two ledger fixes were claimed but absent from the deliverable: the Czech-form 'explicitly marked unverified', and the JTA 'more than a dozen' divergence.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/copy.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The ledger recorded the intent; the text was never edited.
**Correction.** Both now in the body copy.
**Evidence of closure.** grep for 'did not verify it at any Czech institutional source' and 'more than a dozen' in copy.md.

### AR-09 &mdash; FIXED-VERIFIED

**Concern.** The Denver section near-quoted Albright's words without attribution.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/copy.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Paraphrase drifted toward quotation.
**Correction.** Rewritten as explicit paraphrase, pointing at the source item, and saying why it is not quoted: the full text is in the document we could not open.
**Evidence of closure.** Read in copy.md.

### AR-10 &mdash; FIXED-VERIFIED

**Concern.** The manifest labelled rights wording as read 'at the item record' on 2026-10-02 for six records the package's own evidence shows were never reachable.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/media-manifest.csv`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Rights wording came from earlier research notes, not from this pass.
**Correction.** rights_statement_source for every undownloaded item now reads 'TRANSCRIBED FROM RESEARCH NOTES... NOT re-read at the record during this pass'. The figcaption says the same.
**Evidence of closure.** grep: 6 rows carry the transcription warning.

### BR-04 &mdash; FIXED-VERIFIED

**Concern.** The sources block asserted 'Every item below was read at the holding institution's own record.'
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Untrue for every blocked host.
**Correction.** Rewritten to say which items were opened and which are transcribed from research notes pending re-reading.
**Evidence of closure.** Read in the shipped file.

### BR-08 &mdash; FIXED-VERIFIED

**Concern.** The byline cited Prague Winter as 'item 12', which is the book review; the book is item 14.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The lookup matched the first row whose title contained 'Prague Winter'.
**Correction.** The lookup now also requires kind == 'book'.
**Evidence of closure.** Rendered byline reads 'item 14 above'.

### BR-10 &mdash; FIXED-VERIFIED

**Concern.** Her name appeared three different ways across the package, with the Czech form asserted as fact in albright.html while cases.py marked it unverified.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html, cases.py, albright-wp/copy.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Three files edited at different times.
**Correction.** The State Department rendering is used; the Czech form is labelled unverified wherever it appears, including the JSON-LD alternateName.
**Evidence of closure.** grep across the package.

### BR-11 &mdash; FIXED-VERIFIED

**Concern.** Three reasoning defects in cases.py: the ceremony-year explanation did not account for 1941; a claim cited two institutions but linked one; and the Cruz verdict covered '23 gold records', which its own evidence corroborates.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/cases.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Arguments written faster than they were checked.
**Correction.** The ceremony-year item now states where its own explanation fails; the Muir item cites only what it opened and gives the interval accurately as more than four years; the Cruz claim excludes the corroborated element.
**Evidence of closure.** Read in cases.py and the regenerated verify.html.

### BR-12 &mdash; FIXED-VERIFIED

**Concern.** Three evidence items were tagged RECORD — defined in the file as 'an institution's own record of its own act' — when they are secondary or interpretive.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/cases.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Tag applied by source prestige rather than by the definition.
**Correction.** Retagged PARAPHRASE: the AIP chronology, the estate biography and the IAS essay.
**Evidence of closure.** Tag counts in the regenerated page.

### CR-05 &mdash; FIXED-VERIFIED

**Concern.** Three ledger entries cited evidence that did not exist or did not say what was claimed: an assertion in qa/integrity.mjs, and agreement with two sections of source-conflicts.md.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Evidence written from intention rather than from the file.
**Correction.** All three rewritten to describe checks that exist and match.
**Evidence of closure.** Each evidence string re-read against the file it names.

### CR-06 &mdash; FIXED-VERIFIED

**Concern.** Her name appeared as 'Marie Jana Korbelová' asserted as fact in two more places in albright.html, contradicting cases.py and copy.html which mark it unverified. BR-10 claimed this was fixed everywhere.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** BR-10 fixed the JSON-LD and one body mention; the timeline entry and a second body mention were missed.
**Correction.** Both now use the State Department rendering, with the Czech form labelled unverified.
**Evidence of closure.** grep: zero unqualified occurrences.

### CR-07 &mdash; FIXED-VERIFIED

**Concern.** The page resolved the 10-versus-11 November date three times — in the document header, the panel note and the timeline — while stating twice that it is unresolved.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Boilerplate written before the conflict was discovered.
**Correction.** All three now say '10 or 11 November 1998 (unresolved)' or give the month alone.
**Evidence of closure.** grep: the only two remaining mentions both carry the word 'unresolved' or a pointer to source-conflicts.md.

### CR-08 &mdash; FIXED-VERIFIED

**Concern.** Alt text across the package described a lectern, seated citizens and the Archives rotunda — a visual description of a photograph the package states nobody has seen, and none of it in the quoted catalogue metadata.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `albright-wp/media-manifest.csv, copy.html, copy-full.md, site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The alt text predates the discovery that no image file exists, and survived R-03 because that finding only addressed the long description.
**Correction.** Replaced with wording that uses only what the catalogue record states.
**Evidence of closure.** The new alt text is 12 words, 89 characters, and asserts nothing visual beyond the event.

### CR-12 &mdash; FIXED-VERIFIED

**Concern.** verify.html asserted fourteen live-site claims as 'Read 2 October 2026' with no statement of method, while FINDINGS conceded that byte-level HTML was unavailable.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/gen.py, site/verify.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Method caveat recorded in one document and not the other.
**Correction.** The Verification Desk now states the reading method, the re-check date, and that one of our own claims about the live site has already been withdrawn on re-reading.
**Evidence of closure.** Read on the regenerated page.

### DR-06 &mdash; FIXED-VERIFIED

**Concern.** cases.py confessed in the present perfect — 'We have quoted this document at length without reading it' — after every such quotation had been withdrawn, so the page described a state that was no longer true.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/cases.py, site/verify.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** The confession was written while the quotations were still on the page and not revised when they were removed.
**Correction.** Rewritten as an earlier version of the exhibit having done so, with the withdrawal stated.
**Evidence of closure.** Read on the regenerated verify.html.

### DR-08 &mdash; FIXED-VERIFIED

**Concern.** privacy.html described how stories sent through the collection form would be handled, in the present tense, on a site whose form had been removed.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/privacy.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** The privacy page was not revisited when the form was removed under R-01.
**Correction.** The section is now conditional throughout: what would be kept if the form were live.
**Evidence of closure.** Read in the shipped file; integrity.mjs separately confirms the story page collects nothing.

### DR-09 &mdash; FIXED-VERIFIED

**Concern.** FA-02 was recorded as OPEN with a concern describing assertions that had all been removed, so the entry read as though the exhibit still made them.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** The entry was written at the start of the repair and not reworded when the assertions came out.
**Correction.** The concern now describes the underlying gap — the statement has never been opened by anyone on this project — and the limitation records that the assertions are gone while the gap remains.
**Evidence of closure.** The entry's own status is still OPEN, which is the honest state.

### PROC-02 &mdash; NOT-APPLICABLE-JUSTIFIED

**Concern.** Four consecutive review rounds found P0 findings in site/albright.html. Counted from this ledger's own records: 3 in round 2, 4 in round 3, 4 in round 4, 2 in the round-5 sweep. The exhibit page duplicates facts that live in copy.md, media-manifest.csv, cases.py and source-conflicts.md, but unlike copy.html and verify.html it is not generated from them, so every factual correction has to be applied to it by hand, and in each of those rounds at least one was missed.
**Source of the concern.** Observed across five verification rounds
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reproducible from this ledger: filter the JSON for sev=P0 and files containing site/albright.html, then group by source. That is where the 3/4/4/2 figures above come from; no other page appears more than once across the four rounds.
**Root cause.** A hand-maintained page carrying generated pages' facts. The optional site was built before the single-source-of-truth discipline was adopted for the required deliverable.
**Correction.** Not refactored. The required WordPress deliverable — the only part a volunteer integrates — IS generated from copy.md and the manifest by albright-wp/build.py, and qa/rebuild.sh proves it regenerates byte-identically. The optional site's exhibit page was instead swept exhaustively: every factual figure in it was recounted against its source file in round 5, and the sweep is recorded above.
**Evidence of closure.** qa/rebuild.sh regenerates all four generated artefacts byte-identically. qa/integrity.mjs re-derives the manifest counts, the package weight and the alt-text limits from the shipped files rather than from prose.
**Remaining limitation.** site/albright.html remains hand-maintained. A sixth review would most likely find its next defect there, and anyone extending the optional site should generate that page from the same sources the WordPress deliverable uses. This is the single most likely location of a defect still in this package.

### FR-02 &mdash; FIXED-VERIFIED

**Concern.** The closure ledger was internally inconsistent: missing-attachment.txt read '39 recorded (18 + 15 + 12 + 9 + 3)' when that sum is 57; CLOSURE-LEDGER.md was dated 9 October while CLOSURE-LEDGER.json said 2026-10-03; and DR-07 quoted integrity.mjs as '267 KB' when it prints a different figure.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `ledger/missing-attachment.txt, ledger/emit.py, ledger/findings.py`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** Hand-written totals and a hardcoded JSON date that drifted from the prose; a quoted figure that went stale when the package weight changed.
**Correction.** Arithmetic corrected to 57; emit.py now computes one date and writes it to both the JSON and the Markdown; DR-07 no longer quotes a number, it describes the check that recomputes it.
**Evidence of closure.** emit.py output: md and json now carry the same generated date; no literal weight in the ledger.

### FR-06 &mdash; FIXED-VERIFIED

**Concern.** The commented-out <img> tags carried invented pixel dimensions (width=2048 height=1365 on the anchor, 320x213 on the thumbnails) for files nobody has downloaded or measured.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** Placeholder dimensions written to look complete; the manifest holds no dimension data.
**Correction.** Removed from every image template; CSS handles the aspect ratio, and the volunteer sets real dimensions after viewing the files.
**Evidence of closure.** grep: no width=/height= on any media img in copy.html.

### FR-08 &mdash; FIXED-VERIFIED

**Concern.** copy.html and copy-full.md claimed 'the status of each is stated' for the fourteen source items, but only the one unread document carried a visible status note.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** A summary written more strongly than the per-item rendering supported.
**Correction.** Reworded to what the page actually shows: each item listed with source, date and rights wording; images not yet supplied say so in place; the unread document says so too.
**Evidence of closure.** Read in the regenerated copy.html and copy-full.md.

### PROC-03 &mdash; FIXED-VERIFIED

**Concern.** Of roughly 45 BLOCKER/MAJOR findings relayed by three independent reviewers, the majority did not reproduce in the authoritative tree: they were read from a stale extracted copy of an earlier package, or cited line numbers that no longer matched. Acting on them blindly would have 'fixed' defects that were already fixed and could have reintroduced errors.
**Source of the concern.** Observed during the final repair round
**Affected.** `(review process)`
**Our reproduction / verification.** Examples: a simulated 1998 letterhead, a '30 September' date, '19 claims / 30 evidence', and a still-asserted Einstein correction were all reported as present but were already corrected in site/albright.html and site/FINDINGS.md.
**Root cause.** Reviewers were given both an authoritative path and a stale extracted copy; some read the extract.
**Correction.** Every reviewer finding was re-verified against the authoritative tree with grep or a script before any change, and only reproducing defects were touched. The one finding that needed external truth (the AP quotation) was verified against a reachable source rather than assumed. The shipped harnesses were made self-asserting so the evidence is reproducible rather than narrated.
**Evidence of closure.** This round's FR-series lists only the reproduced defects; the non-reproducing reviewer claims were checked and left unchanged because the tree was already correct.
**Remaining limitation.** A reviewer reading a stale artefact is a process hazard, not a defect in the deliverable; the lesson is to point every review at one authoritative tree.

### PROC-01 &mdash; FIXED-VERIFIED

**Concern.** Two fixes were reported as applied when they had not been. A patch script performed several edits and wrote the file once at the end; an assertion failed partway through, the process exited, and every earlier edit in that run was discarded. The log line confirming the first edit had already printed.
**Source of the concern.** Observed during this repair pass
**Affected.** `(repair tooling)`
**Our reproduction / verification.** Happened twice: once on qa/integrity.mjs, once on the exhibit-mode panel in site/albright.html. The second time it was caught only because an independent reviewer re-read the file.
**Root cause.** Buffered writes plus a fail-fast assertion, with success reported from the log rather than from the file.
**Correction.** Later patch scripts write immediately after each step, and every fix in this round was verified by re-reading the shipped file rather than by trusting the script's output.
**Evidence of closure.** The final verification sweep greps the packaged files, not the working copy.
**Remaining limitation.** This is the failure mode most likely to have produced any defect still in the package: a change believed made, reported made, and not present.


## P3 &mdash; Accessibility (13)

### EV-01 &mdash; FIXED-VERIFIED

**Concern.** Albright standfirst had opacity:0 until JS added a class; invisible with no script
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** `.fade-up{opacity:0}` ungated on script presence
**Correction.** Moved the hidden state behind `html.js`, set by a synchronous head shim
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-02 &mdash; FIXED-VERIFIED

**Concern.** With no JS at phone width the nav was display:none and only a JS handler could open it
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `assets/site.css`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Collapse was unconditional below 52rem
**Correction.** Collapse and menu button both gated on `.js`
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-03 &mdash; FIXED-VERIFIED

**Concern.** Dark mode: pressed toggle white-on-accent at 2.33:1
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Hardcoded #fff against a themed background
**Correction.** Replaced with var(--on-accent); found and fixed a second instance (.zoom-hint)
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-04 &mdash; FIXED-VERIFIED

**Concern.** Space on the modal Close button advanced the slideshow instead of closing
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Key handler claimed Space regardless of focus target
**Correction.** Space ignored when focus is on a BUTTON/A/INPUT
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-05 &mdash; FIXED-VERIFIED

**Concern.** Shift+Tab from the modal's opening focus left the modal
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Trap only wrapped from first/last button; focus starts on the panel
**Correction.** Trap now handles focus outside the button list
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### ST-02 &mdash; FIXED-VERIFIED

**Concern.** Nine inductee cards were anchors with href="#" and aria-disabled="true".
**Source of the concern.** Repair pass / task §8
**Affected.** `inductees.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** aria-disabled does not prevent activation, and href="#" jumps to the top of the page. A keyboard user could tab to nine controls that do nothing.
**Correction.** Converted to non-interactive <div> blocks. Zero href="#" remain in the package.
**Evidence of closure.** grep: 0 occurrences of href="#"; qa/integrity.mjs asserts it.

### ST-09 &mdash; FIXED-VERIFIED

**Concern.** The WordPress fragment inherited the host theme's heading font, uppercase transform and centring.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** A WordPress theme styles h1-h6 by element name, which out-specifies a font-family set on the wrapper class. Found by previewing the fragment inside a deliberately hostile theme.
**Correction.** font-family, text-transform, letter-spacing and text-align re-asserted on every element the fragment uses.
**Evidence of closure.** qa/wp.mjs asserts the theme's Impact face and uppercase do not reach inside.

### ST-10 &mdash; FIXED-VERIFIED

**Concern.** The fragment's pull quote took the host theme's #999 colour (2.73:1), and the byline placeholder hardcoded a dark foreground that failed at 1.65:1 in dark mode.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Colour not set on blockquote; .fillme hardcoded #1a1714 against a themed background that flips.
**Correction.** Both now use theme tokens.
**Evidence of closure.** qa/wp.mjs runs axe in both colour schemes: 0 violations.

### ST-12 &mdash; NOT-APPLICABLE-JUSTIFIED

**Concern.** The fragment's h1 would duplicate the WordPress page title.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Most themes print the page title as an h1.
**Correction.** Documented, not silently changed: a comment at the h1 and step 3 of INSTALL.md tell the volunteer when to delete the line.
**Evidence of closure.** Cannot be auto-tested without the target theme; recorded as a human check.
**Remaining limitation.** Needs the target theme to verify.

### AR-12 &mdash; FIXED-VERIFIED

**Concern.** qa/wp.mjs's overlay check carried a dangling ternary that excluded every statically positioned element, so 'no text overlaid on the photograph' could never fail.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `qa/wp.mjs`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A malformed conditional in the filter.
**Correction.** Filter rewritten to count any box intersecting the media box, whatever its position.
**Evidence of closure.** Demonstrated falsifiable: empty as shipped, returns the element when an overlay is injected into the live page.

### AR-13 &mdash; FIXED-VERIFIED

**Concern.** qa/integrity.mjs contained a dead loop followed by ck(true, 'alt-text limits checked at build time') — an unconditional pass for a check nothing performed.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `qa/integrity.mjs`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Placeholder assertion left in.
**Correction.** The manifest's alt_text column is now parsed and every value checked against 15 words and 125 characters.
**Evidence of closure.** Reports the row count it parsed.

### BR-07 &mdash; FIXED-VERIFIED

**Concern.** qa/integrity.mjs still contained the dead loop and the unconditional ck(true, 'alt-text limits checked at build time'), and the weight guard the ledger claimed existed did not.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `qa/integrity.mjs`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** An earlier repair script died on an assertion before reaching this file, and the fix was recorded as made. It was not.
**Correction.** The alt_text column is now parsed with a real CSV splitter and checked against 15 words and 125 characters; a second check recomputes the site weight from the shipped bytes and fails if any document disagrees.
**Evidence of closure.** The weight guard caught a real 3 KB drift on its first run, and a regex that was reading '2,869 KB' as '869 KB'.

### CR-11 &mdash; FIXED-VERIFIED

**Concern.** The weight guard whitelisted the literal 2869 while reporting that every stated weight matches; rebuild.sh diffed two generated files when four are generated.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `qa/integrity.mjs, qa/rebuild.sh`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A magic number and an incomplete file list.
**Correction.** 2869 is now a named COMPARATORS entry with a comment saying it is the live IHH homepage, not a claim about this package; rebuild.sh diffs copy.html, copy-full.md, preview.html and verify.html.
**Evidence of closure.** Both run clean, and rebuild.sh now covers every generated artefact.


## P4 &mdash; Layout (10)

### EV-06 &mdash; FIXED-VERIFIED

**Concern.** Citations recorded in case files 2-5 never reached the finding sheet
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `assets/site.js`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Listener bound to the first .claims list's parent section
**Correction.** One document listener matching /^[vs]-/
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-07 &mdash; FIXED-VERIFIED

**Concern.** Enter in the search field submitted the form, reloading and wiping all filters
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `assets/site.js`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Implicit form submission, no submit handler
**Correction.** submit handler calls preventDefault() then re-applies filters
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-08 &mdash; FIXED-VERIFIED

**Concern.** Hero text column was 125px at a 320px viewport
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** `.hero` was a flex row; caption sat beside the standfirst
**Correction.** Hero relaid out as a media band with the caption in flow beneath
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### EV-09 &mdash; FIXED-VERIFIED

**Concern.** A loaded photograph covered the credit line entirely
**Source of the concern.** IHH-V3-AUDIT-EVIDENCE.zip (independent reviewer)
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced independently in Chromium before fixing; see qa/repro.mjs. Reviewer's SHA-256 list matched all 21 shipped files byte-for-byte.
**Root cause.** Caption stacked beneath the absolutely positioned image
**Correction.** Caption moved below the media band at z-index 3
**Evidence of closure.** qa/repro.mjs — 9/9 reproduced pre-fix, 0/9 post-fix.

### ST-11 &mdash; FIXED-VERIFIED

**Concern.** The fragment overflowed a 320px viewport.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright-wp/copy.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** An unbreakable archived URL inside <code>.
**Correction.** overflow-wrap:anywhere on code and the metadata lines.
**Evidence of closure.** qa/wp.mjs checks 320, 360, 390, 430, 768 and 1280: no horizontal scrolling at any.

### AR-17 &mdash; FIXED-VERIFIED

**Concern.** site/albright.html referenced two image filenames that exist in no manifest, and carried an undocumented [AUTHOR NAME] placeholder.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Filenames diverged from the manifest when it was rewritten.
**Correction.** Filenames aligned to media-manifest.csv; the placeholder now uses the site-wide .todo marker; the sources-checked date aligned to 2 October 2026.
**Evidence of closure.** grep: 0 occurrences of AUTHOR NAME; both media paths match manifest rows.

### BR-05 &mdash; FIXED-VERIFIED

**Concern.** Live <img src="media/…"> tags and a JSON-LD contentUrl pointed at a media directory that does not exist in site/.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Image references left behind when the media plan moved to albright-wp/.
**Correction.** Both now labelled slots with the original tag preserved in a comment; contentUrl neutralised.
**Evidence of closure.** Comment-stripped parse finds zero live <img> pointing at media/.

### BR-09 &mdash; FIXED-VERIFIED

**Concern.** preview.html was hand-assembled, was not regenerated by build.py, and had gone stale — it still rendered six broken images and the old alt text.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `albright-wp/preview.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A generated artefact maintained by hand.
**Correction.** build.py now emits preview.html from the same OUT string as copy.html, so it cannot drift.
**Evidence of closure.** qa/rebuild.sh regenerates from a fresh extraction.

### FR-10 &mdash; FIXED-VERIFIED

**Concern.** The five body sections of copy.md totalled 525 words against the brief's 'roughly 400'.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/copy.md`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** Accumulated editorial prose.
**Correction.** Trimmed to 461 words with no fact or hedge dropped — the Czech-form caveat, 'perhaps Trawniki', the memoir-versus-wire divergence and the unread-statement note all remain.
**Evidence of closure.** Word count recomputed per section from copy.md; every named hedge still present.

### FR-11 &mdash; FIXED-VERIFIED

**Concern.** site/albright.html scrolled horizontally at 320px: the long archived-URL tokens in the facsimile and transcription panels were not in the overflow-wrap:anywhere rule.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `site/albright.html`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** Unbreakable URL tokens in two panels the wrap rule did not cover.
**Correction.** The rule now covers .facsimile and .transcription and their code elements.
**Evidence of closure.** qa/states.mjs and qa/reflow.mjs: 320px clean on all eleven pages; measured scrollWidth==320.


## P5 &mdash; Integration (3)

### ST-03 &mdash; FIXED-VERIFIED

**Concern.** The .ris citation export emitted TY  - ARCHIVE and put the holding institution in PB.
**Source of the concern.** Repair pass / task §8
**Affected.** `albright.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** ARCHIVE is not a defined RIS type tag; PB is the publisher field, not the repository; and Y1 (publication year) was being used for the access year.
**Correction.** Now TY  - GEN, repository in DP, access date in Y2 with an N1 note. 
**Evidence of closure.** qa/integrity.mjs parses the generated RIS and asserts the tags are defined ones.

### ST-04 &mdash; FIXED-VERIFIED

**Concern.** gen.py hardcoded /home/claude/ihh-site/ as the site root.
**Source of the concern.** Repair pass / task §8
**Affected.** `gen.py`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Absolute path from the build machine. The generator could not be re-run from a fresh extraction, so generated output could silently drift from cases.py.
**Correction.** Paths now resolve from __file__. Verified by running it from a clean extraction in a different directory.
**Evidence of closure.** qa/rebuild.sh extracts the final ZIP to a temp dir, runs both generators, and diffs.

### AR-14 &mdash; FIXED-VERIFIED

**Concern.** All harnesses hardcoded this machine's Chromium path and one wrote to an absolute output directory, while integrity.mjs asserted no build-machine paths in the generators.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `qa/*.mjs`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Written for one machine.
**Correction.** CHROMIUM and QA_OUT environment overrides, documented in the README run block.
**Evidence of closure.** grep: no bare absolute Chromium path remains.


## P6 &mdash; Documentation (17)

### ST-05 &mdash; FIXED-VERIFIED

**Concern.** The inductee index said 'Everything below is searchable.'
**Source of the concern.** Repair pass / task §8
**Affected.** `inductees.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Overstated: the filter matches card text only, and nine of ten profiles do not exist.
**Correction.** Reworded to say exactly what it searches and why.
**Evidence of closure.** Read in the shipped file.

### ST-06 &mdash; FIXED-VERIFIED

**Concern.** method.html stated a page weight that the package no longer had.
**Source of the concern.** Repair pass / task §8
**Affected.** `method.html`
**Our reproduction / verification.** Reproduced in the shipped v4 package before changing anything.
**Root cause.** Figure not regenerated after content changes.
**Correction.** Recomputed from the shipped files, and the brief scorecard row corrected to name albright-wp/ as the required deliverable rather than the site.
**Evidence of closure.** qa/integrity.mjs recomputes the site weight from the shipped files and fails if any document states a different figure.

### AR-07 &mdash; FIXED-VERIFIED

**Concern.** Four documents stated a site weight of 242 KB; the shipped bytes are 262 KB, and the 'packaging script that fails if the figure drifts' did not exist.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `site/FINDINGS.md, SITE-README.md, TESTS-RUN.md, method.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Figure not recomputed after the content changes; the guard was described, not built.
**Correction.** All four corrected, and the guard built: qa/integrity.mjs now recomputes the weight from the shipped files and fails if any document disagrees.
**Evidence of closure.** qa/integrity.mjs 'stated site weight matches the shipped bytes'.

### AR-15 &mdash; FIXED-VERIFIED

**Concern.** The README's run block passed five harness paths as argv to the first one, so only dark.mjs ran; it also said 11 harnesses where there are 12 plus rebuild.sh.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `README.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Shell written without running it.
**Correction.** Replaced with a loop that runs each and reports failures, plus the rebuild step and the prerequisites.
**Evidence of closure.** Run as printed.

### AR-16 &mdash; FIXED-VERIFIED

**Concern.** INSTALL.md said the byline placeholder appears three times; it appears twice.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `albright-wp/INSTALL.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Miscount.
**Correction.** Corrected, and copy-full.md's copies are named too.
**Evidence of closure.** Count derived from copy.html at edit time.

### AR-18 &mdash; FIXED-VERIFIED

**Concern.** README and R-02 claimed diplomacy.state.gov was refused and the 1998 statement unreachable 'on every route including web archives', but the evidence logs covered only catalog.archives.gov.
**Source of the concern.** Independent acceptance review, round 1
**Affected.** `README.md, ledger/`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The claim was true but only partly evidenced.
**Correction.** Re-attempted all five URLs and captured the denials: catalog.archives.gov, diplomacy.state.gov, 1997-2001.state.gov and web.archive.org all refused at CONNECT.
**Evidence of closure.** ledger/fetch-attempts.txt (5 URLs, all 000) and ledger/proxy-denial.txt (4 hosts).

### BR-13 &mdash; FIXED-VERIFIED

**Concern.** INSTALL.md described one image slot to switch on; there are seven. The only 'direct download' URL in the package has never been tested and may be wrong.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `albright-wp/INSTALL.md, media/fetch-media.sh, media-manifest.csv`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** The six thumbnail slots were added after INSTALL.md was written; the URL came from research notes.
**Correction.** All seven slots documented with the search term that finds them; the URL labelled untested everywhere it appears, with the record's Download control given as the reliable route.
**Evidence of closure.** Read in the shipped files.

### BR-14 &mdash; FIXED-VERIFIED

**Concern.** robots.txt and the JSON-LD publisher still asserted the live museum's domain, which is the defect ST-01 fixed in the sitemap.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `site/robots.txt, site/albright.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** ST-01 was applied to one file only.
**Correction.** Both now use example.invalid, with the reason stated.
**Evidence of closure.** qa/integrity.mjs checks the sitemap; grep covers the other two.

### BR-15 &mdash; FIXED-VERIFIED

**Concern.** Four smaller documentation defects: README described copy.md as 'the same words as Markdown' when it omits the source set; the manifest's reasoning pointed at the wrong neighbouring column; required_credit duplicated the institution on three rows; the ledger named a file not in the package and leaked build-environment detail into a deliverable.
**Source of the concern.** Independent acceptance review, round 2
**Affected.** `README.md, media-manifest.csv, ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Accumulated drift.
**Correction.** All four corrected.
**Evidence of closure.** Read in the shipped files.

### CR-09 &mdash; FIXED-VERIFIED

**Concern.** proxy-denial.txt's header listed the four archival hosts as refused, but its raw log — a rolling buffer — had rotated and contained only unrelated hosts. README cited this file as the evidence for the project's central constraint.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `ledger/proxy-denial.txt`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** A rolling buffer captured at the wrong moment and never re-read.
**Correction.** The file now says plainly that the buffer rotates, that it may not contain the archival hosts, and that fetch-attempts.txt is the authoritative per-URL record.
**Evidence of closure.** fetch-attempts.txt shows all five archival URLs returning 000.

### CR-10 &mdash; FIXED-VERIFIED

**Concern.** Six documentation defects: FINDINGS said four of the failed claims were ours (two are) and axe ran on 9 pages (11); 'seven image files' where there are six files in seven slots; SITE-README listed a manifest that had been deleted and miscounted the harnesses; TESTS-RUN still described one external audit when three had run.
**Source of the concern.** Independent acceptance review, round 3
**Affected.** `site/FINDINGS.md, site/SITE-README.md, site/TESTS-RUN.md`
**Our reproduction / verification.** Reported by the reviewer and reproduced here before changing anything.
**Root cause.** Accumulated drift.
**Correction.** All corrected, and the audit history now records all three rounds with their defect counts.
**Evidence of closure.** Read in the shipped files.

### DR-05 &mdash; FIXED-VERIFIED

**Concern.** method.html still said seven image files have to be downloaded; there are six files in seven slots, and the rest of the package had already been corrected.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `site/method.html`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** The round-3 seven/six sweep covered FINDINGS, TESTS-RUN and SITE-README but not method.html.
**Correction.** Corrected in both places on the page.
**Evidence of closure.** grep across the package: no 'seven image' remains outside the ledger's record of the defect.

### DR-07 &mdash; FIXED-VERIFIED

**Concern.** A ledger entry restated the package weight as a figure in prose, which drifts every time a file changes.
**Source of the concern.** Independent acceptance review, round 4
**Affected.** `ledger/findings.py`
**Our reproduction / verification.** Reported by the reviewer and reproduced in the shipped file before changing anything.
**Root cause.** A formatted literal where a derived value belonged.
**Correction.** The sentence no longer carries the number; the weight is stated once, in the documentation, and checked against the shipped bytes by qa/integrity.mjs.
**Evidence of closure.** integrity.mjs asserts, from the shipped bytes, that every weight figure stated in the documentation matches the files; it recomputes the number rather than trusting prose.

### ER-03 &mdash; FIXED-VERIFIED

**Concern.** The same summaries counted 'three images considered and turned down' where the excluded-sources list has four entries covering two UN photographs, the brooch photographs and the State Department Flickr stream.
**Source of the concern.** Verification sweep, round 5
**Affected.** `site/albright.html, site/index.html, site/FINDINGS.md`
**Our reproduction / verification.** Found by recounting every stated figure against the file it describes, after the round-4 fixes had passed the full harness suite.
**Root cause.** Another count carried in prose rather than read off the list.
**Correction.** Restated as four lines of imagery, which is what the list contains.
**Evidence of closure.** Counted from the <li> elements in the excluded section.

### FR-03 &mdash; FIXED-VERIFIED

**Concern.** site/SITE-README.md still said 'Seven files still need downloading' when there are six image files.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `site/SITE-README.md`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** A seven/six sweep in an earlier round missed this line.
**Correction.** Corrected to six.
**Evidence of closure.** grep: no 'Seven files' remains.

### FR-07 &mdash; FIXED-VERIFIED

**Concern.** INSTALL.md told self-hosted WordPress users to paste copy.html but never told them the uncommented src='media/…' paths are relative and will not resolve on a live site; the upload-and-repoint step existed only under the WordPress.com route.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/INSTALL.md`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** The image-hosting instruction was attached to one of the two routes.
**Correction.** The self-hosted route now says to upload the six photographs to the media library and repoint each src, and notes the slot stays a labelled box (not a broken image) until then.
**Evidence of closure.** Read in the shipped file.

### FR-09 &mdash; FIXED-VERIFIED

**Concern.** copy-full.md (the WordPress.com rebuild source) carried build-time spec labels — 'Opening line (sits above the photograph):', 'Credit (sits immediately beneath…):', 'First-person quotation (one, as reported by…):' — which would publish as body text in a block rebuild.
**Source of the concern.** Final repair round (post three-reviewer acceptance pass)
**Affected.** `albright-wp/build.py`
**Our reproduction / verification.** Reproduced in the authoritative working tree before changing anything; reviewer findings that did not reproduce there were not acted on.
**Root cause.** copy-full.md was assembled from the raw copy.md, whose labels are parse markers for the HTML build.
**Correction.** build.py now strips the build-spec parentheticals from those labels when assembling copy-full.md, leaving clean block guidance.
**Evidence of closure.** grep: 'sits above the photograph' no longer appears in copy-full.md.
