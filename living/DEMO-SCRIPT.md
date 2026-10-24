# Living Museum: two-minute demo for judges

Run everything from the repository root. On Windows, set `PYTHONUTF8=1` first. Times are approximate.

## Before the demo (not on the clock)

```
python living/run.py status
python living/eval/run_eval.py
```

Open the review queue in a browser tab: `python living/run.py review`, then <http://127.0.0.1:8765/>. Open `site/new.html` and the profile page you will show (e.g. `site/lamarr.html`) in other tabs.

## 0:00 – 0:20 Discover

> "Every page here was researched by hand. The Living Museum keeps researching, but it is never allowed to publish on its own."

```
python living/run.py find --slug lamarr --limit 3
```

Point out what the output shows:

- it reads only allowlisted, trusted sources;
- it identifies itself honestly, obeys robots.txt and waits between requests;
- a blocked page is reported as "could not retrieve".

## 0:20 – 0:50 Gates

```
python living/run.py verify
```

> "A separate checker never sees the finder's reasoning. It fetches every source again itself."

In the queue tab, open one card (e.g. LM-0033, "the U.S. Navy did not use the invention during World War II"):

- the quoted words highlighted inside the real page text, with tier badges for the Smithsonian (tier 1) and Encyclopedia.com (tier 2);
- the gate table: exact words present, every number present, two independent domains, no contradiction;
- the banner: with no AI key the meaning check says **NEEDS HUMAN JUDGMENT**. The system never pretends to understand.

Then show LM-0030, the honorary MA. The Dictionary of Canadian Biography says 1911 and FIBA says 1910, so it arrives as a **CONFLICT** item with no Approve button.

> "On 75 deliberately false statements, including four real errors we found on IHH's own pages, the automatic checks accepted none."

(`living/eval/RESULTS.md`)

## 0:50 – 1:20 Human approval

On a fact card: type a name, press **Approve and create PR branch**. The publisher:

- re-checks the sources;
- adds the sentence to `copy.md` with a `{verified:ID}` marker, the sources to the manifest, and the evidence to `verified-facts.json`;
- rebuilds the pages and runs the rebuild check;
- commits on a new branch with a pull-request body listing every source, span and gate result.

> "Merging that pull request is the approval. Nothing goes live any other way."

## 1:20 – 1:40 Live page

Open the profile page. The approved paragraph carries a small **✓ Verified · Sources N · Last checked [date]** note that links to the source cards below. Then open **New at the Museum** (`site/new.html`): one entry, written for young visitors, with its source. Before anything is approved this page honestly says "Nothing new yet".

*(This beat needs a fact that a person has actually approved. If none has been approved yet, show the empty "New at the Museum" page and the pull-request body instead. Never approve a fact just for the demo.)*

## 1:40 – 2:00 The museum checks itself

```
python living/run.py watchdog --simulate living/demo/watchdog-simulation.json
```

> "This is a **simulation**: a local copy of the Nobel Prize page was edited on purpose so it now says 1941."

The watchdog re-reads both sources behind the published fact "Einstein became a U.S. citizen in 1940", finds the quoted words gone from one of them, and opens a re-verification item. The published page is left alone until a person decides.

Close: *"Found by software, checked word by word, approved by a person, and watched for as long as it is on the wall."*

## Honest limits to mention if asked

- The AI meaning judge has not been measured yet; no key was used. Until it is, people judge meaning.
- Corroboration is strict: under the current trust tiers no dated Naismith fact can pass, because all his sources are tier 2.
- Some major references (Britannica, Congress.gov, parts of the Smithsonian) refuse automated requests. A reviewer can save such a page in a normal browser and import it; it is then labelled "retrieved by a person".
