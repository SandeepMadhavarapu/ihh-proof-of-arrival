# Immigrant Hall of Honor — rebuild

Eleven pages. 271 KB. No framework, no build step, no third-party request, no tracking.
Open `index.html` in any browser. There is nothing to install.

## The pages

| File | What it is |
|---|---|
| `index.html` | Home |
| `verify.html` | **The Verification Desk** — the interactive exhibit. 5 case files, 20 claims, 47 named sources (30 of them linked) |
| `method.html` | How this was built, what we refused to build for IHH and why, and how it maps to the brief |
| `inductees.html` | Browsable index — filter by region, decade and field; search |
| `albright.html` | The worked profile, with provenance panels and a rights register on the page |
| `share.html` | Story submission, with one consent regime instead of two contradictory ones |
| `rights.html` | Rights and reuse policy — the page IHH does not currently have |
| `accessibility.html` · `privacy.html` · `about.html` · `404.html` | |

## The documents

- **`FINDINGS.md`** — the audit of the live site, the interactive, the refusal, and the limits.
- **`TESTS-RUN.md`** — what was tested, with results, what has *not* been tested, and the nine
  defects an independent audit found after this site passed its own suite.
- **`qa/`** — the test harnesses in `../qa/`, with a note on what each one caught.
- **`../albright-wp/media-manifest.csv`** — every image: source, rights statement word for word, credit line, alt
  text, and whether we recommend using it. Six image files still need downloading; the URLs are here.

## Adding a sixth case file

`cases.py` holds the data; `gen.py` renders `verify.html` from it. A case file is a list of
claims, each with its evidence, a verdict and the reasoning. No code, no design work, no
developer. Run `python3 gen.py`.

If IHH would rather not run a script, the generated HTML is plain and repetitive enough to copy
a claim block and edit it by hand.

## What is deliberately unfinished

Three `slot` blocks are marked in the markup — the capital campaign facts, the leadership roster
and the analytics disclosure. **We will not invent an EIN, a fundraising goal or a board list.**
Nine of the ten inductee profiles are unwritten. Six image files are not downloaded.
