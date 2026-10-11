# Immigrant Hall of Honor — repaired package

**The required deliverable is `albright-wp/`.** It is one finished Madeleine Albright
profile that a non-technical volunteer can paste into WordPress. Start at
`albright-wp/INSTALL.md`.

**`site/` is the optional standalone demonstration site.** It is not the deliverable and
nothing depends on it. It exists because it holds the audit of the live IHH website and an
interactive exhibit built from that audit.

---

## What is in here

| Path | What it is |
|---|---|
| **`albright-wp/`** | **The deliverable.** `copy.html` (paste this), `copy.md` (editorial text only), `copy-full.md` (**the complete page as Markdown** - use this one if Custom HTML blocks are unavailable), `INSTALL.md` (20-minute volunteer guide), `media-manifest.csv` (item-level rights register), `media/` (empty — see below), `build.py`, `verify-media.py`, `preview.html` |
| `site/` | The optional 11-page site, including the Verification Desk |
| `ledger/` | **`CLOSURE-LEDGER.md` / `.json` / `.csv`** — 116 findings with reproduction, root cause, fix and evidence, plus the raw evidence of what could not be done |
| `qa/` | 12 browser/static harnesses plus `rebuild.sh`. Run them; they are the evidence |

## Three things to know before you use any of it

**1. There are no image files.** Six archival photographs are specified at item level in
`albright-wp/media-manifest.csv` with their stable URLs. The machine that built this package
is refused by `catalog.archives.gov` and `diplomacy.state.gov` at its network's egress proxy
(HTTP 403 on CONNECT. `ledger/fetch-attempts.txt` is the authoritative record: five attempted URLs, all returning 000. `ledger/proxy-denial.txt` describes how the proxy refuses these hosts and warns that its own rolling raw log may have rotated past the archival entries — so fetch-attempts.txt, not the raw log, is the evidence.) Run
`albright-wp/media/fetch-media.sh` from any ordinary network, then
`python3 albright-wp/verify-media.py` to check what you got.

**2. One document central to this story has never been opened by anyone who worked on it.**
The 1998 State Department press statement about Albright's oath renewal is unreachable from
here on every route including web archives. Earlier versions of this work quoted it at length
anyway. They should not have. The profile now says so on its face, and uses a wire report of
the same ceremony instead. Its date is also unresolved — filename and page title say 10
November 1998, almost every citation says 11 November. The page shows the conflict.

**3. `IHH-V3-DEEP-AUDIT.md` was not supplied.** It was named as required reading and contains
72 findings; only the evidence ZIP arrived. The search is recorded in
`ledger/missing-attachment.txt`. **This ledger holds 116 findings and does not close that
audit.**

## Running it

```sh
# look at the deliverable the way WordPress will render it
python3 -m http.server 8741            # from this directory
#   -> http://127.0.0.1:8741/albright-wp/preview.html

# look at the optional site
cd site && python3 -m http.server 8731
#   -> http://127.0.0.1:8731/index.html

# regenerate anything you edit
python3 albright-wp/build.py           # copy.md + manifest  -> copy.html
python3 site/gen.py                    # cases.py            -> verify.html

# run the tests (needs: npm i playwright axe-core)
# The browser harnesses need Playwright, axe-core and a Chromium binary.
# Point CHROMIUM at yours if it is not at the default path:
#   npm i playwright axe-core
#   export CHROMIUM=/path/to/chrome
#   python3 -m http.server 8731 --directory site &
#   python3 -m http.server 8741 &
node qa/integrity.mjs .                # static checks, no browser needed
node qa/wp.mjs                         # the deliverable, anatomy + scoping + reflow
node qa/states.mjs                     # reduced motion, print, widths, focus
node qa/pixels.mjs                     # screenshots for the pixel contrast check
for t in dark nojs interact repro targets reflow leak incomplete; do
  echo "== $t"; node qa/$t.mjs || echo "FAILED: $t"
done
bash qa/rebuild.sh /path/to/IHH-FINAL.zip   # generators reproduce the shipped output
```

## What is deliberately not finished

Nine of the ten inductee profiles are unwritten — the brief asks for at least four and this
package delivers one complete profile plus five case files covering five people. Three `slot`
blocks in the site markup are marked and empty: the capital campaign facts, the leadership
roster, and the analytics disclosure. **We will not invent an EIN, a fundraising goal or a
board list.**

No screen-reader user has tested any of this. No volunteer has run the handoff. No permission
letter has been sent to any institution. `site/TESTS-RUN.md` lists what was and was not tested,
and by whom it still needs to be.
