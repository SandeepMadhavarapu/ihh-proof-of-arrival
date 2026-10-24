# Actual command outputs — Workstream 1

Run on 17 October 2026. Local HTTP servers served `site/` on 8731 and the repository on 8741. Browser commands used `CHROMIUM=/tmp/ihh-chromium`. These are captured outputs, not guarantees for later changes.

## dark

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/dark.mjs
  ✓ light scheme, toggles pressed, disclosures open: 0 violations across 20 pages
  ✓ dark scheme, toggles pressed, disclosures open: 0 violations across 20 pages

TOTAL: 0
```

## fresh-clone-drift

```text
$ fresh-clone-drift (see REPORT.md)
(empty output; exit 0)
```

## fresh-clone-rebuild

```text
$ bash qa/rebuild.sh (in fresh local clone)
OPEN ITEM: berlin/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: einstein/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: hope/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: muir/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: naismith/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: strauss/search-log.csv missing; team lead will supply the actual research log.
  OK   site/verify.html regenerates byte-identically
  OK   handover/OPEN-ITEMS.md regenerates byte-identically
  OK   site/albright.html regenerates byte-identically
  OK   handover/albright/copy.html regenerates byte-identically
  OK   handover/albright/copy-full.md regenerates byte-identically
  OK   handover/albright/preview.html regenerates byte-identically
  OK   handover/albright/media-manifest.csv regenerates byte-identically
  OK   inductees/albright/copy.html regenerates byte-identically
  OK   inductees/albright/copy-full.md regenerates byte-identically
  OK   inductees/albright/preview.html regenerates byte-identically
  OK   inductees/albright/media/web/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   site/media/albright/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   site/media/albright/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   site/media/albright/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-2016-naturalization.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-2016-naturalization.jpg regenerates byte-identically
  OK   site/media/albright/albright-2016-naturalization.jpg regenerates byte-identically
  OK   handover/albright/search-log.csv regenerates byte-identically
  OK   site/berlin.html regenerates byte-identically
  OK   handover/berlin/copy.html regenerates byte-identically
  OK   handover/berlin/copy-full.md regenerates byte-identically
  OK   handover/berlin/preview.html regenerates byte-identically
  OK   handover/berlin/media-manifest.csv regenerates byte-identically
  OK   inductees/berlin/copy.html regenerates byte-identically
  OK   inductees/berlin/copy-full.md regenerates byte-identically
  OK   inductees/berlin/preview.html regenerates byte-identically
  OK   inductees/berlin/media/web/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   handover/berlin/media/web/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   site/media/berlin/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   site/cruz.html regenerates byte-identically
  OK   handover/cruz/copy.html regenerates byte-identically
  OK   handover/cruz/copy-full.md regenerates byte-identically
  OK   handover/cruz/preview.html regenerates byte-identically
  OK   handover/cruz/media-manifest.csv regenerates byte-identically
  OK   inductees/cruz/copy.html regenerates byte-identically
  OK   inductees/cruz/copy-full.md regenerates byte-identically
  OK   inductees/cruz/preview.html regenerates byte-identically
  OK   inductees/cruz/media/web/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   handover/cruz/media/web/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   site/media/cruz/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   inductees/cruz/media/web/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   handover/cruz/media/web/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   site/media/cruz/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   handover/cruz/search-log.csv regenerates byte-identically
  OK   site/einstein.html regenerates byte-identically
  OK   handover/einstein/copy.html regenerates byte-identically
  OK   handover/einstein/copy-full.md regenerates byte-identically
  OK   handover/einstein/preview.html regenerates byte-identically
  OK   handover/einstein/media-manifest.csv regenerates byte-identically
  OK   inductees/einstein/copy.html regenerates byte-identically
  OK   inductees/einstein/copy-full.md regenerates byte-identically
  OK   inductees/einstein/preview.html regenerates byte-identically
  OK   inductees/einstein/media/web/einstein-portrait-turner.jpg regenerates byte-identically
  OK   handover/einstein/media/web/einstein-portrait-turner.jpg regenerates byte-identically
  OK   site/media/einstein/einstein-portrait-turner.jpg regenerates byte-identically
  OK   site/hope.html regenerates byte-identically
  OK   handover/hope/copy.html regenerates byte-identically
  OK   handover/hope/copy-full.md regenerates byte-identically
  OK   handover/hope/preview.html regenerates byte-identically
  OK   handover/hope/media-manifest.csv regenerates byte-identically
  OK   inductees/hope/copy.html regenerates byte-identically
  OK   inductees/hope/copy-full.md regenerates byte-identically
  OK   inductees/hope/preview.html regenerates byte-identically
  OK   inductees/hope/media/web/hope-portrait-nbc.jpg regenerates byte-identically
  OK   handover/hope/media/web/hope-portrait-nbc.jpg regenerates byte-identically
  OK   site/media/hope/hope-portrait-nbc.jpg regenerates byte-identically
  OK   site/lamarr.html regenerates byte-identically
  OK   handover/lamarr/copy.html regenerates byte-identically
  OK   handover/lamarr/copy-full.md regenerates byte-identically
  OK   handover/lamarr/preview.html regenerates byte-identically
  OK   handover/lamarr/media-manifest.csv regenerates byte-identically
  OK   inductees/lamarr/copy.html regenerates byte-identically
  OK   inductees/lamarr/copy-full.md regenerates byte-identically
  OK   inductees/lamarr/preview.html regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   handover/lamarr/search-log.csv regenerates byte-identically
  OK   site/muir.html regenerates byte-identically
  OK   handover/muir/copy.html regenerates byte-identically
  OK   handover/muir/copy-full.md regenerates byte-identically
  OK   handover/muir/preview.html regenerates byte-identically
  OK   handover/muir/media-manifest.csv regenerates byte-identically
  OK   inductees/muir/copy.html regenerates byte-identically
  OK   inductees/muir/copy-full.md regenerates byte-identically
  OK   inductees/muir/preview.html regenerates byte-identically
  OK   inductees/muir/media/web/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   handover/muir/media/web/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   site/media/muir/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   site/naismith.html regenerates byte-identically
  OK   handover/naismith/copy.html regenerates byte-identically
  OK   handover/naismith/copy-full.md regenerates byte-identically
  OK   handover/naismith/preview.html regenerates byte-identically
  OK   handover/naismith/media-manifest.csv regenerates byte-identically
  OK   inductees/naismith/copy.html regenerates byte-identically
  OK   inductees/naismith/copy-full.md regenerates byte-identically
  OK   inductees/naismith/preview.html regenerates byte-identically
  OK   inductees/naismith/media/web/naismith-portrait.jpg regenerates byte-identically
  OK   handover/naismith/media/web/naismith-portrait.jpg regenerates byte-identically
  OK   site/media/naismith/naismith-portrait.jpg regenerates byte-identically
  OK   site/pei.html regenerates byte-identically
  OK   handover/pei/copy.html regenerates byte-identically
  OK   handover/pei/copy-full.md regenerates byte-identically
  OK   handover/pei/preview.html regenerates byte-identically
  OK   handover/pei/media-manifest.csv regenerates byte-identically
  OK   inductees/pei/copy.html regenerates byte-identically
  OK   inductees/pei/copy-full.md regenerates byte-identically
  OK   inductees/pei/preview.html regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   site/media/pei/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   site/media/pei/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   site/media/pei/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   site/media/pei/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   handover/pei/search-log.csv regenerates byte-identically
  OK   site/strauss.html regenerates byte-identically
  OK   handover/strauss/copy.html regenerates byte-identically
  OK   handover/strauss/copy-full.md regenerates byte-identically
  OK   handover/strauss/preview.html regenerates byte-identically
  OK   handover/strauss/media-manifest.csv regenerates byte-identically
  OK   inductees/strauss/copy.html regenerates byte-identically
  OK   inductees/strauss/copy-full.md regenerates byte-identically
  OK   inductees/strauss/preview.html regenerates byte-identically
  OK   inductees/strauss/media/web/strauss-portrait.jpg regenerates byte-identically
  OK   handover/strauss/media/web/strauss-portrait.jpg regenerates byte-identically
  OK   site/media/strauss/strauss-portrait.jpg regenerates byte-identically

ALL GENERATED FILES MATCH THEIR SOURCES
PASS albright: package, media, reconciliation and research-log disclosure
PASS berlin: package, media, reconciliation and research-log disclosure
PASS cruz: package, media, reconciliation and research-log disclosure
PASS einstein: package, media, reconciliation and research-log disclosure
PASS hope: package, media, reconciliation and research-log disclosure
PASS lamarr: package, media, reconciliation and research-log disclosure
PASS muir: package, media, reconciliation and research-log disclosure
PASS naismith: package, media, reconciliation and research-log disclosure
PASS pei: package, media, reconciliation and research-log disclosure
PASS strauss: package, media, reconciliation and research-log disclosure
PASS all ten handover packages
PASS key-like secret scan across all tracked text files (including Markdown)
```

## handover

```text
$ python qa/handover.py
PASS albright: package, media, reconciliation and research-log disclosure
PASS berlin: package, media, reconciliation and research-log disclosure
PASS cruz: package, media, reconciliation and research-log disclosure
PASS einstein: package, media, reconciliation and research-log disclosure
PASS hope: package, media, reconciliation and research-log disclosure
PASS lamarr: package, media, reconciliation and research-log disclosure
PASS muir: package, media, reconciliation and research-log disclosure
PASS naismith: package, media, reconciliation and research-log disclosure
PASS pei: package, media, reconciliation and research-log disclosure
PASS strauss: package, media, reconciliation and research-log disclosure
PASS all ten handover packages
```

## incomplete

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/incomplete.mjs
axe "incomplete" colour-contrast nodes across 11 pages: 73
  70×  Element's background color could not be determined due to a background gradient
  2×  Element's background color could not be determined due to a pseudo element
  1×  Element content contains only non-text characters
```

## integrity

```text
$ node qa/integrity.mjs .
  OK   no form can submit personal data by GET 
  OK   the story page collects nothing
  OK   no href="#" placeholder links (0)
  OK   no sitemap <loc> asserts the live museum domain
  OK   every sitemap <loc> is an absolute URL as the spec requires
  OK   sitemap lists every page except 404 (19 vs 19)
  OK   albright.html: no script inside the profile
  OK   albright.html: all 5 images have alt text
  OK   albright.html: anchor image carries its rights wording
  OK   berlin.html: no script inside the profile
  OK   berlin.html: all 2 images have alt text
  OK   berlin.html: anchor image carries its rights wording
  OK   cruz.html: no script inside the profile
  OK   cruz.html: all 3 images have alt text
  OK   cruz.html: anchor image carries its rights wording
  OK   einstein.html: no script inside the profile
  OK   einstein.html: all 2 images have alt text
  OK   einstein.html: anchor image carries its rights wording
  OK   hope.html: no script inside the profile
  OK   hope.html: all 2 images have alt text
  OK   hope.html: anchor image carries its rights wording
  OK   lamarr.html: no script inside the profile
  OK   lamarr.html: all 7 images have alt text
  OK   lamarr.html: anchor image carries its rights wording
  OK   muir.html: no script inside the profile
  OK   muir.html: all 2 images have alt text
  OK   muir.html: anchor image carries its rights wording
  OK   naismith.html: no script inside the profile
  OK   naismith.html: all 2 images have alt text
  OK   naismith.html: anchor image carries its rights wording
  OK   pei.html: no script inside the profile
  OK   pei.html: all 9 images have alt text
  OK   pei.html: anchor image carries its rights wording
  OK   strauss.html: no script inside the profile
  OK   strauss.html: all 2 images have alt text
  OK   strauss.html: anchor image carries its rights wording
  OK   no un-retracted copyright claim in 404.html
  OK   no un-retracted copyright claim in about.html
  OK   no un-retracted copyright claim in accessibility.html
  OK   no un-retracted copyright claim in albright.html
  OK   no un-retracted copyright claim in berlin.html
  OK   no un-retracted copyright claim in cruz.html
  OK   no un-retracted copyright claim in einstein.html
  OK   no un-retracted copyright claim in hope.html
  OK   no un-retracted copyright claim in index.html
  OK   no un-retracted copyright claim in inductees.html
  OK   no un-retracted copyright claim in lamarr.html
  OK   no un-retracted copyright claim in method.html
  OK   no un-retracted copyright claim in muir.html
  OK   no un-retracted copyright claim in naismith.html
  OK   no un-retracted copyright claim in pei.html
  OK   no un-retracted copyright claim in privacy.html
  OK   no un-retracted copyright claim in rights.html
  OK   no un-retracted copyright claim in share.html
  OK   no un-retracted copyright claim in strauss.html
  OK   no un-retracted copyright claim in verify.html
  OK   no un-retracted copyright claim in FINDINGS.md
  OK   albright: WordPress fragment contains zero script tags
  OK   albright: fragment loads no external resource
  OK   albright: original fragment retains 10+ source items
  OK   albright: original search log present
  OK   albright: every non-dropped manifest row rendered exactly once
  OK   albright: manifest alt_text column parsed (6 values)
  OK   albright: every alt text <=15 words and <=125 chars
  OK   albright: every image used was viewed before it was described
  OK   albright: all 5 images present in media/web
  OK   berlin: WordPress fragment contains zero script tags
  OK   berlin: fragment loads no external resource
  OK   berlin: missing research log explicitly reported
  OK   berlin: every non-dropped manifest row rendered exactly once
  OK   berlin: manifest alt_text column parsed (1 values)
  OK   berlin: every alt text <=15 words and <=125 chars
  OK   berlin: every image used was viewed before it was described
  OK   berlin: all 2 images present in media/web
  OK   cruz: WordPress fragment contains zero script tags
  OK   cruz: fragment loads no external resource
  OK   cruz: original fragment retains 10+ source items
  OK   cruz: original search log present
  OK   cruz: every non-dropped manifest row rendered exactly once
  OK   cruz: manifest alt_text column parsed (2 values)
  OK   cruz: every alt text <=15 words and <=125 chars
  OK   cruz: every image used was viewed before it was described
  OK   cruz: all 3 images present in media/web
  OK   einstein: WordPress fragment contains zero script tags
  OK   einstein: fragment loads no external resource
  OK   einstein: missing research log explicitly reported
  OK   einstein: every non-dropped manifest row rendered exactly once
  OK   einstein: manifest alt_text column parsed (1 values)
  OK   einstein: every alt text <=15 words and <=125 chars
  OK   einstein: every image used was viewed before it was described
  OK   einstein: all 2 images present in media/web
  OK   hope: WordPress fragment contains zero script tags
  OK   hope: fragment loads no external resource
  OK   hope: missing research log explicitly reported
  OK   hope: every non-dropped manifest row rendered exactly once
  OK   hope: manifest alt_text column parsed (1 values)
  OK   hope: every alt text <=15 words and <=125 chars
  OK   hope: every image used was viewed before it was described
  OK   hope: all 2 images present in media/web
  OK   lamarr: WordPress fragment contains zero script tags
  OK   lamarr: fragment loads no external resource
  OK   lamarr: original fragment retains 10+ source items
  OK   lamarr: original search log present
  OK   lamarr: every non-dropped manifest row rendered exactly once
  OK   lamarr: manifest alt_text column parsed (5 values)
  OK   lamarr: every alt text <=15 words and <=125 chars
  OK   lamarr: every image used was viewed before it was described
  OK   lamarr: all 7 images present in media/web
  OK   muir: WordPress fragment contains zero script tags
  OK   muir: fragment loads no external resource
  OK   muir: missing research log explicitly reported
  OK   muir: every non-dropped manifest row rendered exactly once
  OK   muir: manifest alt_text column parsed (1 values)
  OK   muir: every alt text <=15 words and <=125 chars
  OK   muir: every image used was viewed before it was described
  OK   muir: all 2 images present in media/web
  OK   naismith: WordPress fragment contains zero script tags
  OK   naismith: fragment loads no external resource
  OK   naismith: missing research log explicitly reported
  OK   naismith: every non-dropped manifest row rendered exactly once
  OK   naismith: manifest alt_text column parsed (1 values)
  OK   naismith: every alt text <=15 words and <=125 chars
  OK   naismith: every image used was viewed before it was described
  OK   naismith: all 2 images present in media/web
  OK   pei: WordPress fragment contains zero script tags
  OK   pei: fragment loads no external resource
  OK   pei: original fragment retains 10+ source items
  OK   pei: original search log present
  OK   pei: every non-dropped manifest row rendered exactly once
  OK   pei: manifest alt_text column parsed (7 values)
  OK   pei: every alt text <=15 words and <=125 chars
  OK   pei: every image used was viewed before it was described
  OK   pei: all 9 images present in media/web
  OK   strauss: WordPress fragment contains zero script tags
  OK   strauss: fragment loads no external resource
  OK   strauss: missing research log explicitly reported
  OK   strauss: every non-dropped manifest row rendered exactly once
  OK   strauss: manifest alt_text column parsed (1 values)
  OK   strauss: every alt text <=15 words and <=125 chars
  OK   strauss: every image used was viewed before it was described
  OK   strauss: all 2 images present in media/web
  OK   albright: manifest preserves the commission's duplicate identification
  OK   handover/INSTALL.md present
  OK   site weight is stated in the documentation (462 KB found)
  OK   every stated site weight matches the shipped bytes (462 KB)
  OK   no absolute build-machine path in gen.py
  OK   no absolute build-machine path in build_profile.py
  OK   no absolute build-machine path in build_site_pages.py

ALL 148 INTEGRITY CHECKS PASSED
```

## interact

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/interact.mjs

PASS (39)
  ✓ 20 claims rendered (15+ expected)
  ✓ every one of the 20 claims has an evidence drawer
  ✓ 47 evidence items across 20 claims
  ✓ curator findings start closed
  ✓ tally starts at 0
  ✓ sheet starts empty
  ✓ first verdict control is focusable
  ✓ arrow keys move and select within the radio group (got contradicted)
  ✓ recording a verdict opens the curator finding
  ✓ claim marked answered
  ✓ tally incremented to 1
  ✓ agreement reported: "Your finding matches the curator."
  ✓ status line reports agreement
  ✓ finding sheet built
  ✓ citation step hidden before a verdict is recorded
  ✓ citation step appears once a verdict is recorded
  ✓ citation recorded on the finding sheet
  ✓ visitor may reject the curator’s own evidence
  ✓ disagreement recorded without overriding the visitor
  ✓ curator reasoning shown even when you disagree
  ✓ clear resets the tally
  ✓ clear re-closes the curator findings
  ✓ clear empties the sheet
  ✓ no JS errors (none)
  ✓ verdicts register in all 5 case files
  ✓ citations register in all 5 case files (got 5 of 5)
  ✓ tally counts across case files
  ✓ Enter in the search field keeps the filter ("Showing 1 of 10." -> "Showing 1 of 10.")
  ✓ Enter does not reload the page
  ✓ axe clean with ALL drawers open 
  ✓ all targets ≥24×24 
  ✓ no-JS: all 20 claims present
  ✓ no-JS: all 47 evidence items present
  ✓ no-JS: every curator verdict still in the page
  ✓ no-JS: every lesson still readable
  ✓ no-JS: 60 verdict controls (3 per claim) still usable
  ✓ no-JS: 67 citation controls (one per evidence item plus "none") still usable
  ✓ no-JS: the citation step is visible (not gated on script)
  ✓ no-JS: evidence drawer opens natively

ALL 39 CHECKS PASSED
```

## leak

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/leak.mjs
No site-theme rule changes rendering inside the exhibit.
```

## nojs

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/nojs.mjs
  ✓ phone 375, no JavaScript: all 20 pages fully readable and navigable
  ✓ desktop 1280, no JavaScript: all 20 pages fully readable and navigable

No content is hidden behind JavaScript on any page, at either width.
```

## package

```text
$ bash tools/package_handover.sh
inductees/albright: 5 sections, 14 sources (4 images), 5 questions, 2 activities, 0 script tags
inductees/berlin: 5 sections, 5 sources (1 images), 5 questions, 2 activities, 0 script tags
inductees/cruz: 5 sections, 10 sources (2 images), 5 questions, 2 activities, 0 script tags
inductees/einstein: 5 sections, 8 sources (1 images), 5 questions, 2 activities, 0 script tags
inductees/hope: 5 sections, 5 sources (1 images), 5 questions, 2 activities, 0 script tags
inductees/lamarr: 5 sections, 11 sources (5 images), 5 questions, 2 activities, 0 script tags
inductees/muir: 5 sections, 8 sources (1 images), 5 questions, 2 activities, 0 script tags
inductees/naismith: 5 sections, 7 sources (1 images), 5 questions, 2 activities, 0 script tags
inductees/pei: 5 sections, 13 sources (7 images), 5 questions, 2 activities, 0 script tags
inductees/strauss: 5 sections, 5 sources (1 images), 5 questions, 2 activities, 0 script tags
OPEN ITEM: berlin/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: einstein/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: hope/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: muir/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: naismith/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: strauss/search-log.csv missing; team lead will supply the actual research log.
handover/ assembled (human sign-off pending): 7.4M zip
```

## pipeline-commands

```text
$ pipeline-commands (see REPORT.md)
$ /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -m pipeline.generic_build --profile-dir profiles/madeleine-albright
exit=0
generic profile written: $REPO/profiles/madeleine-albright/copy.html, $REPO/profiles/madeleine-albright/copy-full.md, $REPO/profiles/madeleine-albright/preview.html

$ node qa/integrity.mjs .
exit=0
  OK   no form can submit personal data by GET 
  OK   the story page collects nothing
  OK   no href="#" placeholder links (0)
  OK   no sitemap <loc> asserts the live museum domain
  OK   every sitemap <loc> is an absolute URL as the spec requires
  OK   sitemap lists every page except 404 (19 vs 19)
  OK   albright.html: no script inside the profile
  OK   albright.html: all 5 images have alt text
  OK   albright.html: anchor image carries its rights wording
  OK   berlin.html: no script inside the profile
  OK   berlin.html: all 2 images have alt text
  OK   berlin.html: anchor image carries its rights wording
  OK   cruz.html: no script inside the profile
  OK   cruz.html: all 3 images have alt text
  OK   cruz.html: anchor image carries its rights wording
  OK   einstein.html: no script inside the profile
  OK   einstein.html: all 2 images have alt text
  OK   einstein.html: anchor image carries its rights wording
  OK   hope.html: no script inside the profile
  OK   hope.html: all 2 images have alt text
  OK   hope.html: anchor image carries its rights wording
  OK   lamarr.html: no script inside the profile
  OK   lamarr.html: all 7 images have alt text
  OK   lamarr.html: anchor image carries its rights wording
  OK   muir.html: no script inside the profile
  OK   muir.html: all 2 images have alt text
  OK   muir.html: anchor image carries its rights wording
  OK   naismith.html: no script inside the profile
  OK   naismith.html: all 2 images have alt text
  OK   naismith.html: anchor image carries its rights wording
  OK   pei.html: no script inside the profile
  OK   pei.html: all 9 images have alt text
  OK   pei.html: anchor image carries its rights wording
  OK   strauss.html: no script inside the profile
  OK   strauss.html: all 2 images have alt text
  OK   strauss.html: anchor image carries its rights wording
  OK   no un-retracted copyright claim in 404.html
  OK   no un-retracted copyright claim in about.html
  OK   no un-retracted copyright claim in accessibility.html
  OK   no un-retracted copyright claim in albright.html
  OK   no un-retracted copyright claim in berlin.html
  OK   no un-retracted copyright claim in cruz.html
  OK   no un-retracted copyright claim in einstein.html
  OK   no un-retracted copyright claim in hope.html
  OK   no un-retracted copyright claim in index.html
  OK   no un-retracted copyright claim in inductees.html
  OK   no un-retracted copyright claim in lamarr.html
  OK   no un-retracted copyright claim in method.html
  OK   no un-retracted copyright claim in muir.html
  OK   no un-retracted copyright claim in naismith.html
  OK   no un-retracted copyright claim in pei.html
  OK   no un-retracted copyright claim in privacy.html
  OK   no un-retracted copyright claim in rights.html
  OK   no un-retracted copyright claim in share.html
  OK   no un-retracted copyright claim in strauss.html
  OK   no un-retracted copyright claim in verify.html
  OK   no un-retracted copyright claim in FINDINGS.md
  OK   albright: WordPress fragment contains zero script tags
  OK   albright: fragment loads no external resource
  OK   albright: original fragment retains 10+ source items
  OK   albright: original search log present
  OK   albright: every non-dropped manifest row rendered exactly once
  OK   albright: manifest alt_text column parsed (6 values)
  OK   albright: every alt text <=15 words and <=125 chars
  OK   albright: every image used was viewed before it was described
  OK   albright: all 5 images present in media/web
  OK   berlin: WordPress fragment contains zero script tags
  OK   berlin: fragment loads no external resource
  OK   berlin: missing research log explicitly reported
  OK   berlin: every non-dropped manifest row rendered exactly once
  OK   berlin: manifest alt_text column parsed (1 values)
  OK   berlin: every alt text <=15 words and <=125 chars
  OK   berlin: every image used was viewed before it was described
  OK   berlin: all 2 images present in media/web
  OK   cruz: WordPress fragment contains zero script tags
  OK   cruz: fragment loads no external resource
  OK   cruz: original fragment retains 10+ source items
  OK   cruz: original search log present
  OK   cruz: every non-dropped manifest row rendered exactly once
  OK   cruz: manifest alt_text column parsed (2 values)
  OK   cruz: every alt text <=15 words and <=125 chars
  OK   cruz: every image used was viewed before it was described
  OK   cruz: all 3 images present in media/web
  OK   einstein: WordPress fragment contains zero script tags
  OK   einstein: fragment loads no external resource
  OK   einstein: missing research log explicitly reported
  OK   einstein: every non-dropped manifest row rendered exactly once
  OK   einstein: manifest alt_text column parsed (1 values)
  OK   einstein: every alt text <=15 words and <=125 chars
  OK   einstein: every image used was viewed before it was described
  OK   einstein: all 2 images present in media/web
  OK   hope: WordPress fragment contains zero script tags
  OK   hope: fragment loads no external resource
  OK   hope: missing research log explicitly reported
  OK   hope: every non-dropped manifest row rendered exactly once
  OK   hope: manifest alt_text column parsed (1 values)
  OK   hope: every alt text <=15 words and <=125 chars
  OK   hope: every image used was viewed before it was described
  OK   hope: all 2 images present in media/web
  OK   lamarr: WordPress fragment contains zero script tags
  OK   lamarr: fragment loads no external resource
  OK   lamarr: original fragment retains 10+ source items
  OK   lamarr: original search log present
  OK   lamarr: every non-dropped manifest row rendered exactly once
  OK   lamarr: manifest alt_text column parsed (5 values)
  OK   lamarr: every alt text <=15 words and <=125 chars
  OK   lamarr: every image used was viewed before it was described
  OK   lamarr: all 7 images present in media/web
  OK   muir: WordPress fragment contains zero script tags
  OK   muir: fragment loads no external resource
  OK   muir: missing research log explicitly reported
  OK   muir: every non-dropped manifest row rendered exactly once
  OK   muir: manifest alt_text column parsed (1 values)
  OK   muir: every alt text <=15 words and <=125 chars
  OK   muir: every image used was viewed before it was described
  OK   muir: all 2 images present in media/web
  OK   naismith: WordPress fragment contains zero script tags
  OK   naismith: fragment loads no external resource
  OK   naismith: missing research log explicitly reported
  OK   naismith: every non-dropped manifest row rendered exactly once
  OK   naismith: manifest alt_text column parsed (1 values)
  OK   naismith: every alt text <=15 words and <=125 chars
  OK   naismith: every image used was viewed before it was described
  OK   naismith: all 2 images present in media/web
  OK   pei: WordPress fragment contains zero script tags
  OK   pei: fragment loads no external resource
  OK   pei: original fragment retains 10+ source items
  OK   pei: original search log present
  OK   pei: every non-dropped manifest row rendered exactly once
  OK   pei: manifest alt_text column parsed (7 values)
  OK   pei: every alt text <=15 words and <=125 chars
  OK   pei: every image used was viewed before it was described
  OK   pei: all 9 images present in media/web
  OK   strauss: WordPress fragment contains zero script tags
  OK   strauss: fragment loads no external resource
  OK   strauss: missing research log explicitly reported
  OK   strauss: every non-dropped manifest row rendered exactly once
  OK   strauss: manifest alt_text column parsed (1 values)
  OK   strauss: every alt text <=15 words and <=125 chars
  OK   strauss: every image used was viewed before it was described
  OK   strauss: all 2 images present in media/web
  OK   albright: manifest preserves the commission's duplicate identification
  OK   handover/INSTALL.md present
  OK   site weight is stated in the documentation (462 KB found)
  OK   every stated site weight matches the shipped bytes (462 KB)
  OK   no absolute build-machine path in gen.py
  OK   no absolute build-machine path in build_profile.py
  OK   no absolute build-machine path in build_site_pages.py

ALL 148 INTEGRITY CHECKS PASSED

$ node -e require.resolve('playwright'); require.resolve('axe-core'); console.log('browser QA dependencies present')
exit=0
browser QA dependencies present

$ node qa/dark.mjs
exit=0
  ✓ light scheme, toggles pressed, disclosures open: 0 violations across 20 pages
  ✓ dark scheme, toggles pressed, disclosures open: 0 violations across 20 pages

TOTAL: 0

$ node qa/pixels.mjs
exit=0
Sampled 570 text runs against real composited pixels, across 20 pages in both colour schemes.
Tightest 5 (measured / required):
  5.05 / 4.5  light index      SPAN: Immigrant Hall of Honor · Digital exhi
  5.05 / 4.5  dark  index      SPAN: Immigrant Hall of Honor · Digital exhi
  5.10 / 4.5  light 404        A: Home
  5.10 / 4.5  light about      A: Home
  5.10 / 4.5  light accessibility A: Home

  OK   every one of 570 sampled text runs meets its WCAG contrast minimum

$ node qa/states.mjs
exit=0
  ✓ prefers-reduced-motion: nothing animates on any page 
  ✓ print: every collapsed section opens (0 still hidden)
  ✓ print: interface chrome is removed (0 still shown)
  ✓ print: WordPress fragment opens all sections (0 hidden)
  ✓ 320px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 360px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 390px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 430px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 768px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 1280px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 1600px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ keyboard: every one of 30 focus stops shows a visible indicator (0 did not)

ALL 12 STATE CHECKS PASSED

$ node qa/reflow.mjs
exit=0
  ✓ 320px (reflow): all 20 pages reflow with no horizontal scrolling
  ✓ 640px (=200% zoom): all 20 pages reflow with no horizontal scrolling

$ node qa/wp.mjs
exit=0
  ✓ albright: light: axe clean on the fragment 
  ✓ albright: light: no JS errors
  ✓ albright: dark: axe clean on the fragment 
  ✓ albright: dark: no JS errors
  ✓ albright: opening sentence sits ABOVE the photograph
  ✓ albright: credit sits immediately BENEATH the photograph
  ✓ albright: no text overlaid on the photograph 
  ✓ albright: standfirst present
  ✓ albright: exactly 5 sections (got 5)
  ✓ albright: 14 source items (original 10-15 contract)
  ✓ albright: source register is nonempty
  ✓ albright: exactly 5 discussion questions (got 5)
  ✓ albright: exactly 2 activities (got 2)
  ✓ albright: quotation count matches authored optional quotation (got 1)
  ✓ albright: exactly one h1
  ✓ albright: ZERO script elements in the fragment
  ✓ albright: zero external RESOURCES loaded (got 0)
  ✓ albright: 16 evidence links cover the source register
  ✓ albright: original profile retains 10+ evidence links
  ✓ albright: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ albright: theme's Impact heading font does not reach inside (got Georgia)
  ✓ albright: theme's uppercase transform does not reach inside
  ✓ albright: fragment's styles do not leak out to the host
  ✓ albright: all 5 section headers reachable by Tab (reached 10)
  ✓ albright: Enter toggles a section closed
  ✓ albright: Enter toggles it open again
  ✓ albright: no horizontal scrolling at 320px
  ✓ albright: no horizontal scrolling at 360px
  ✓ albright: no horizontal scrolling at 390px
  ✓ albright: no horizontal scrolling at 430px
  ✓ albright: no horizontal scrolling at 768px
  ✓ albright: no horizontal scrolling at 1280px
  ✓ berlin: light: axe clean on the fragment 
  ✓ berlin: light: no JS errors
  ✓ berlin: dark: axe clean on the fragment 
  ✓ berlin: dark: no JS errors
  ✓ berlin: opening sentence sits ABOVE the photograph
  ✓ berlin: credit sits immediately BENEATH the photograph
  ✓ berlin: no text overlaid on the photograph 
  ✓ berlin: standfirst present
  ✓ berlin: exactly 5 sections (got 5)
  ✓ berlin: source register is nonempty
  ✓ berlin: exactly 5 discussion questions (got 5)
  ✓ berlin: exactly 2 activities (got 2)
  ✓ berlin: quotation count matches authored optional quotation (got 1)
  ✓ berlin: exactly one h1
  ✓ berlin: ZERO script elements in the fragment
  ✓ berlin: zero external RESOURCES loaded (got 0)
  ✓ berlin: 7 evidence links cover the source register
  ✓ berlin: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ berlin: theme's Impact heading font does not reach inside (got Georgia)
  ✓ berlin: theme's uppercase transform does not reach inside
  ✓ berlin: fragment's styles do not leak out to the host
  ✓ berlin: all 5 section headers reachable by Tab (reached 15)
  ✓ berlin: Enter toggles a section closed
  ✓ berlin: Enter toggles it open again
  ✓ berlin: no horizontal scrolling at 320px
  ✓ berlin: no horizontal scrolling at 360px
  ✓ berlin: no horizontal scrolling at 390px
  ✓ berlin: no horizontal scrolling at 430px
  ✓ berlin: no horizontal scrolling at 768px
  ✓ berlin: no horizontal scrolling at 1280px
  ✓ cruz: light: axe clean on the fragment 
  ✓ cruz: light: no JS errors
  ✓ cruz: dark: axe clean on the fragment 
  ✓ cruz: dark: no JS errors
  ✓ cruz: opening sentence sits ABOVE the photograph
  ✓ cruz: credit sits immediately BENEATH the photograph
  ✓ cruz: no text overlaid on the photograph 
  ✓ cruz: standfirst present
  ✓ cruz: exactly 5 sections (got 5)
  ✓ cruz: 10 source items (original 10-15 contract)
  ✓ cruz: source register is nonempty
  ✓ cruz: exactly 5 discussion questions (got 5)
  ✓ cruz: exactly 2 activities (got 2)
  ✓ cruz: quotation count matches authored optional quotation (got 1)
  ✓ cruz: exactly one h1
  ✓ cruz: ZERO script elements in the fragment
  ✓ cruz: zero external RESOURCES loaded (got 0)
  ✓ cruz: 12 evidence links cover the source register
  ✓ cruz: original profile retains 10+ evidence links
  ✓ cruz: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ cruz: theme's Impact heading font does not reach inside (got Georgia)
  ✓ cruz: theme's uppercase transform does not reach inside
  ✓ cruz: fragment's styles do not leak out to the host
  ✓ cruz: all 5 section headers reachable by Tab (reached 12)
  ✓ cruz: Enter toggles a section closed
  ✓ cruz: Enter toggles it open again
  ✓ cruz: no horizontal scrolling at 320px
  ✓ cruz: no horizontal scrolling at 360px
  ✓ cruz: no horizontal scrolling at 390px
  ✓ cruz: no horizontal scrolling at 430px
  ✓ cruz: no horizontal scrolling at 768px
  ✓ cruz: no horizontal scrolling at 1280px
  ✓ einstein: light: axe clean on the fragment 
  ✓ einstein: light: no JS errors
  ✓ einstein: dark: axe clean on the fragment 
  ✓ einstein: dark: no JS errors
  ✓ einstein: opening sentence sits ABOVE the photograph
  ✓ einstein: credit sits immediately BENEATH the photograph
  ✓ einstein: no text overlaid on the photograph 
  ✓ einstein: standfirst present
  ✓ einstein: exactly 5 sections (got 5)
  ✓ einstein: source register is nonempty
  ✓ einstein: exactly 5 discussion questions (got 5)
  ✓ einstein: exactly 2 activities (got 2)
  ✓ einstein: quotation count matches authored optional quotation (got 1)
  ✓ einstein: exactly one h1
  ✓ einstein: ZERO script elements in the fragment
  ✓ einstein: zero external RESOURCES loaded (got 0)
  ✓ einstein: 10 evidence links cover the source register
  ✓ einstein: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ einstein: theme's Impact heading font does not reach inside (got Georgia)
  ✓ einstein: theme's uppercase transform does not reach inside
  ✓ einstein: fragment's styles do not leak out to the host
  ✓ einstein: all 5 section headers reachable by Tab (reached 15)
  ✓ einstein: Enter toggles a section closed
  ✓ einstein: Enter toggles it open again
  ✓ einstein: no horizontal scrolling at 320px
  ✓ einstein: no horizontal scrolling at 360px
  ✓ einstein: no horizontal scrolling at 390px
  ✓ einstein: no horizontal scrolling at 430px
  ✓ einstein: no horizontal scrolling at 768px
  ✓ einstein: no horizontal scrolling at 1280px
  ✓ hope: light: axe clean on the fragment 
  ✓ hope: light: no JS errors
  ✓ hope: dark: axe clean on the fragment 
  ✓ hope: dark: no JS errors
  ✓ hope: opening sentence sits ABOVE the photograph
  ✓ hope: credit sits immediately BENEATH the photograph
  ✓ hope: no text overlaid on the photograph 
  ✓ hope: standfirst present
  ✓ hope: exactly 5 sections (got 5)
  ✓ hope: source register is nonempty
  ✓ hope: exactly 5 discussion questions (got 5)
  ✓ hope: exactly 2 activities (got 2)
  ✓ hope: quotation count matches authored optional quotation (got 0)
  ✓ hope: exactly one h1
  ✓ hope: ZERO script elements in the fragment
  ✓ hope: zero external RESOURCES loaded (got 0)
  ✓ hope: 7 evidence links cover the source register
  ✓ hope: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ hope: theme's Impact heading font does not reach inside (got Georgia)
  ✓ hope: theme's uppercase transform does not reach inside
  ✓ hope: fragment's styles do not leak out to the host
  ✓ hope: all 5 section headers reachable by Tab (reached 15)
  ✓ hope: Enter toggles a section closed
  ✓ hope: Enter toggles it open again
  ✓ hope: no horizontal scrolling at 320px
  ✓ hope: no horizontal scrolling at 360px
  ✓ hope: no horizontal scrolling at 390px
  ✓ hope: no horizontal scrolling at 430px
  ✓ hope: no horizontal scrolling at 768px
  ✓ hope: no horizontal scrolling at 1280px
  ✓ lamarr: light: axe clean on the fragment 
  ✓ lamarr: light: no JS errors
  ✓ lamarr: dark: axe clean on the fragment 
  ✓ lamarr: dark: no JS errors
  ✓ lamarr: opening sentence sits ABOVE the photograph
  ✓ lamarr: credit sits immediately BENEATH the photograph
  ✓ lamarr: no text overlaid on the photograph 
  ✓ lamarr: standfirst present
  ✓ lamarr: exactly 5 sections (got 5)
  ✓ lamarr: 11 source items (original 10-15 contract)
  ✓ lamarr: source register is nonempty
  ✓ lamarr: exactly 5 discussion questions (got 5)
  ✓ lamarr: exactly 2 activities (got 2)
  ✓ lamarr: quotation count matches authored optional quotation (got 1)
  ✓ lamarr: exactly one h1
  ✓ lamarr: ZERO script elements in the fragment
  ✓ lamarr: zero external RESOURCES loaded (got 0)
  ✓ lamarr: 13 evidence links cover the source register
  ✓ lamarr: original profile retains 10+ evidence links
  ✓ lamarr: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ lamarr: theme's Impact heading font does not reach inside (got Georgia)
  ✓ lamarr: theme's uppercase transform does not reach inside
  ✓ lamarr: fragment's styles do not leak out to the host
  ✓ lamarr: all 5 section headers reachable by Tab (reached 10)
  ✓ lamarr: Enter toggles a section closed
  ✓ lamarr: Enter toggles it open again
  ✓ lamarr: no horizontal scrolling at 320px
  ✓ lamarr: no horizontal scrolling at 360px
  ✓ lamarr: no horizontal scrolling at 390px
  ✓ lamarr: no horizontal scrolling at 430px
  ✓ lamarr: no horizontal scrolling at 768px
  ✓ lamarr: no horizontal scrolling at 1280px
  ✓ muir: light: axe clean on the fragment 
  ✓ muir: light: no JS errors
  ✓ muir: dark: axe clean on the fragment 
  ✓ muir: dark: no JS errors
  ✓ muir: opening sentence sits ABOVE the photograph
  ✓ muir: credit sits immediately BENEATH the photograph
  ✓ muir: no text overlaid on the photograph 
  ✓ muir: standfirst present
  ✓ muir: exactly 5 sections (got 5)
  ✓ muir: source register is nonempty
  ✓ muir: exactly 5 discussion questions (got 5)
  ✓ muir: exactly 2 activities (got 2)
  ✓ muir: quotation count matches authored optional quotation (got 1)
  ✓ muir: exactly one h1
  ✓ muir: ZERO script elements in the fragment
  ✓ muir: zero external RESOURCES loaded (got 0)
  ✓ muir: 10 evidence links cover the source register
  ✓ muir: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ muir: theme's Impact heading font does not reach inside (got Georgia)
  ✓ muir: theme's uppercase transform does not reach inside
  ✓ muir: fragment's styles do not leak out to the host
  ✓ muir: all 5 section headers reachable by Tab (reached 15)
  ✓ muir: Enter toggles a section closed
  ✓ muir: Enter toggles it open again
  ✓ muir: no horizontal scrolling at 320px
  ✓ muir: no horizontal scrolling at 360px
  ✓ muir: no horizontal scrolling at 390px
  ✓ muir: no horizontal scrolling at 430px
  ✓ muir: no horizontal scrolling at 768px
  ✓ muir: no horizontal scrolling at 1280px
  ✓ naismith: light: axe clean on the fragment 
  ✓ naismith: light: no JS errors
  ✓ naismith: dark: axe clean on the fragment 
  ✓ naismith: dark: no JS errors
  ✓ naismith: opening sentence sits ABOVE the photograph
  ✓ naismith: credit sits immediately BENEATH the photograph
  ✓ naismith: no text overlaid on the photograph 
  ✓ naismith: standfirst present
  ✓ naismith: exactly 5 sections (got 5)
  ✓ naismith: source register is nonempty
  ✓ naismith: exactly 5 discussion questions (got 5)
  ✓ naismith: exactly 2 activities (got 2)
  ✓ naismith: quotation count matches authored optional quotation (got 1)
  ✓ naismith: exactly one h1
  ✓ naismith: ZERO script elements in the fragment
  ✓ naismith: zero external RESOURCES loaded (got 0)
  ✓ naismith: 9 evidence links cover the source register
  ✓ naismith: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ naismith: theme's Impact heading font does not reach inside (got Georgia)
  ✓ naismith: theme's uppercase transform does not reach inside
  ✓ naismith: fragment's styles do not leak out to the host
  ✓ naismith: all 5 section headers reachable by Tab (reached 15)
  ✓ naismith: Enter toggles a section closed
  ✓ naismith: Enter toggles it open again
  ✓ naismith: no horizontal scrolling at 320px
  ✓ naismith: no horizontal scrolling at 360px
  ✓ naismith: no horizontal scrolling at 390px
  ✓ naismith: no horizontal scrolling at 430px
  ✓ naismith: no horizontal scrolling at 768px
  ✓ naismith: no horizontal scrolling at 1280px
  ✓ pei: light: axe clean on the fragment 
  ✓ pei: light: no JS errors
  ✓ pei: dark: axe clean on the fragment 
  ✓ pei: dark: no JS errors
  ✓ pei: opening sentence sits ABOVE the photograph
  ✓ pei: credit sits immediately BENEATH the photograph
  ✓ pei: no text overlaid on the photograph 
  ✓ pei: standfirst present
  ✓ pei: exactly 5 sections (got 5)
  ✓ pei: 13 source items (original 10-15 contract)
  ✓ pei: source register is nonempty
  ✓ pei: exactly 5 discussion questions (got 5)
  ✓ pei: exactly 2 activities (got 2)
  ✓ pei: quotation count matches authored optional quotation (got 1)
  ✓ pei: exactly one h1
  ✓ pei: ZERO script elements in the fragment
  ✓ pei: zero external RESOURCES loaded (got 0)
  ✓ pei: 15 evidence links cover the source register
  ✓ pei: original profile retains 10+ evidence links
  ✓ pei: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ pei: theme's Impact heading font does not reach inside (got Georgia)
  ✓ pei: theme's uppercase transform does not reach inside
  ✓ pei: fragment's styles do not leak out to the host
  ✓ pei: all 5 section headers reachable by Tab (reached 10)
  ✓ pei: Enter toggles a section closed
  ✓ pei: Enter toggles it open again
  ✓ pei: no horizontal scrolling at 320px
  ✓ pei: no horizontal scrolling at 360px
  ✓ pei: no horizontal scrolling at 390px
  ✓ pei: no horizontal scrolling at 430px
  ✓ pei: no horizontal scrolling at 768px
  ✓ pei: no horizontal scrolling at 1280px
  ✓ strauss: light: axe clean on the fragment 
  ✓ strauss: light: no JS errors
  ✓ strauss: dark: axe clean on the fragment 
  ✓ strauss: dark: no JS errors
  ✓ strauss: opening sentence sits ABOVE the photograph
  ✓ strauss: credit sits immediately BENEATH the photograph
  ✓ strauss: no text overlaid on the photograph 
  ✓ strauss: standfirst present
  ✓ strauss: exactly 5 sections (got 5)
  ✓ strauss: source register is nonempty
  ✓ strauss: exactly 5 discussion questions (got 5)
  ✓ strauss: exactly 2 activities (got 2)
  ✓ strauss: quotation count matches authored optional quotation (got 0)
  ✓ strauss: exactly one h1
  ✓ strauss: ZERO script elements in the fragment
  ✓ strauss: zero external RESOURCES loaded (got 0)
  ✓ strauss: 7 evidence links cover the source register
  ✓ strauss: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ strauss: theme's Impact heading font does not reach inside (got Georgia)
  ✓ strauss: theme's uppercase transform does not reach inside
  ✓ strauss: fragment's styles do not leak out to the host
  ✓ strauss: all 5 section headers reachable by Tab (reached 15)
  ✓ strauss: Enter toggles a section closed
  ✓ strauss: Enter toggles it open again
  ✓ strauss: no horizontal scrolling at 320px
  ✓ strauss: no horizontal scrolling at 360px
  ✓ strauss: no horizontal scrolling at 390px
  ✓ strauss: no horizontal scrolling at 430px
  ✓ strauss: no horizontal scrolling at 768px
  ✓ strauss: no horizontal scrolling at 1280px

ALL 308 CHECKS PASSED

$ node qa/nojs.mjs
exit=0
  ✓ phone 375, no JavaScript: all 20 pages fully readable and navigable
  ✓ desktop 1280, no JavaScript: all 20 pages fully readable and navigable

No content is hidden behind JavaScript on any page, at either width.

$ node qa/targets.mjs
exit=0

Every non-inline target on all 20 pages is at least 24x24.

$ node qa/leak.mjs
exit=0
No site-theme rule changes rendering inside the exhibit.

$ node qa/interact.mjs
exit=0

PASS (39)
  ✓ 20 claims rendered (15+ expected)
  ✓ every one of the 20 claims has an evidence drawer
  ✓ 47 evidence items across 20 claims
  ✓ curator findings start closed
  ✓ tally starts at 0
  ✓ sheet starts empty
  ✓ first verdict control is focusable
  ✓ arrow keys move and select within the radio group (got contradicted)
  ✓ recording a verdict opens the curator finding
  ✓ claim marked answered
  ✓ tally incremented to 1
  ✓ agreement reported: "Your finding matches the curator."
  ✓ status line reports agreement
  ✓ finding sheet built
  ✓ citation step hidden before a verdict is recorded
  ✓ citation step appears once a verdict is recorded
  ✓ citation recorded on the finding sheet
  ✓ visitor may reject the curator’s own evidence
  ✓ disagreement recorded without overriding the visitor
  ✓ curator reasoning shown even when you disagree
  ✓ clear resets the tally
  ✓ clear re-closes the curator findings
  ✓ clear empties the sheet
  ✓ no JS errors (none)
  ✓ verdicts register in all 5 case files
  ✓ citations register in all 5 case files (got 5 of 5)
  ✓ tally counts across case files
  ✓ Enter in the search field keeps the filter ("Showing 1 of 10." -> "Showing 1 of 10.")
  ✓ Enter does not reload the page
  ✓ axe clean with ALL drawers open 
  ✓ all targets ≥24×24 
  ✓ no-JS: all 20 claims present
  ✓ no-JS: all 47 evidence items present
  ✓ no-JS: every curator verdict still in the page
  ✓ no-JS: every lesson still readable
  ✓ no-JS: 60 verdict controls (3 per claim) still usable
  ✓ no-JS: 67 citation controls (one per evidence item plus "none") still usable
  ✓ no-JS: the citation step is visible (not gated on script)
  ✓ no-JS: evidence drawer opens natively

ALL 39 CHECKS PASSED

$ node qa/incomplete.mjs
exit=0
axe "incomplete" colour-contrast nodes across 11 pages: 73
  70×  Element's background color could not be determined due to a background gradient
  2×  Element's background color could not be determined due to a pseudo element
  1×  Element content contains only non-text characters

$ node qa/repro.mjs
exit=0
  NOT REPRO  A  no-JS hero paragraph invisible         
               [{"t":"In July 1935 an American vice ","o":"1"},{"t":"I. M. Pei came to America on a","o":"1"}]  (.fade-up elements on page: 0)

  NOT REPRO  B  no-JS mobile nav unreachable           
               nav display=block; menu button is displayed but its only handler is JS

  NOT REPRO  C-E albright profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E berlin profile has script or buttons  
               {"btn":0,"js":0}

  NOT REPRO  C-E cruz profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E einstein profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E hope profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E lamarr profile has script or buttons  
               {"btn":0,"js":0}

  NOT REPRO  C-E muir profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E naismith profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E pei profile has script or buttons     
               {"btn":0,"js":0}

  NOT REPRO  C-E strauss profile has script or buttons 
               {"btn":0,"js":0}

  NOT REPRO  F  citation ignored outside case file 1   
               case file 1 citation registered=true; citations shown after recording two=2 (expected 2)

  NOT REPRO  G  Enter wipes search and filters         
               "Showing 1 of 10."  ->  "Showing 1 of 10."   url/inductees.html

  NOT REPRO  H  hero text column at 320px              
               hero copy column 320px wide; figcaption 320px at x=0

  NOT REPRO  I  loaded photo covers the hero credit    
               topmost element over the credit line: ["FIGCAPTION","FIGURE.anchor","DIV.ihh-profile","MAIN.profile-page"]  (test used a 1px stand-in image, so this measures stacking only)

Reproduced 0 of 16 findings.

$ node qa/profile-factory.mjs
exit=0
  ✓ light: mobile has no horizontal overflow
  ✓ light: generated profile axe clean 
  ✓ light: generated profile has no page errors
  ✓ light: exactly one profile h1
  ✓ light: exactly one profile main landmark
  ✓ light: provenance register is present
  ✓ light: every non-inline summary/link meets 24px target floor 
  ✓ dark: mobile has no horizontal overflow
  ✓ dark: generated profile axe clean 
  ✓ dark: generated profile has no page errors
  ✓ dark: exactly one profile h1
  ✓ dark: exactly one profile main landmark
  ✓ dark: provenance register is present
  ✓ dark: every non-inline summary/link meets 24px target floor 
  ✓ generated profile: no horizontal scroll at 320px
  ✓ generated profile: no horizontal scroll at 360px
  ✓ generated profile: no horizontal scroll at 375px
  ✓ generated profile: no horizontal scroll at 390px
  ✓ generated profile: no horizontal scroll at 412px
  ✓ generated profile: no horizontal scroll at 430px
  ✓ generated profile: no horizontal scroll at 640px
  ✓ generated profile: no horizontal scroll at 768px
  ✓ generated profile: no horizontal scroll at 1024px
  ✓ generated profile: no horizontal scroll at 1280px
  ✓ generated profile: no horizontal scroll at 1440px
  ✓ generated profile has zero scripts
  ✓ generated profile loads zero external src resources
  ✓ generated profile has zero link/iframe/object/embed runtime dependencies
  ✓ generated profile has zero unsafe href schemes
  ✓ generated profile exposes human sign-off status
  ✓ generated profile has five narrative sections
  ✓ generated profile remains substantive with JavaScript disabled
  ✓ generated profile honors reduced motion with no active animation/transition
  ✓ generated profile print layout has no horizontal overflow
  ✓ print exposes all five narrative sections without toggling disclosures

ALL 35 PROFILE FACTORY CHECKS PASSED

```

## pipeline-demo

```text
$ CHROMIUM=/tmp/ihh-chromium python -m pipeline.demo
QA PASS: /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -m pipeline.generic_build --profile-dir profiles/madeleine-albright
QA PASS: node qa/integrity.mjs .
QA PASS: node -e require.resolve('playwright'); require.resolve('axe-core'); console.log('browser QA dependencies present')
QA PASS: node qa/dark.mjs
QA PASS: node qa/pixels.mjs
QA PASS: node qa/states.mjs
QA PASS: node qa/reflow.mjs
QA PASS: node qa/wp.mjs
QA PASS: node qa/nojs.mjs
QA PASS: node qa/targets.mjs
QA PASS: node qa/leak.mjs
QA PASS: node qa/interact.mjs
QA PASS: node qa/incomplete.mjs
QA PASS: node qa/repro.mjs
QA PASS: node qa/profile-factory.mjs
DEMO PIPELINE COMPLETE
STATUS: PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF
claims=15 sources=5 qa_commands=15
```

## pixels

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/pixels.mjs
Sampled 570 text runs against real composited pixels, across 20 pages in both colour schemes.
Tightest 5 (measured / required):
  5.05 / 4.5  light index      SPAN: Immigrant Hall of Honor · Digital exhi
  5.05 / 4.5  dark  index      SPAN: Immigrant Hall of Honor · Digital exhi
  5.10 / 4.5  light 404        A: Home
  5.10 / 4.5  light about      A: Home
  5.10 / 4.5  light accessibility A: Home

  OK   every one of 570 sampled text runs meets its WCAG contrast minimum
```

## preview-history

```text
$ preview-history (see REPORT.md)
4fab8601a2cdd1f474e592da38833b131f71d61c preview: add Naismith & Strauss exhibits; scroll-reveal on exhibit pages
58d06be18f86afa970a01d1a3e3394824b81ab3f preview: add Irving Berlin exhibit; Hope review fix (first civilian); name Tolochin
d791f4e6b092ab80ee88b0d531a196d8f7fbef84 preview: add Bob Hope exhibit; fix unsourced card claims; hedge Einstein portrait date
d0862291e032ada29909d26628fac318ea32edc9 preview: reframe Muir to stand alone; add Einstein exhibit
6f39f894a7bf05814a1c2bbad150c8f138da9a3b preview: John Muir exhibit + homepage hero wall & background
 inductees/berlin/copy-full.md                      | 113 ++++++++
 inductees/berlin/copy.html                         | 212 ++++++++++++++
 inductees/berlin/copy.md                           |  66 +++++
 inductees/berlin/media-manifest.csv                |   6 +
 .../berlin/media/web/berlin-portrait-nywts.jpg     | Bin 0 -> 33514 bytes
 inductees/berlin/preview.html                      | 227 +++++++++++++++
 inductees/einstein/copy-full.md                    | 137 ++++++++++
 inductees/einstein/copy.html                       | 236 ++++++++++++++++
 inductees/einstein/copy.md                         |  66 +++++
 inductees/einstein/media-manifest.csv              |   9 +
 .../media/web/einstein-portrait-turner.jpg         | Bin 0 -> 35413 bytes
 inductees/einstein/preview.html                    | 251 +++++++++++++++++
 inductees/hope/copy-full.md                        | 112 ++++++++
 inductees/hope/copy.html                           | 212 ++++++++++++++
 inductees/hope/copy.md                             |  65 +++++
 inductees/hope/media-manifest.csv                  |   6 +
 inductees/hope/media/web/hope-portrait-nbc.jpg     | Bin 0 -> 27755 bytes
 inductees/hope/preview.html                        | 227 +++++++++++++++
 inductees/muir/copy-full.md                        | 142 ++++++++++
 inductees/muir/copy.html                           | 236 ++++++++++++++++
 inductees/muir/copy.md                             |  71 +++++
 inductees/muir/media-manifest.csv                  |   9 +
 .../muir/media/web/muir-watkins-portrait-c1875.jpg | Bin 0 -> 25556 bytes
 inductees/muir/preview.html                        | 251 +++++++++++++++++
 inductees/naismith/copy-full.md                    | 134 +++++++++
 inductees/naismith/copy.html                       | 228 ++++++++++++++++
 inductees/naismith/copy.md                         |  71 +++++
 inductees/naismith/media-manifest.csv              |   8 +
 inductees/naismith/media/web/naismith-portrait.jpg | Bin 0 -> 45583 bytes
 inductees/naismith/preview.html                    | 243 +++++++++++++++++
 inductees/strauss/copy-full.md                     | 112 ++++++++
 inductees/strauss/copy.html                        | 212 ++++++++++++++
 inductees/strauss/copy.md                          |  65 +++++
 inductees/strauss/media-manifest.csv               |   6 +
 inductees/strauss/media/web/strauss-portrait.jpg   | Bin 0 -> 22220 bytes
 inductees/strauss/preview.html                     | 227 +++++++++++++++
 site/__pycache__/cases.cpython-313.pyc             | Bin 28902 -> 28897 bytes
 site/assets/site.css                               |  50 +++-
 site/assets/site.js                                |  51 ++++
 site/berlin.html                                   | 279 +++++++++++++++++++
 site/einstein.html                                 | 303 +++++++++++++++++++++
 site/hope.html                                     | 279 +++++++++++++++++++
 site/index.html                                    |  11 +-
 site/inductees.html                                |  46 ++--
 site/media/berlin/berlin-portrait-nywts.jpg        | Bin 0 -> 33514 bytes
 site/media/einstein/einstein-portrait-turner.jpg   | Bin 0 -> 35413 bytes
 site/media/hope/hope-portrait-nbc.jpg              | Bin 0 -> 27755 bytes
 site/media/muir/muir-watkins-portrait-c1875.jpg    | Bin 0 -> 25556 bytes
 site/media/naismith/naismith-portrait.jpg          | Bin 0 -> 45583 bytes
 site/media/strauss/strauss-portrait.jpg            | Bin 0 -> 22220 bytes
 site/muir.html                                     | 303 +++++++++++++++++++++
 site/naismith.html                                 | 295 ++++++++++++++++++++
 site/strauss.html                                  | 279 +++++++++++++++++++
 53 files changed, 5830 insertions(+), 26 deletions(-)
```

## profile-factory

```text
$ CHROMIUM=/tmp/ihh-chromium PROFILE_URL=http://127.0.0.1:8741/profiles/madeleine-albright/preview.html node qa/profile-factory.mjs
  ✓ light: mobile has no horizontal overflow
  ✓ light: generated profile axe clean 
  ✓ light: generated profile has no page errors
  ✓ light: exactly one profile h1
  ✓ light: exactly one profile main landmark
  ✓ light: provenance register is present
  ✓ light: every non-inline summary/link meets 24px target floor 
  ✓ dark: mobile has no horizontal overflow
  ✓ dark: generated profile axe clean 
  ✓ dark: generated profile has no page errors
  ✓ dark: exactly one profile h1
  ✓ dark: exactly one profile main landmark
  ✓ dark: provenance register is present
  ✓ dark: every non-inline summary/link meets 24px target floor 
  ✓ generated profile: no horizontal scroll at 320px
  ✓ generated profile: no horizontal scroll at 360px
  ✓ generated profile: no horizontal scroll at 375px
  ✓ generated profile: no horizontal scroll at 390px
  ✓ generated profile: no horizontal scroll at 412px
  ✓ generated profile: no horizontal scroll at 430px
  ✓ generated profile: no horizontal scroll at 640px
  ✓ generated profile: no horizontal scroll at 768px
  ✓ generated profile: no horizontal scroll at 1024px
  ✓ generated profile: no horizontal scroll at 1280px
  ✓ generated profile: no horizontal scroll at 1440px
  ✓ generated profile has zero scripts
  ✓ generated profile loads zero external src resources
  ✓ generated profile has zero link/iframe/object/embed runtime dependencies
  ✓ generated profile has zero unsafe href schemes
  ✓ generated profile exposes human sign-off status
  ✓ generated profile has five narrative sections
  ✓ generated profile remains substantive with JavaScript disabled
  ✓ generated profile honors reduced motion with no active animation/transition
  ✓ generated profile print layout has no horizontal overflow
  ✓ print exposes all five narrative sections without toggling disclosures

ALL 35 PROFILE FACTORY CHECKS PASSED
```

## protected-files

```text
$ protected-files (see REPORT.md)
PASS: no changes to .gitignore, profile copy.md, or profile manifests against preview head
```

## python-tests

```text
$ python -m unittest discover -s tests -v
test_cache_hash_mismatch_is_never_used_as_evidence (test_cache.CacheTests.test_cache_hash_mismatch_is_never_used_as_evidence) ... ok
test_cached_unparsed_bytes_are_reparsed_without_network (test_cache.CacheTests.test_cached_unparsed_bytes_are_reparsed_without_network) ... ok
test_failed_fetch_says_fetch_failed_not_nonexistent (test_cache.CacheTests.test_failed_fetch_says_fetch_failed_not_nonexistent) ... ok
test_missing_cached_body_is_never_treated_as_retrieved_evidence (test_cache.CacheTests.test_missing_cached_body_is_never_treated_as_retrieved_evidence) ... ok
test_private_and_local_urls_are_rejected_before_fetch (test_cache.CacheTests.test_private_and_local_urls_are_rejected_before_fetch) ... ok
test_builder_rejects_nested_or_external_profile_directory (test_generic_build.GenericBuildTests.test_builder_rejects_nested_or_external_profile_directory) ... ok
test_generic_output_has_no_albright_hardcodes_and_keeps_archival_style (test_generic_build.GenericBuildTests.test_generic_output_has_no_albright_hardcodes_and_keeps_archival_style) ... ok
test_media_path_traversal_filename_is_rejected (test_generic_build.GenericBuildTests.test_media_path_traversal_filename_is_rejected) ... ok
test_unsafe_source_href_is_rejected (test_generic_build.GenericBuildTests.test_unsafe_source_href_is_rejected) ... ok
test_http_error_never_echoes_api_key_or_full_provider_body (test_llm.LLMClientTests.test_http_error_never_echoes_api_key_or_full_provider_body) ... ok
test_model_must_be_explicit_key_stays_out_of_payload_and_endpoint_is_fixed (test_llm.LLMClientTests.test_model_must_be_explicit_key_stays_out_of_payload_and_endpoint_is_fixed) ... ok
test_redactor_catches_bearer_and_key_patterns (test_llm.LLMClientTests.test_redactor_catches_bearer_and_key_patterns) ... ok
test_alt_limits (test_media_rights.MediaRightsTests.test_alt_limits) ... ok
test_automated_agent_never_issues_affirmative_legal_determination (test_media_rights.MediaRightsTests.test_automated_agent_never_issues_affirmative_legal_determination) ... ok
test_exact_subject_span_allows_only_conservative_generated_alt (test_media_rights.MediaRightsTests.test_exact_subject_span_allows_only_conservative_generated_alt) ... ok
test_invented_or_unsafe_urls_are_rejected (test_media_rights.MediaRightsTests.test_invented_or_unsafe_urls_are_rejected) ... ok
test_media_filename_path_traversal_is_rejected (test_media_rights.MediaRightsTests.test_media_filename_path_traversal_is_rejected) ... ok
test_retrieved_source_cannot_be_silently_omitted (test_media_rights.MediaRightsTests.test_retrieved_source_cannot_be_silently_omitted) ... ok
test_rights_must_be_exact_source_span (test_media_rights.MediaRightsTests.test_rights_must_be_exact_source_span) ... ok
test_unproven_subject_is_mechanically_downgraded_even_if_model_names_person (test_media_rights.MediaRightsTests.test_unproven_subject_is_mechanically_downgraded_even_if_model_names_person) ... ok
test_visitor_visible_metadata_must_be_retrieved_not_invented (test_media_rights.MediaRightsTests.test_visitor_visible_metadata_must_be_retrieved_not_invented) ... ok
test_rejects_output_outside_or_nested_under_profiles (test_orchestrator.OrchestratorIsolationTests.test_rejects_output_outside_or_nested_under_profiles) ... ok
test_connection_pins_resolved_numeric_address (test_release_boundaries.ReleaseBoundaryTests.test_connection_pins_resolved_numeric_address) ... ok
test_connection_rejects_mixed_public_private_dns_without_connecting (test_release_boundaries.ReleaseBoundaryTests.test_connection_rejects_mixed_public_private_dns_without_connecting) ... ok
test_corrupt_metadata_is_not_evidence_and_never_fetches (test_release_boundaries.ReleaseBoundaryTests.test_corrupt_metadata_is_not_evidence_and_never_fetches) ... ok
test_failed_rerun_invalidates_old_success_on_return_and_exception (test_release_boundaries.ReleaseBoundaryTests.test_failed_rerun_invalidates_old_success_on_return_and_exception) ... ok
test_incomplete_api_response_cannot_pass_even_with_valid_json (test_release_boundaries.ReleaseBoundaryTests.test_incomplete_api_response_cannot_pass_even_with_valid_json) ... ok
test_large_source_refuses_partial_verification_and_rights_review (test_release_boundaries.ReleaseBoundaryTests.test_large_source_refuses_partial_verification_and_rights_review) ... ok
test_private_redirect_is_blocked_before_request_creation (test_release_boundaries.ReleaseBoundaryTests.test_private_redirect_is_blocked_before_request_creation) ... ok
test_windows_ambiguous_filenames_and_url_shapes_are_rejected (test_release_boundaries.ReleaseBoundaryTests.test_windows_ambiguous_filenames_and_url_shapes_are_rejected) ... ok
test_claim_serializes_enum_values (test_schema.SchemaTests.test_claim_serializes_enum_values) ... ok
test_profile_defaults_to_human_signoff (test_schema.SchemaTests.test_profile_defaults_to_human_signoff) ... ok
test_character_and_word_limits_are_both_required (test_verifier_evidence_quality.EvidenceQualityTests.test_character_and_word_limits_are_both_required) ... ok
test_non_substring_still_fails_even_with_long_matching_tokens (test_verifier_evidence_quality.EvidenceQualityTests.test_non_substring_still_fails_even_with_long_matching_tokens) ... ok
test_overlap_is_case_insensitive (test_verifier_evidence_quality.EvidenceQualityTests.test_overlap_is_case_insensitive) ... ok
test_quotation_containment_still_required_after_quality_checks (test_verifier_evidence_quality.EvidenceQualityTests.test_quotation_containment_still_required_after_quality_checks) ... ok
test_supported_claim_with_context_passes_gate (test_verifier_evidence_quality.EvidenceQualityTests.test_supported_claim_with_context_passes_gate) ... ok
test_trivial_span_fabrication_fails_gate (test_verifier_evidence_quality.EvidenceQualityTests.test_trivial_span_fabrication_fails_gate) ... ok
test_unrelated_long_span_and_stopword_overlap_fail (test_verifier_evidence_quality.EvidenceQualityTests.test_unrelated_long_span_and_stopword_overlap_fail) ... ok
test_factual_heading_and_quote_attribution_are_in_verification_stream (test_verifier_gate.VerifierGateTests.test_factual_heading_and_quote_attribution_are_in_verification_stream) ... ok
test_factual_question_cannot_bypass_evidence_by_being_marked_editorial (test_verifier_gate.VerifierGateTests.test_factual_question_cannot_bypass_evidence_by_being_marked_editorial) ... ok
test_fake_exact_span_downgrades_confirmed (test_verifier_gate.VerifierGateTests.test_fake_exact_span_downgrades_confirmed) ... ok
test_lowercase_historical_question_cannot_use_editorial_heuristic (test_verifier_gate.VerifierGateTests.test_lowercase_historical_question_cannot_use_editorial_heuristic) ... ok
test_planted_unsupported_claim_fails_gate (test_verifier_gate.VerifierGateTests.test_planted_unsupported_claim_fails_gate) ... ok
test_remediation_rewrites_rejected_claim_then_reaudits (test_verifier_gate.VerifierGateTests.test_remediation_rewrites_rejected_claim_then_reaudits) ... ok
test_source_prompt_injection_is_explicitly_treated_as_untrusted_data (test_verifier_gate.VerifierGateTests.test_source_prompt_injection_is_explicitly_treated_as_untrusted_data) ... ok
test_status_prefix_cannot_hide_a_historical_claim (test_verifier_gate.VerifierGateTests.test_status_prefix_cannot_hide_a_historical_claim) ... ok
test_supported_claim_passes_with_exact_span (test_verifier_gate.VerifierGateTests.test_supported_claim_passes_with_exact_span) ... ok
test_absent_or_empty_copy_is_not_success (test_web_fallback.WebFallbackTests.test_absent_or_empty_copy_is_not_success) ... ok
test_tracked_copy_without_original (test_web_fallback.WebFallbackTests.test_tracked_copy_without_original) ... ok

----------------------------------------------------------------------
Ran 50 tests in 0.042s

OK
```

## rebuild

```text
$ bash qa/rebuild.sh
OPEN ITEM: berlin/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: einstein/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: hope/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: muir/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: naismith/search-log.csv missing; team lead will supply the actual research log.
OPEN ITEM: strauss/search-log.csv missing; team lead will supply the actual research log.
  OK   site/verify.html regenerates byte-identically
  OK   handover/OPEN-ITEMS.md regenerates byte-identically
  OK   site/albright.html regenerates byte-identically
  OK   handover/albright/copy.html regenerates byte-identically
  OK   handover/albright/copy-full.md regenerates byte-identically
  OK   handover/albright/preview.html regenerates byte-identically
  OK   handover/albright/media-manifest.csv regenerates byte-identically
  OK   inductees/albright/copy.html regenerates byte-identically
  OK   inductees/albright/copy-full.md regenerates byte-identically
  OK   inductees/albright/preview.html regenerates byte-identically
  OK   inductees/albright/media/web/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   site/media/albright/albright-1997-commission-duplicate.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   site/media/albright/albright-1997-swearing-in.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   site/media/albright/albright-1999-truman-library-1.jpg regenerates byte-identically
  OK   inductees/albright/media/web/albright-2016-naturalization.jpg regenerates byte-identically
  OK   handover/albright/media/web/albright-2016-naturalization.jpg regenerates byte-identically
  OK   site/media/albright/albright-2016-naturalization.jpg regenerates byte-identically
  OK   handover/albright/search-log.csv regenerates byte-identically
  OK   site/berlin.html regenerates byte-identically
  OK   handover/berlin/copy.html regenerates byte-identically
  OK   handover/berlin/copy-full.md regenerates byte-identically
  OK   handover/berlin/preview.html regenerates byte-identically
  OK   handover/berlin/media-manifest.csv regenerates byte-identically
  OK   inductees/berlin/copy.html regenerates byte-identically
  OK   inductees/berlin/copy-full.md regenerates byte-identically
  OK   inductees/berlin/preview.html regenerates byte-identically
  OK   inductees/berlin/media/web/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   handover/berlin/media/web/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   site/media/berlin/berlin-portrait-nywts.jpg regenerates byte-identically
  OK   site/cruz.html regenerates byte-identically
  OK   handover/cruz/copy.html regenerates byte-identically
  OK   handover/cruz/copy-full.md regenerates byte-identically
  OK   handover/cruz/preview.html regenerates byte-identically
  OK   handover/cruz/media-manifest.csv regenerates byte-identically
  OK   inductees/cruz/copy.html regenerates byte-identically
  OK   inductees/cruz/copy-full.md regenerates byte-identically
  OK   inductees/cruz/preview.html regenerates byte-identically
  OK   inductees/cruz/media/web/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   handover/cruz/media/web/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   site/media/cruz/cruz-1970s-dress-arteaga-nmaahc.jpg regenerates byte-identically
  OK   inductees/cruz/media/web/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   handover/cruz/media/web/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   site/media/cruz/cruz-2024-quarter-reverse-usmint.jpg regenerates byte-identically
  OK   handover/cruz/search-log.csv regenerates byte-identically
  OK   site/einstein.html regenerates byte-identically
  OK   handover/einstein/copy.html regenerates byte-identically
  OK   handover/einstein/copy-full.md regenerates byte-identically
  OK   handover/einstein/preview.html regenerates byte-identically
  OK   handover/einstein/media-manifest.csv regenerates byte-identically
  OK   inductees/einstein/copy.html regenerates byte-identically
  OK   inductees/einstein/copy-full.md regenerates byte-identically
  OK   inductees/einstein/preview.html regenerates byte-identically
  OK   inductees/einstein/media/web/einstein-portrait-turner.jpg regenerates byte-identically
  OK   handover/einstein/media/web/einstein-portrait-turner.jpg regenerates byte-identically
  OK   site/media/einstein/einstein-portrait-turner.jpg regenerates byte-identically
  OK   site/hope.html regenerates byte-identically
  OK   handover/hope/copy.html regenerates byte-identically
  OK   handover/hope/copy-full.md regenerates byte-identically
  OK   handover/hope/preview.html regenerates byte-identically
  OK   handover/hope/media-manifest.csv regenerates byte-identically
  OK   inductees/hope/copy.html regenerates byte-identically
  OK   inductees/hope/copy-full.md regenerates byte-identically
  OK   inductees/hope/preview.html regenerates byte-identically
  OK   inductees/hope/media/web/hope-portrait-nbc.jpg regenerates byte-identically
  OK   handover/hope/media/web/hope-portrait-nbc.jpg regenerates byte-identically
  OK   site/media/hope/hope-portrait-nbc.jpg regenerates byte-identically
  OK   site/lamarr.html regenerates byte-identically
  OK   handover/lamarr/copy.html regenerates byte-identically
  OK   handover/lamarr/copy-full.md regenerates byte-identically
  OK   handover/lamarr/preview.html regenerates byte-identically
  OK   handover/lamarr/media-manifest.csv regenerates byte-identically
  OK   inductees/lamarr/copy.html regenerates byte-identically
  OK   inductees/lamarr/copy-full.md regenerates byte-identically
  OK   inductees/lamarr/preview.html regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1939-portrait-lat.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1942-patent-2292387-sheet1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1942-patent-2292387-text-p1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1945-property-claim-p1.jpg regenerates byte-identically
  OK   inductees/lamarr/media/web/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   handover/lamarr/media/web/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   site/media/lamarr/lamarr-1945-property-claim-p2.jpg regenerates byte-identically
  OK   handover/lamarr/search-log.csv regenerates byte-identically
  OK   site/muir.html regenerates byte-identically
  OK   handover/muir/copy.html regenerates byte-identically
  OK   handover/muir/copy-full.md regenerates byte-identically
  OK   handover/muir/preview.html regenerates byte-identically
  OK   handover/muir/media-manifest.csv regenerates byte-identically
  OK   inductees/muir/copy.html regenerates byte-identically
  OK   inductees/muir/copy-full.md regenerates byte-identically
  OK   inductees/muir/preview.html regenerates byte-identically
  OK   inductees/muir/media/web/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   handover/muir/media/web/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   site/media/muir/muir-watkins-portrait-c1875.jpg regenerates byte-identically
  OK   site/naismith.html regenerates byte-identically
  OK   handover/naismith/copy.html regenerates byte-identically
  OK   handover/naismith/copy-full.md regenerates byte-identically
  OK   handover/naismith/preview.html regenerates byte-identically
  OK   handover/naismith/media-manifest.csv regenerates byte-identically
  OK   inductees/naismith/copy.html regenerates byte-identically
  OK   inductees/naismith/copy-full.md regenerates byte-identically
  OK   inductees/naismith/preview.html regenerates byte-identically
  OK   inductees/naismith/media/web/naismith-portrait.jpg regenerates byte-identically
  OK   handover/naismith/media/web/naismith-portrait.jpg regenerates byte-identically
  OK   site/media/naismith/naismith-portrait.jpg regenerates byte-identically
  OK   site/pei.html regenerates byte-identically
  OK   handover/pei/copy.html regenerates byte-identically
  OK   handover/pei/copy-full.md regenerates byte-identically
  OK   handover/pei/preview.html regenerates byte-identically
  OK   handover/pei/media-manifest.csv regenerates byte-identically
  OK   inductees/pei/copy.html regenerates byte-identically
  OK   inductees/pei/copy-full.md regenerates byte-identically
  OK   inductees/pei/preview.html regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-penn-admission-radiogram.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-san-francisco-arrival-statement.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   site/media/pei/pei-1935-shanghai-consulate-precis.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   site/media/pei/pei-1946-change-of-status-p1.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   site/media/pei/pei-1947-harvard-dean-letter.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   site/media/pei/pei-1947-permanent-residence-calais.jpg regenerates byte-identically
  OK   inductees/pei/media/web/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   handover/pei/media/web/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   site/media/pei/pei-1978-east-building-highsmith.jpg regenerates byte-identically
  OK   handover/pei/search-log.csv regenerates byte-identically
  OK   site/strauss.html regenerates byte-identically
  OK   handover/strauss/copy.html regenerates byte-identically
  OK   handover/strauss/copy-full.md regenerates byte-identically
  OK   handover/strauss/preview.html regenerates byte-identically
  OK   handover/strauss/media-manifest.csv regenerates byte-identically
  OK   inductees/strauss/copy.html regenerates byte-identically
  OK   inductees/strauss/copy-full.md regenerates byte-identically
  OK   inductees/strauss/preview.html regenerates byte-identically
  OK   inductees/strauss/media/web/strauss-portrait.jpg regenerates byte-identically
  OK   handover/strauss/media/web/strauss-portrait.jpg regenerates byte-identically
  OK   site/media/strauss/strauss-portrait.jpg regenerates byte-identically

ALL GENERATED FILES MATCH THEIR SOURCES
```

## reflow

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/reflow.mjs
  ✓ 320px (reflow): all 20 pages reflow with no horizontal scrolling
  ✓ 640px (=200% zoom): all 20 pages reflow with no horizontal scrolling
```

## repro

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/repro.mjs
  NOT REPRO  A  no-JS hero paragraph invisible         
               [{"t":"In July 1935 an American vice ","o":"1"},{"t":"I. M. Pei came to America on a","o":"1"}]  (.fade-up elements on page: 0)

  NOT REPRO  B  no-JS mobile nav unreachable           
               nav display=block; menu button is displayed but its only handler is JS

  NOT REPRO  C-E albright profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E berlin profile has script or buttons  
               {"btn":0,"js":0}

  NOT REPRO  C-E cruz profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E einstein profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E hope profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E lamarr profile has script or buttons  
               {"btn":0,"js":0}

  NOT REPRO  C-E muir profile has script or buttons    
               {"btn":0,"js":0}

  NOT REPRO  C-E naismith profile has script or buttons
               {"btn":0,"js":0}

  NOT REPRO  C-E pei profile has script or buttons     
               {"btn":0,"js":0}

  NOT REPRO  C-E strauss profile has script or buttons 
               {"btn":0,"js":0}

  NOT REPRO  F  citation ignored outside case file 1   
               case file 1 citation registered=true; citations shown after recording two=2 (expected 2)

  NOT REPRO  G  Enter wipes search and filters         
               "Showing 1 of 10."  ->  "Showing 1 of 10."   url/inductees.html

  NOT REPRO  H  hero text column at 320px              
               hero copy column 320px wide; figcaption 320px at x=0

  NOT REPRO  I  loaded photo covers the hero credit    
               topmost element over the credit line: ["FIGCAPTION","FIGURE.anchor","DIV.ihh-profile","MAIN.profile-page"]  (test used a 1px stand-in image, so this measures stacking only)

Reproduced 0 of 16 findings.
```

## secrets

```text
$ python qa/secrets.py
PASS key-like secret scan across all tracked text files (including Markdown)
```

## states

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/states.mjs
  ✓ prefers-reduced-motion: nothing animates on any page 
  ✓ print: every collapsed section opens (0 still hidden)
  ✓ print: interface chrome is removed (0 still shown)
  ✓ print: WordPress fragment opens all sections (0 hidden)
  ✓ 320px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 360px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 390px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 430px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 768px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 1280px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ 1600px: no horizontal scrolling on 20 pages + the WP fragment 
  ✓ keyboard: every one of 30 focus stops shows a visible indicator (0 did not)

ALL 12 STATE CHECKS PASSED
```

## targets

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/targets.mjs

Every non-inline target on all 20 pages is at least 24x24.
```

## wp

```text
$ CHROMIUM=/tmp/ihh-chromium node qa/wp.mjs
  ✓ albright: light: axe clean on the fragment 
  ✓ albright: light: no JS errors
  ✓ albright: dark: axe clean on the fragment 
  ✓ albright: dark: no JS errors
  ✓ albright: opening sentence sits ABOVE the photograph
  ✓ albright: credit sits immediately BENEATH the photograph
  ✓ albright: no text overlaid on the photograph 
  ✓ albright: standfirst present
  ✓ albright: exactly 5 sections (got 5)
  ✓ albright: 14 source items (original 10-15 contract)
  ✓ albright: source register is nonempty
  ✓ albright: exactly 5 discussion questions (got 5)
  ✓ albright: exactly 2 activities (got 2)
  ✓ albright: quotation count matches authored optional quotation (got 1)
  ✓ albright: exactly one h1
  ✓ albright: ZERO script elements in the fragment
  ✓ albright: zero external RESOURCES loaded (got 0)
  ✓ albright: 16 evidence links cover the source register
  ✓ albright: original profile retains 10+ evidence links
  ✓ albright: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ albright: theme's Impact heading font does not reach inside (got Georgia)
  ✓ albright: theme's uppercase transform does not reach inside
  ✓ albright: fragment's styles do not leak out to the host
  ✓ albright: all 5 section headers reachable by Tab (reached 10)
  ✓ albright: Enter toggles a section closed
  ✓ albright: Enter toggles it open again
  ✓ albright: no horizontal scrolling at 320px
  ✓ albright: no horizontal scrolling at 360px
  ✓ albright: no horizontal scrolling at 390px
  ✓ albright: no horizontal scrolling at 430px
  ✓ albright: no horizontal scrolling at 768px
  ✓ albright: no horizontal scrolling at 1280px
  ✓ berlin: light: axe clean on the fragment 
  ✓ berlin: light: no JS errors
  ✓ berlin: dark: axe clean on the fragment 
  ✓ berlin: dark: no JS errors
  ✓ berlin: opening sentence sits ABOVE the photograph
  ✓ berlin: credit sits immediately BENEATH the photograph
  ✓ berlin: no text overlaid on the photograph 
  ✓ berlin: standfirst present
  ✓ berlin: exactly 5 sections (got 5)
  ✓ berlin: source register is nonempty
  ✓ berlin: exactly 5 discussion questions (got 5)
  ✓ berlin: exactly 2 activities (got 2)
  ✓ berlin: quotation count matches authored optional quotation (got 1)
  ✓ berlin: exactly one h1
  ✓ berlin: ZERO script elements in the fragment
  ✓ berlin: zero external RESOURCES loaded (got 0)
  ✓ berlin: 7 evidence links cover the source register
  ✓ berlin: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ berlin: theme's Impact heading font does not reach inside (got Georgia)
  ✓ berlin: theme's uppercase transform does not reach inside
  ✓ berlin: fragment's styles do not leak out to the host
  ✓ berlin: all 5 section headers reachable by Tab (reached 15)
  ✓ berlin: Enter toggles a section closed
  ✓ berlin: Enter toggles it open again
  ✓ berlin: no horizontal scrolling at 320px
  ✓ berlin: no horizontal scrolling at 360px
  ✓ berlin: no horizontal scrolling at 390px
  ✓ berlin: no horizontal scrolling at 430px
  ✓ berlin: no horizontal scrolling at 768px
  ✓ berlin: no horizontal scrolling at 1280px
  ✓ cruz: light: axe clean on the fragment 
  ✓ cruz: light: no JS errors
  ✓ cruz: dark: axe clean on the fragment 
  ✓ cruz: dark: no JS errors
  ✓ cruz: opening sentence sits ABOVE the photograph
  ✓ cruz: credit sits immediately BENEATH the photograph
  ✓ cruz: no text overlaid on the photograph 
  ✓ cruz: standfirst present
  ✓ cruz: exactly 5 sections (got 5)
  ✓ cruz: 10 source items (original 10-15 contract)
  ✓ cruz: source register is nonempty
  ✓ cruz: exactly 5 discussion questions (got 5)
  ✓ cruz: exactly 2 activities (got 2)
  ✓ cruz: quotation count matches authored optional quotation (got 1)
  ✓ cruz: exactly one h1
  ✓ cruz: ZERO script elements in the fragment
  ✓ cruz: zero external RESOURCES loaded (got 0)
  ✓ cruz: 12 evidence links cover the source register
  ✓ cruz: original profile retains 10+ evidence links
  ✓ cruz: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ cruz: theme's Impact heading font does not reach inside (got Georgia)
  ✓ cruz: theme's uppercase transform does not reach inside
  ✓ cruz: fragment's styles do not leak out to the host
  ✓ cruz: all 5 section headers reachable by Tab (reached 12)
  ✓ cruz: Enter toggles a section closed
  ✓ cruz: Enter toggles it open again
  ✓ cruz: no horizontal scrolling at 320px
  ✓ cruz: no horizontal scrolling at 360px
  ✓ cruz: no horizontal scrolling at 390px
  ✓ cruz: no horizontal scrolling at 430px
  ✓ cruz: no horizontal scrolling at 768px
  ✓ cruz: no horizontal scrolling at 1280px
  ✓ einstein: light: axe clean on the fragment 
  ✓ einstein: light: no JS errors
  ✓ einstein: dark: axe clean on the fragment 
  ✓ einstein: dark: no JS errors
  ✓ einstein: opening sentence sits ABOVE the photograph
  ✓ einstein: credit sits immediately BENEATH the photograph
  ✓ einstein: no text overlaid on the photograph 
  ✓ einstein: standfirst present
  ✓ einstein: exactly 5 sections (got 5)
  ✓ einstein: source register is nonempty
  ✓ einstein: exactly 5 discussion questions (got 5)
  ✓ einstein: exactly 2 activities (got 2)
  ✓ einstein: quotation count matches authored optional quotation (got 1)
  ✓ einstein: exactly one h1
  ✓ einstein: ZERO script elements in the fragment
  ✓ einstein: zero external RESOURCES loaded (got 0)
  ✓ einstein: 10 evidence links cover the source register
  ✓ einstein: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ einstein: theme's Impact heading font does not reach inside (got Georgia)
  ✓ einstein: theme's uppercase transform does not reach inside
  ✓ einstein: fragment's styles do not leak out to the host
  ✓ einstein: all 5 section headers reachable by Tab (reached 15)
  ✓ einstein: Enter toggles a section closed
  ✓ einstein: Enter toggles it open again
  ✓ einstein: no horizontal scrolling at 320px
  ✓ einstein: no horizontal scrolling at 360px
  ✓ einstein: no horizontal scrolling at 390px
  ✓ einstein: no horizontal scrolling at 430px
  ✓ einstein: no horizontal scrolling at 768px
  ✓ einstein: no horizontal scrolling at 1280px
  ✓ hope: light: axe clean on the fragment 
  ✓ hope: light: no JS errors
  ✓ hope: dark: axe clean on the fragment 
  ✓ hope: dark: no JS errors
  ✓ hope: opening sentence sits ABOVE the photograph
  ✓ hope: credit sits immediately BENEATH the photograph
  ✓ hope: no text overlaid on the photograph 
  ✓ hope: standfirst present
  ✓ hope: exactly 5 sections (got 5)
  ✓ hope: source register is nonempty
  ✓ hope: exactly 5 discussion questions (got 5)
  ✓ hope: exactly 2 activities (got 2)
  ✓ hope: quotation count matches authored optional quotation (got 0)
  ✓ hope: exactly one h1
  ✓ hope: ZERO script elements in the fragment
  ✓ hope: zero external RESOURCES loaded (got 0)
  ✓ hope: 7 evidence links cover the source register
  ✓ hope: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ hope: theme's Impact heading font does not reach inside (got Georgia)
  ✓ hope: theme's uppercase transform does not reach inside
  ✓ hope: fragment's styles do not leak out to the host
  ✓ hope: all 5 section headers reachable by Tab (reached 15)
  ✓ hope: Enter toggles a section closed
  ✓ hope: Enter toggles it open again
  ✓ hope: no horizontal scrolling at 320px
  ✓ hope: no horizontal scrolling at 360px
  ✓ hope: no horizontal scrolling at 390px
  ✓ hope: no horizontal scrolling at 430px
  ✓ hope: no horizontal scrolling at 768px
  ✓ hope: no horizontal scrolling at 1280px
  ✓ lamarr: light: axe clean on the fragment 
  ✓ lamarr: light: no JS errors
  ✓ lamarr: dark: axe clean on the fragment 
  ✓ lamarr: dark: no JS errors
  ✓ lamarr: opening sentence sits ABOVE the photograph
  ✓ lamarr: credit sits immediately BENEATH the photograph
  ✓ lamarr: no text overlaid on the photograph 
  ✓ lamarr: standfirst present
  ✓ lamarr: exactly 5 sections (got 5)
  ✓ lamarr: 11 source items (original 10-15 contract)
  ✓ lamarr: source register is nonempty
  ✓ lamarr: exactly 5 discussion questions (got 5)
  ✓ lamarr: exactly 2 activities (got 2)
  ✓ lamarr: quotation count matches authored optional quotation (got 1)
  ✓ lamarr: exactly one h1
  ✓ lamarr: ZERO script elements in the fragment
  ✓ lamarr: zero external RESOURCES loaded (got 0)
  ✓ lamarr: 13 evidence links cover the source register
  ✓ lamarr: original profile retains 10+ evidence links
  ✓ lamarr: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ lamarr: theme's Impact heading font does not reach inside (got Georgia)
  ✓ lamarr: theme's uppercase transform does not reach inside
  ✓ lamarr: fragment's styles do not leak out to the host
  ✓ lamarr: all 5 section headers reachable by Tab (reached 10)
  ✓ lamarr: Enter toggles a section closed
  ✓ lamarr: Enter toggles it open again
  ✓ lamarr: no horizontal scrolling at 320px
  ✓ lamarr: no horizontal scrolling at 360px
  ✓ lamarr: no horizontal scrolling at 390px
  ✓ lamarr: no horizontal scrolling at 430px
  ✓ lamarr: no horizontal scrolling at 768px
  ✓ lamarr: no horizontal scrolling at 1280px
  ✓ muir: light: axe clean on the fragment 
  ✓ muir: light: no JS errors
  ✓ muir: dark: axe clean on the fragment 
  ✓ muir: dark: no JS errors
  ✓ muir: opening sentence sits ABOVE the photograph
  ✓ muir: credit sits immediately BENEATH the photograph
  ✓ muir: no text overlaid on the photograph 
  ✓ muir: standfirst present
  ✓ muir: exactly 5 sections (got 5)
  ✓ muir: source register is nonempty
  ✓ muir: exactly 5 discussion questions (got 5)
  ✓ muir: exactly 2 activities (got 2)
  ✓ muir: quotation count matches authored optional quotation (got 1)
  ✓ muir: exactly one h1
  ✓ muir: ZERO script elements in the fragment
  ✓ muir: zero external RESOURCES loaded (got 0)
  ✓ muir: 10 evidence links cover the source register
  ✓ muir: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ muir: theme's Impact heading font does not reach inside (got Georgia)
  ✓ muir: theme's uppercase transform does not reach inside
  ✓ muir: fragment's styles do not leak out to the host
  ✓ muir: all 5 section headers reachable by Tab (reached 15)
  ✓ muir: Enter toggles a section closed
  ✓ muir: Enter toggles it open again
  ✓ muir: no horizontal scrolling at 320px
  ✓ muir: no horizontal scrolling at 360px
  ✓ muir: no horizontal scrolling at 390px
  ✓ muir: no horizontal scrolling at 430px
  ✓ muir: no horizontal scrolling at 768px
  ✓ muir: no horizontal scrolling at 1280px
  ✓ naismith: light: axe clean on the fragment 
  ✓ naismith: light: no JS errors
  ✓ naismith: dark: axe clean on the fragment 
  ✓ naismith: dark: no JS errors
  ✓ naismith: opening sentence sits ABOVE the photograph
  ✓ naismith: credit sits immediately BENEATH the photograph
  ✓ naismith: no text overlaid on the photograph 
  ✓ naismith: standfirst present
  ✓ naismith: exactly 5 sections (got 5)
  ✓ naismith: source register is nonempty
  ✓ naismith: exactly 5 discussion questions (got 5)
  ✓ naismith: exactly 2 activities (got 2)
  ✓ naismith: quotation count matches authored optional quotation (got 1)
  ✓ naismith: exactly one h1
  ✓ naismith: ZERO script elements in the fragment
  ✓ naismith: zero external RESOURCES loaded (got 0)
  ✓ naismith: 9 evidence links cover the source register
  ✓ naismith: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ naismith: theme's Impact heading font does not reach inside (got Georgia)
  ✓ naismith: theme's uppercase transform does not reach inside
  ✓ naismith: fragment's styles do not leak out to the host
  ✓ naismith: all 5 section headers reachable by Tab (reached 15)
  ✓ naismith: Enter toggles a section closed
  ✓ naismith: Enter toggles it open again
  ✓ naismith: no horizontal scrolling at 320px
  ✓ naismith: no horizontal scrolling at 360px
  ✓ naismith: no horizontal scrolling at 390px
  ✓ naismith: no horizontal scrolling at 430px
  ✓ naismith: no horizontal scrolling at 768px
  ✓ naismith: no horizontal scrolling at 1280px
  ✓ pei: light: axe clean on the fragment 
  ✓ pei: light: no JS errors
  ✓ pei: dark: axe clean on the fragment 
  ✓ pei: dark: no JS errors
  ✓ pei: opening sentence sits ABOVE the photograph
  ✓ pei: credit sits immediately BENEATH the photograph
  ✓ pei: no text overlaid on the photograph 
  ✓ pei: standfirst present
  ✓ pei: exactly 5 sections (got 5)
  ✓ pei: 13 source items (original 10-15 contract)
  ✓ pei: source register is nonempty
  ✓ pei: exactly 5 discussion questions (got 5)
  ✓ pei: exactly 2 activities (got 2)
  ✓ pei: quotation count matches authored optional quotation (got 1)
  ✓ pei: exactly one h1
  ✓ pei: ZERO script elements in the fragment
  ✓ pei: zero external RESOURCES loaded (got 0)
  ✓ pei: 15 evidence links cover the source register
  ✓ pei: original profile retains 10+ evidence links
  ✓ pei: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ pei: theme's Impact heading font does not reach inside (got Georgia)
  ✓ pei: theme's uppercase transform does not reach inside
  ✓ pei: fragment's styles do not leak out to the host
  ✓ pei: all 5 section headers reachable by Tab (reached 10)
  ✓ pei: Enter toggles a section closed
  ✓ pei: Enter toggles it open again
  ✓ pei: no horizontal scrolling at 320px
  ✓ pei: no horizontal scrolling at 360px
  ✓ pei: no horizontal scrolling at 390px
  ✓ pei: no horizontal scrolling at 430px
  ✓ pei: no horizontal scrolling at 768px
  ✓ pei: no horizontal scrolling at 1280px
  ✓ strauss: light: axe clean on the fragment 
  ✓ strauss: light: no JS errors
  ✓ strauss: dark: axe clean on the fragment 
  ✓ strauss: dark: no JS errors
  ✓ strauss: opening sentence sits ABOVE the photograph
  ✓ strauss: credit sits immediately BENEATH the photograph
  ✓ strauss: no text overlaid on the photograph 
  ✓ strauss: standfirst present
  ✓ strauss: exactly 5 sections (got 5)
  ✓ strauss: source register is nonempty
  ✓ strauss: exactly 5 discussion questions (got 5)
  ✓ strauss: exactly 2 activities (got 2)
  ✓ strauss: quotation count matches authored optional quotation (got 0)
  ✓ strauss: exactly one h1
  ✓ strauss: ZERO script elements in the fragment
  ✓ strauss: zero external RESOURCES loaded (got 0)
  ✓ strauss: 7 evidence links cover the source register
  ✓ strauss: byline placeholders are visibly marked for the volunteer (got 2)
  ✓ strauss: theme's Impact heading font does not reach inside (got Georgia)
  ✓ strauss: theme's uppercase transform does not reach inside
  ✓ strauss: fragment's styles do not leak out to the host
  ✓ strauss: all 5 section headers reachable by Tab (reached 15)
  ✓ strauss: Enter toggles a section closed
  ✓ strauss: Enter toggles it open again
  ✓ strauss: no horizontal scrolling at 320px
  ✓ strauss: no horizontal scrolling at 360px
  ✓ strauss: no horizontal scrolling at 390px
  ✓ strauss: no horizontal scrolling at 430px
  ✓ strauss: no horizontal scrolling at 768px
  ✓ strauss: no horizontal scrolling at 1280px

ALL 308 CHECKS PASSED
```

## zip-reproducibility

```text
$ zip-reproducibility (see REPORT.md)
handover/IHH-inductee-profiles.zip: OK
```

