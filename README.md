# Immigrant Hall of Honor: four inductee profiles

Content for the Immigrant Hall of Honor (IHH), Challenge+X Fall 2026. The brief asks for:
the **types** of content that would make the inductee pages more engaging; **four inductees**
to research; a **documented search**; the **best content** selected; and everything in a
**format IHH can transfer** to its site.

**The deliverable is `handover/`.** It holds one ready-to-paste WordPress profile for each of
Madeleine Albright, Hedy Lamarr, I. M. Pei and Celia Cruz, with images, a rights register,
and a log of how every item was found. Start at `handover/INSTALL.md`.

**Positioning: supplement/pilot, not replacement.** The board assessment recommends taking
specific ideas now (option c), with a controlled WordPress pilot toward option b. Nothing here
replaces the museum's website. See [POSITIONING.md](POSITIONING.md), [ROADMAP.md](ROADMAP.md)
and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## What is in here

| Path | What it is |
|---|---|
| **`handover/`** | **The deliverable.** One folder per inductee (`copy.html` to paste, `preview.html`, `copy-full.md`, `media/web/`, `media-manifest.csv`, `search-log.csv`), plus `INSTALL.md`, `OPEN-ITEMS.md` and a zip of the lot. Generated; do not edit by hand. |
| `inductees/<name>/` | The sources of each profile: `copy.md` (the text), `media-manifest.csv` (every source and image, rights word for word), `search-log.csv`, full-resolution originals in `media/`, saved source documents in `sources/`. **Edit here.** |
| `templates/` | For the next inductee: `copy-template.md`, `media-manifest.csv`, `search-log.csv`, `where-to-search.md`, `rights-guide.md`, `profile.css`. |
| `tools/` | `build_profile.py` (copy.md + manifest → WordPress block), `build_site_pages.py` (→ demo site pages), `package_handover.sh`, `open_items.py`. |
| `site/` | The optional demonstration site, including the Verification Desk exhibit and the four profiles in the site's design. |
| `ledger/`, `site-src/FINDINGS.md` | The earlier audit of the live IHH site (factual errors found on its inductee pages). **Share privately and kindly.** |
| `qa/` | Browser and static test harnesses, including `profile-factory.mjs`. |
| `pipeline/` | **Profile Factory** (Sandeep): a build-time tool that turns an inductee name and seed source URLs into an evidence-gated draft profile under `profiles/<slug>/`. See `pipeline/README.md`. |
| `profiles/` | Profile Factory outputs only. Each stays **REQUIRES HUMAN SIGN-OFF**; its Albright demo is not a substitute for `inductees/albright/`. |
| `tests/` | Offline Python tests for the Profile Factory's gates; no API key or network needed. |

## The four profiles, and the document at the heart of each

| Inductee | Anchor | Key primary source found |
|---|---|---|
| Madeleine Albright | 2016 naturalization ceremony photo, National Archives | Her full 1998 speech to new citizens, recovered from the State Department's archived site: "in America, but not of America" |
| Hedy Lamarr | Her 1942 patent drawing, signed "Hedy Kiesler Markey" | A 1945 letter in the National Archives: her lawyer, on behalf of "a British subject" in Beverly Hills, asks the U.S. Army to protect her father's Austrian oil fields from the Red Army |
| I. M. Pei | 1935 Shanghai visa form with his photograph, age 18 | His complete 139-page immigration file: twelve years on student visas, then a trip to Canada to re-enter as a permanent resident |
| Celia Cruz | Her sequin stage dress, Smithsonian NMAAHC (CC0) | President Clinton's 1994 National Medal of Arts remarks; Congress.gov proof that the "Congressional Gold Medal" on many websites never passed |

## What a person still has to do

`handover/OPEN-ITEMS.md` lists every item that needs a human with a browser or a phone: a few
rights statements on sites that block automated tools, and records that need a login
(passenger lists) or a request (naturalization files). **Every search log was run by an AI
assistant and needs a team member to spot-check it** before it is presented as the team's work.

The demo sitemap uses `https://example.invalid/` deliberately: it is a non-production
deployment placeholder, not a set of working museum links. Before deployment, replace every
placeholder with approved production URLs or omit the sitemap until configured.

## Running it

```sh
python3 -m http.server 8741                      # from this directory
#   -> http://127.0.0.1:8741/handover/pei/preview.html   (any inductee)
cd site && python3 -m http.server 8731
#   -> http://127.0.0.1:8731/index.html

# after editing inductees/<name>/copy.md or its manifest:
bash tools/package_handover.sh                   # rebuilds the profiles and handover/
python3 tools/build_site_pages.py                # refreshes the demo site pages

# tests (needs: npm i playwright axe-core, and Chrome)
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
python3 -m http.server 8731 --directory site &  python3 -m http.server 8741 &
node qa/integrity.mjs .
for t in wp states dark nojs interact repro targets reflow leak; do node qa/$t.mjs || echo "FAILED: $t"; done
bash qa/rebuild.sh                               # generated files match their sources

# Profile Factory
python3 -m unittest discover -s tests -v         # offline unit tests
python3 -m pipeline.demo                         # deterministic demo, no API key or network
node qa/profile-factory.mjs                      # QA of the generated demo profile
```

## Profile Factory publication boundary

The Profile Factory is intentionally stricter than a content generator. Its verifier audits
visitor-facing factual copy against retrieved source text, requires exact evidence spans, and
hard-fails unsupported material. The rights stage separately prevents unverified rights grants
and image subjects. Build-time source/API activity never ships into the visitor page.

Even after every machine gate passes, the maximum automated state is
**PIPELINE VERIFIED — REQUIRES HUMAN SIGN-OFF.** A person still needs to re-open live sources,
review rights, fact-check the profile, inspect any images, and approve museum publication.

## Decisions worth knowing

- **No AI-generated voices or video of inductees**, though the brief lists it. The brief also
  asks that all content be reliable and verifiable. The reasoning is in `site/method.html`.
- **Uncertainty is stated, not smoothed.** Celia Cruz's naturalization date is unknown and the
  page says so. Disputed dates (Albright's 1998 ceremony on the 10th, the statement on the 11th)
  are explained.
- **Every image was looked at before it was described.** Alt text is at most 15 words.

## What is deliberately not finished

Six of the ten inductee profiles are unwritten; this package delivers four, each still needing
a named person's editorial sign-off (the byline placeholder) before publication. The Profile
Factory's deterministic demo does not count as another profile. No screen-reader user has
tested any of this, no volunteer has run the WordPress handoff in the museum's real site, and
no permission letter has been sent to any institution. `site-src/TESTS-RUN.md` lists what was and
was not tested.

The demo sitemap uses `https://example.invalid/` deliberately: it is a non-production
placeholder. Replace it with approved production URLs, or omit the sitemap, before deployment.
