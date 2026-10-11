# Tests run — with results

Everything below was executed in a real headless Chromium against the built site served
over HTTP. The scripts are in `qa/`. **The last section lists what still has not been
tested, and by whom it needs to be.**

---

## An independent audit found nine defects this suite had passed

Before reading the rest of this file, read this. An outside reviewer ran their own
Playwright and axe-core harness against the exact ZIP shipped as v3 — they published
SHA-256 hashes, and all 21 files match byte-for-byte. They found **nine defects.**

**All nine reproduced on the first attempt. All nine are fixed. All nine are now
regression tests in `qa/repro.mjs`.**

| # | Defect | Why it mattered |
|---|---|---|
| 1 | The Albright standfirst had `opacity: 0` until JavaScript added a class | **Falsified a claim made in writing.** The handoff file said "delete the JavaScript and every word still works." It did not. |
| 2 | With no JavaScript on a phone, the nav was `display:none` and the only way to open it was a JS handler | The site was unnavigable without script on mobile |
| 3 | A pressed toggle in dark mode: white on the light accent, **2.33:1** | I had computed exactly this risk for `.btn` and solved it with a token — then missed two hardcoded copies |
| 4 | Space on the modal's "Close" button advanced the slideshow instead of closing | Keyboard users could not close the modal the normal way |
| 5 | Shift+Tab from the modal's opening focus left the modal entirely | The focus trap only wrapped from the first and last buttons; focus started on neither |
| 6 | Citations recorded in case files 2–5 never reached the finding sheet | The listener was bound to the *first* case file's parent section |
| 7 | Enter in the search box submitted the form, reloaded the page and wiped every filter | The single most natural keystroke in a search field |
| 8 | At 320px the hero text was squeezed into a **125px** column | The hero was a flex row; the credit caption sat beside the standfirst |
| 9 | A real photograph covered the credit line entirely | The caption was stacked beneath the absolutely-positioned image. **"Every image carries a visible credit" is a headline claim of this project** |

### Why my own tests missed all nine

This is the useful part. The suite was not weak — it was **narrow**, in four specific ways:

- **It tested case file 1.** The citation listener worked there and nowhere else.
- **It tested with JavaScript on**, except for one page. The `opacity: 0` and the dead
  mobile nav were both invisible to it.
- **It tested the light scheme.** Both contrast failures only exist in dark mode.
- **It tested resting state.** Both contrast failures only exist in a *pressed* state,
  and defect 9 only exists once an image actually loads.

Every one of those is a happy path. The suite now sweeps all five case files, both
colour schemes, both JS states, two viewport widths, and presses every toggle before
measuring.

### One thing the audit flagged that turned out not to be a defect

axe reports a few dozen colour-contrast nodes as **"incomplete"** — it cannot compute
them, because this site's aged-paper background is a CSS gradient. The exact number is
non-deterministic run to run (observed around 33); `qa/incomplete.mjs` prints it and the
breakdown each time. That is a fair challenge to any "zero violations" claim.

So rather than trust the declared tokens, `qa/pixels.mjs` screenshots all eleven pages in
both colour schemes, reads the **actual composited pixels** behind every text run, finds
the real background colour and computes the WCAG ratio — and it **asserts**: it exits
nonzero if any run falls short. Run it yourself. The latest run samples **339 text runs,
zero failures, tightest margin 5.11:1** against a 4.5 threshold. (It caught a genuine
2.51:1 failure on a filename chip the first time it ran at full coverage; that was fixed,
which is the point of a test that can fail.)

*(An earlier sampler reported 12 phantom failures — it sampled outside elements that carry
their own background. The method was corrected; a measurement you have not sanity-checked
is not evidence.)*

---

## The suite, and what each script caught

### Automated accessibility — RUN, PASSES
axe-core 4.x, rulesets `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` **and
`best-practice`**, across all 11 pages, in **both colour schemes**, with every
`<details>` forced open **and every `aria-pressed` toggle clicked**.

**Result: 0 violations.** One `<h1>` per page, unbroken heading ladder.

Earlier rounds of this test found and fixed: two `<main>` landmarks on one page with a
duplicate `id`; an H1→H3 skip; a tag colour at 4.43:1; and the two dark-mode 2.33:1
buttons above.

### No JavaScript — RUN, PASSES
All 11 pages, at 375px and 1280px: no text content at `opacity:0`, `visibility:hidden`
or `display:none`, and the navigation reachable. One element is legitimately hidden —
the caption describing the evidence layer, a feature that only exists with script. It
carries `data-js-only` so the test can tell deliberate from accidental.

### Behaviour — RUN, 40 CHECKS PASS
Keyboard-only path through the Verification Desk; arrow keys within the radio group;
verdicts and citations across **all five** case files; disagreement preserved rather
than corrected; "none of the evidence convinced me" recordable; Clear resets and
returns focus; Enter in the search field filters without reloading; Space on the
modal's Close button closes it; Shift+Tab stays inside the modal. Zero JS errors.

With JavaScript disabled: all 20 claims, 47 evidence items, 20 curator verdicts and 20
lessons readable; 60 verdict controls and 67 citation controls still usable. These counts are
derived by the test from the rendered page, not hardcoded — a stale literal here is exactly what
failed when the case files were rewritten.

### Target size — SC 2.5.8 — RUN, PASSES
Every `a`, `button`, `summary`, `input`, `select`, `textarea` on all 11 pages, with the
"inline in a sentence" exception applied programmatically. **Every non-inline target is
at least 24×24 CSS px.** 132 failed initially.

### Reflow and resize — SC 1.4.10, SC 1.4.4 — RUN, PASSES
No horizontal scrolling at **320px** or at **640px** (equivalent to 200% zoom), on any
page, with every disclosure open.

This test found a caption overflowing at 320px. The first hypothesis — that the missing
image was stretching its alt text — was **tested with a placeholder and proved wrong.**
The real cause: `overflow-wrap: break-word` does not reduce a box's min-content width,
so an unbreakable archive identifier set the caption's width. `anywhere` does.

### Stylesheet scope — RUN, PASSES
The exhibit page carries its own complete stylesheet scoped under `.ihh`; the site theme
is unscoped. `qa/leak.mjs` diffs computed styles inside the exhibit with the theme
enabled and disabled.

It found **18 element classes** being restyled by the theme — most visibly, the theme's
`.hero` rule was centring the entire exhibit, because the exhibit's anchor is
`<figure class="anchor hero">`. Fixed by scoping the theme's rules to `section.hero` and
the desk's drawers to `.cl`, plus an explicit scope boundary in the exhibit. **Now zero.**

### Page weight — MEASURED
**271 KB for the entire 11-page site**, against **2,869 KB for the current IHH homepage
alone.** 3 requests per page. Zero third-party hosts.

---

## NOT run — and these matter more than the ones above

| | |
|---|---|
| **A screen reader, used by somebody who uses one** | Automated tools catch perhaps a third of real accessibility problems. Nothing here has been heard. |
| **Readers aged 15–19** | The design rests on a study of what teenagers *said they wanted*. Nobody has watched one use this. |
| **The handoff test** | Give the folder to somebody at IHH who did not build it and does not write code. Time them. Answer nothing. |
| **Rights re-verification** | Every `stable_url` in the media manifest re-opened by a person and compared word for word. |
| **Independent fact check** | Two people, separately, tracing every factual sentence to a source. Untraceable sentences get deleted, not softened. |
| **Lighthouse on real hosting** | Measured locally only. No 4G LCP figure. |
| **The six image files** | Still not downloaded. The hero is a labelled gap until they are. |
| **The next independent audit** | Several waves of independent checking have run against this package. The closure ledger records what each contributed: 9 from the evidence ZIP, then 18, 15, 12 and 9 across four acceptance-review rounds, then 3 from a final verification sweep. Every wave found at least one publication blocker in work that had just passed this full suite, and for four rounds running the blocker was on the same hand-maintained page (`albright.html`). There is no reason to assume the next audit finds none. |

If you are presenting this work: the tested block is tested and you may say so. The
block above is not, and you may not. And the honest headline is not "it passes" — it is
**"it passed, somebody else found nine things, and here is what changed."**
