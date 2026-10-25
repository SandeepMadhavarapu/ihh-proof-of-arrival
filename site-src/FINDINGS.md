# immigranthallofhonor.org — audit and rebuild
**2 October 2026. Prepared for Challenge+X Fall 2026, IHH use case.**

27 pages read. All ten inductee profiles. Technical measurements taken in a real browser
against the live site. Everything below is quoted from the site or measured, not inferred.

A note on tone: this is a small volunteer non-profit doing something worth doing, and the
privacy policy is genuinely good. The findings are blunt because precision is more useful
than politeness, not because the work is contemptible.

---

## 1. The errors to fix today, and one we got wrong ourselves

Each is verified against an authoritative source, re-opened during this repair pass. **Row 6b is a correction to this document, not to IHH.**

| # | Page | What it says | What is true |
|---|---|---|---|
| 1 | Celia Cruz | `Awarded the Congressional Gold Medal (2005)` | **The bill never became law.** H.R. 149 (109th Congress), the *Congressional Tribute to Celia Cruz Act*, was introduced 4 Jan 2005 and referred to subcommittee 23 Feb 2005. No further action. She appears nowhere in the CRS list of Gold Medal recipients. |
| 2 | John Muir | `Helped establish … Grand Canyon (1908) National Park` | Grand Canyon became a **monument** in 1908 and a **park in 1919**. Muir died in 1914. NPS's own article on the Grand Canyon and the Antiquities Act does not mention him. |
| 3 | John Muir | `Yosemite (1898)` | Yosemite was established **1890**. The same sentence dates Sequoia correctly to 1890. |
| 4 | John Muir | `The John Muir Trust was formed in England` | It is **Scottish** — registered office Pitlochry, charity no. SC002061. On a page about a Scot. |
| 5 | Albert Einstein | `immigrated to Princeton, N.J., in 1932` (twice) | **1933.** The Institute for Advanced Study records his appointment as 9/1933. |
| 6 | Albert Einstein | `Polytechnische Schule (1911)` | **1900.** ETH Zurich holds the leaving certificate and dates it *Abgangszeugnis, 28.07.1900*. (The Nobel biography says 1901 — the year he gained Swiss citizenship. Either way, not 1911.) |
| 6b | Albert Einstein | `Ph.D … (1906)` | **No error. IHH is right and we were wrong.** The University of Zurich states the doctorate was conferred in January 1906. An earlier version of this audit 'corrected' it to 1905 on the authority of the Nobel biography. Three events get flattened here: dissertation completed 30 April 1905, faculty approval 27 July 1905, conferral 15 January 1906. |
| 7 | I. M. Pei | `the East Wing of the National Art Gallery (1983)` | **East Building** of the **National Gallery of Art**, opened **1978**. Three errors in one phrase. |
| 8 | Bob Hope | `Won an Academy Award 5 times (1941, 1945, 1953, 1960, 1966)` | The Academy's own lists confirm **three**: Honorary Award 1952, Jean Hersholt Humanitarian Award 1959, Honorary Award 1965. Two further special honours are widely reported but **we could not confirm them at the Academy**. The page's years are ceremony years, not award years. None of these is a competitive Oscar — though note we could not run the database query that would *prove* he was never nominated, and we no longer claim it as proven. |

Plus internal contradictions: Cruz's page says `more than 70 albums` in prose and `Produced 70 songs` in the list. Hope's page gives immigration as `Ellis Island, 1908` in the field and `immigrated to Cleveland, Ohio, in 1920` in the prose — 1920 is his *naturalisation*. Levi Strauss's own achievements list includes `In 2023, Levi Strauss company reported revenue of $6.179 billion`; he died in 1902.

**And the tell:** `Information sources: Britannica, Biography, Grammys` appears **byte-identical on the John Muir page and the Celia Cruz page.** The Grammys reference was copy-pasted onto a Scottish naturalist.

---

## 2. WITHDRAWN — the copyright criticism, and why we are retracting it

**This section previously led the document.** It said IHH ran two contradictory copyright
regimes on its story forms — one taking the copyright outright, one taking a non-exclusive
licence — and advised opening any conversation with it.

**It is no longer true, and we are withdrawing it.** On re-reading all four live intake forms,
three of them now carry the same clause:

> *"I retain ownership of my copyright and grant the Project a non-exclusive, royalty-free
> license to reproduce, publish, display, distribute, and otherwise use my story or interview,
> in whole or in part, for historical, educational, archival, museum, outreach, promotional,
> fundraising and research purposes."*

An explicit string check for the old *"donate and convey … all rights, title, and interest"*
wording returns **not present**. The privacy policy matches the licence framing. **IHH fixed
this.** Republishing the criticism would have been a false accusation, and this is exactly the
failure mode the rest of this document is about.

**What survives, at its true weight.** The second-generation form takes no position on
copyright at all, and asks the submitter to confirm they have a relative's permission to share
that relative's story. That confirmation is not verifiable by anyone, and the story belongs to
somebody who is not filling in the form. That is worth raising. It is not a headline.

**The nomination form defect does stand.** `/nominate/` still asks *"Do you have any images of
the nominee you can provide?"* with Yes/No/Maybe, then marks **both** the image upload **and**
the "I own the complete publishing rights" checkbox **required**. A nominator answering "No"
still cannot submit. For any historical figure — the premise of a Hall of Honor — no nominator
owns such rights.

**Also still true:** no rights or reproduction policy page exists; `/accessibility/` returns
404 and no accessibility statement is linked anywhere; there is no site search.

*Re-read 3 October 2026 through an automated fetch. Byte-level HTML was not available, so
confirm the exact punctuation at the form before quoting it.*

---

## 3. What a browser actually measures

Live homepage, real browser, 2 October 2026:

| | immigranthallofhonor.org | This rebuild |
|---|---|---|
| Page weight | **2,869 KB** (homepage alone) | **521 KB** of HTML, CSS, scripts and text across twenty-one pages; portrait and archival image files additional |
| HTTP requests | 56 | 3 per page |
| `<h1>` elements | **0** | 1 on every page |
| Heading sequence | `H6 > H6 > H6 > H6 > H6 > H6 > H3 > H2` | `H1 > H2 > H3` |
| Images with filename alt text | **8 of 20** — `400x525 hedy lamarr`, `1000 AdobeStock 461051688` | 0 |
| Images with no alt at all | 2 | 0 |
| **Third-party hosts** | **12** | **0** |
| axe-core WCAG 2.2 AA violations | not run against live site | **0 across 11 pages** |
| CSS files / scripts | 21 / 18 | 1 / 1 |

**Zero of the pages audited has an `<h1>`** — not the homepage, not one of the ten inductee profiles. No page declares its own topic to a screen reader or a search engine.

### The twelve third parties

`googletagmanager.com` · `google-analytics.com` · **`googleads.g.doubleclick.net`** · **`ad.doubleclick.net`** · **`match.adsrvr.org`** (The Trade Desk) · **`connect.facebook.net`** · **`facebook.com`** · `cdn.feathr.co` · `polo.feathr.co` · `marco.feathr.co` · `fonts.googleapis.com` · `google.com`

**Four advertising networks and a Facebook pixel, on a site asking immigrants to submit personal family histories.** Some contributors are recent arrivals. Some have family whose position is not secure. The privacy policy is thorough and names Feathr, GA and GTM — it does **not** name DoubleClick, The Trade Desk or Facebook.

This is the finding to lead with. It is not a design opinion; it is a list of hosts the browser contacted.

---

## 4. Structural problems

**Four different primary navigations**, depending on which page you are on. The same destinations carry different labels — `TELL YOUR STORY` / `SHARE A STORY`, `LEADERSHIP` / `BOARD OF DIRECTORS` / `ABOUT US`. **And one of them is broken:** on `/tell-your-story/`, the nav item `MISSION AND VISION` points to `/what-to-expect/`, which returns **404**.

**Two leadership pages that contradict each other.** `/leadership/` lists seven people; `/board-of-directors/` lists four. Three different people are titled "Founder". Most seriously, `/leadership/` records the founder as `SARA PUIG LAAS (1930-2026)` while `/board-of-directors/` still describes her in the present tense.

**The best content on the site is unreachable.** `/europe/`, `/the-americas/`, `/asia/`, `/mexico/`, `/cuba/` are substantial regional hubs that connect famous inductees to community stories — exactly the cross-cutting browse a museum needs. They appear in the sitemap and are **linked from no page found.**

**The inductee index carries no information.** Ten names, ten portraits, and the line `Select a profile image below…`. No taglines, no countries, no dates, no fields. Seven of ten inductees have no one-line summary anywhere outside their own page. Nothing can be sorted or filtered.

**No search anywhere on the site.**

**Three URL hierarchies for the same class of content:** inductees at `/inductees/inductee-<name>/`, leadership at `/leadership/<name>/`, but Founding Voices stories at the **root** — `/sumrin-kalia/`, `/fannie-faigen/`. Sumrin Kalia has two pages.

**Other verified defects:** `Immigration Hall of Honor` (wrong org name) in the first sentence of `/nominate/` · `Grammrely character counter` · the story limit is `7,000 characters` in the prose and `10,000` in the field · `IMBd` · `Education: n/a` published on three pages · `RANIER` and `SEQUIOA` as headings · a headline reading `Oscar Johanson Builds a Life in Sweden's Second City` above a story set in **Chicago** · the same person as `Rafaela Prieto Ochoa` in the URL and `Rafaela Prieto Núñez` in the body · `Día de Los Muertos` spelled three ways on one page · concatenated dates throughout `/founding-voices/`: `July 19, 2026September 25, 2026`.

**Upload limit: 3 MB.** Below a single photo from a modern phone, for an organisation whose purpose is preservation.

**Missing entirely:** rights and reproduction policy · accessibility statement · site search · press kit · educator resources · EIN · mailing address · any museum project page (no site, timeline, cost, opening date or renderings, for an organisation whose headline is "we're building a museum").

---

## 5. What this rebuild does differently

**Twenty-one pages. 521 KB of HTML, CSS, scripts and text; portrait and archival image files additional. Zero third-party requests. Zero axe violations. One H1 per page.**

1. **Every claim sourced, every image credited** — the Albright profile carries 14 source items — 6 catalogued archival photographs with each institution's rights statement reproduced word for word, and 8 text sources — plus 4 lines of imagery considered and **turned down with the reason given**, and 2 records the National Archives Catalog does not describe at item level, named rather than hidden.
2. **A rights and reuse policy** — the page they do not have, and the one a museum is judged on.
3. **An accessibility statement** that says what is *not* finished.
4. **One consent regime**, the non-exclusive licence, with a credit choice and an honest limit on withdrawal.
5. **A browsable index** — filter by region, decade and field; search across everything. Built to answer the question their index cannot.
6. **No tracking.** Stated on the privacy page as a deliberate choice, with the reason.
7. **One navigation**, one leadership page, no dead links.
8. **Works with JavaScript off.** Filtering and search are enhancements.

### Deliberately left empty
Three `slot` blocks marked in the build: the capital campaign facts, the leadership roster, and the analytics disclosure. **We will not invent an EIN, a fundraising goal, or a board list.** Those need someone at IHH who knows the answers.

---

## 6. The Verification Desk — the interactive

The brief asks for content that engages visitors, "especially young people." Every obvious
answer to that — an AI persona of a dead inductee, a 3D gallery, a quiz, a migration map — is
either saturated or disqualifying, and three of them are things the sponsor has no building,
no estate consent, and no staff to maintain.

So the exhibit does the opposite of what engagement normally means. Instead of asking the
visitor to trust the museum more, it hands them the tools and asks them to trust it less.

**You examine a claim. You open the evidence. You record a finding. Then you say which piece
of evidence settled it** — or that none of it convinced you, which is a recordable answer.

| | |
|---|---|
| Case files | **5** — Bob Hope, Albert Einstein, John Muir, Madeleine Albright, Celia Cruz. The brief asks for at least four |
| Claims | **20** |
| Published on immigranthallofhonor.org today | **14** |
| Of those, did not survive checking | **10** |
| Named pieces of evidence | **47** (30 of them linked) |
| Timer | none |
| Score | none |
| Verdicts that can be changed, forever | all of them |

Each claim teaches something different, and that is the point of the selection:

- **Bob Hope** — "Won an Academy Award 5 times." He received Academy *honours*, not five
  competitive Oscars. The Academy's own lists confirm **three** (two Honorary Awards and the Jean
  Hersholt Humanitarian Award); two more are widely reported but we could **not** confirm them. We
  also believe he was never nominated in a competitive category — but that is a negative we cannot
  prove, so we record it as unverified, not as fact. *A number can be correct and the claim around
  it still false.*
- **Albert Einstein** — the page dates the ETH diploma to 1911; the issuing school's own record
  puts it at **1900**. Its Ph.D. date of **1906**, which an earlier version of this audit wrongly
  "corrected" to 1905, is **right**: the University of Zurich conferred the doctorate in January
  1906. *Check the correction as hard as the claim — this one was wrong.*
- **John Muir** — credited with helping establish a national park that came into existence five
  years after he died. *Check the date against the person's lifespan.*
- **Madeleine Albright** — citizenship in 1957: confirmed as to the year, and no month, no
  court, no certificate, no digitised document anywhere. *"Confirmed" and "documented" are
  different words.*
- **Celia Cruz** — "Awarded the Congressional Gold Medal (2005)." H.R. 149 died in subcommittee.
  *A bill introduced is not an award conferred.*

**Why it survives the obvious attacks.** It is not a quiz: no score, no timer, no enforced right
answer, and the curator's reasoning appears whether you agreed or not. It is not a demo: a new
case file is a list of claims and a list of sources, so IHH can add one without a developer.
And it is not fragile: no framework, no build step, no API key, no account, nothing that can
expire or start charging.

**On building it from the sponsor's own errors.** The exhibit says out loud that these are the
errors every museum has, that three of them are copy-paste slips, and that the museums with the
most authority are the ones that publish their own corrections. It also says that the case files
can be rebuilt from any source at all if IHH would rather not publish its own errata — the
format does not depend on it.

---

## 7. What we refused to build, and why

Slide 5 of the brief invites **"AI generated video and audio of or about inductees."** We
declined. The full argument is on the site's method page; the short version:

1. **Slide 3 of the same brief forbids it** — "All content should be reliable and verifiable."
   A generated sentence has no source. That is not a limitation to engineer around; it is what
   generation is.
2. **The field already ran this experiment in public.** Khan Academy's AI Harriet Tubman, July
   2023: *Washington Post* testing found it failed basic fact checks, and Khan Academy's defence
   was that the bot "is not intended to function as a historical record of events." That
   sentence saves an ed-tech product and destroys a museum.
3. **Five of the ten inductees died within living memory** — Lamarr 2000, Hope 2003, Cruz 2003,
   Pei 2019, Albright 2022. New York Civil Rights Law §50-f runs forty years past death;
   Tennessee's ELVIS Act was enacted in 2024 for synthesised voice specifically.
4. **It is what everyone else will build.** Across three museum-hackathon project galleries, the
   AI historical-figure persona is the most common entry there is.

There is a version that works, and it needs consent from the estate, a visible label on every
synthesised second, and a published policy — not a model. We will draft the policy.

---

## 8. An independent audit found nine defects after this passed its own tests

An outside reviewer ran their own Playwright and axe-core harness against the exact
package shipped as v3, published SHA-256 hashes for every file, and found **nine
defects.** All twenty-one files match byte-for-byte, so they tested what we shipped.

**All nine reproduced on the first attempt. All nine are fixed. All nine are now
regression tests.** Two of them falsified claims made in writing — a paragraph that was
invisible without JavaScript on a page whose handoff note said "delete the JavaScript and
every word still works," and a credit line that a real photograph covered completely on a
site whose headline is that every image carries a visible credit.

The reason the suite missed them is worth more than the fixes. It was not weak, it was
**narrow**: it tested case file 1, with JavaScript on, in the light scheme, at rest.
Every one of the nine lives outside that happy path — in case files 2–5, with JavaScript
off, in dark mode, or in a pressed state. The suite now sweeps all five case files, both
colour schemes, both JavaScript states, two widths, and presses every toggle before it
measures.

One challenge did **not** turn out to be a defect: axe reported dozens of contrast nodes
as "incomplete," which is a fair objection to any "zero violations" claim. Those are
caused by this site's own paper-texture gradient. Rather than assert the token values,
`qa/pixels.mjs` screenshots all eleven pages in both schemes, measures contrast from the
**actual composited pixels**, and asserts zero failures (it exits nonzero otherwise). The
latest run: 339 text runs, zero failures, tightest margin 5.11:1 against a 4.5 threshold.

`TESTS-RUN.md` has the full account. The honest headline is not "it passes." It is
**"it passed, somebody else found nine things, and here is what changed."**

---

## 9. The theme: "Broadside"

A museum site that argues for the authority of the archival record should look like it
belongs to one. The theme is set as a nineteenth-century printed broadside.

**What it is made of.** Aged rag paper, foxing blooms, laid lines and a plate vignette —
all of it drawn by the browser from CSS gradients. **There is not one image file in the
stylesheet**, so the entire texture costs nothing to download. A masthead with an engraved
seal, a thick-thin rule, and the navigation set as letterspaced small capitals divided by
printers' lozenges. A three-line drop cap. Oldstyle figures throughout (`font-variant-numeric`),
lining figures only where numbers are data. Engraved diamonds seated on the rules between
sections. Letterpress buttons that sit down 2px when pressed. Catalogue cards with a pressed
corner. The arrivals timeline set as a surveyor's scale. A dark mode that reads as lamplight
rather than an inverted screen.

**The typefaces are local.** The stack prefers Hoefler Text, Baskerville, Bookman Old Style
and Palatino, falling back through Georgia to the system serif. **There is no `@font-face`
rule and no font request**, because the no-third-party claim on the privacy page has to be
literally true — including for fonts. The trade is that the page looks best on macOS and
Windows, which ship those faces, and plainer on a device that ships none. That is the right
side of the trade for an organisation collecting immigrant family histories.

**It did not cost accessibility.** Every colour pair was computed, not eyeballed: body ink
14.4:1, muted 5.6:1, accent 7.2:1, tag text on the deeper stock 5.3:1, control borders 3.7:1
against the WCAG 1.4.11 minimum of 3. axe-core reports **zero violations across all eleven
pages** with the `best-practice` ruleset enabled on top of WCAG 2.2 AA. The masthead is
deliberately not sticky — a fixed bar is a modern convention, and SC 2.4.11 Focus Not Obscured
is easier to honour without one.

---

## 10. Honest limits

- The site is a **demonstration**, not a migration. Moving it into WordPress is a separate job.
- **The forms are not wired to a server.** Markup and consent language only.
- **The Albright profile needs six image files downloaded** from NARA and the National Museum of American Diplomacy. The proxy here blocks `.gov` binaries; every URL is in `media-manifest.csv`.
- **Nine of ten inductee profiles are not written.** The index lists all ten with verified arrival facts; only Albright is complete.
- axe-core is automated testing. It catches perhaps a third of real accessibility problems. **No screen-reader user has tested this**, and the accessibility page says so. What *was* run, with results, is in `TESTS-RUN.md` — including one hypothesis that was tested and turned out to be wrong.
- The factual corrections in §1 are sourced to institutions named inline. They should be re-checked before anyone tells IHH their site is wrong.
- Some findings are marked *appears to be* in the detailed audit rather than verified — the Naismith KU tenure dates, Albright's Order of the White Lion year, Pei's Medal of Freedom year. Those need a second pass.

---

## 11. What to do with this

**Do not open with the error list.** Nobody enjoys being handed a list of their own mistakes
by students.

**Do not open with the copyright finding either** — it is withdrawn, and an earlier version of
this document was wrong to lead with it. If you have already shown that slide to anyone,
correct it before you show it again.

Open with the **nomination form that cannot be submitted**. It is live, it is costing them
contributions today, and fixing it costs nothing. Then the **twelve third-party hosts**,
because that one is about their contributors rather than about them.

Then show the work, and let the 2,869 KB against this package's weight do its own talking.

**And say this out loud:** of the twenty claims on the Verification Desk, two of our own six claims failed. One of them is a correction we made to IHH that was itself wrong. A team
that shows you its own retractions is telling you something about how it checked everything
else.
