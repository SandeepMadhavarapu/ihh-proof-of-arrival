# Contributing

Read [POSITIONING.md](POSITIONING.md) and [ROADMAP.md](ROADMAP.md) first. This is a supplement/pilot, not an authorized museum replacement. Keep changes on a feature branch from current `main`, open a PR, and do not merge or deploy without explicit authorization. Do not invent facts, biographies, image rights, institutional details, owners, or evidence of human acceptance.

## Build discipline

**Never hand-edit generated files:** `copy.html`, `copy-full.md`, `preview.html`, `verify.html`, or `CLOSURE-LEDGER.*`. Edit their sources and run the appropriate generator:

| Sources | Generator | Generated artifacts |
|---|---|---|
| `albright-wp/copy.md`, `albright-wp/media-manifest.csv` (and builder code only when needed) | `python albright-wp/build.py` | `albright-wp/copy.html`, `copy-full.md`, `preview.html` |
| `profiles/<slug>/copy.md`, `profiles/<slug>/media-manifest.csv` | `python albright-wp/build.py --profile-dir profiles/<slug>` | That profile's `copy.html`, `copy-full.md`, `preview.html` |
| `site/cases.py` (and generator template when needed) | `python site/gen.py` | `site/verify.html` |
| `ledger/findings.py` (and serializer when needed) | `python ledger/emit.py` | `ledger/CLOSURE-LEDGER.md`, `.json`, `.csv` |

The frozen no-argument Albright output must remain byte-for-byte unchanged in changes that promise to preserve it. Check both comparison against the base branch and clean rebuild reproducibility. Do not change fixtures or expected results merely to hide failures. If a stricter contract requires more informative synthetic evidence, retain the original assertions and explain the fixture changes.

## Local validation

Use Python 3.12 and Node.js with `playwright` and `axe-core` installed locally. Set `CHROMIUM` to the browser executable. Run:

```sh
python -m unittest discover -s tests -v
node qa/integrity.mjs .
python -m pipeline.demo
```

The demo starts its own servers on ports 8731/8741; free those ports first. It must not test some other running server's content. Its results are machine checks, not museum publication sign-off.

For the individual browser harnesses, serve `site/` on port 8731 and the repository root on port 8741, then run:

```sh
for t in dark nojs interact pixels states targets reflow leak incomplete wp repro; do
  node qa/$t.mjs || exit 1
done
PROFILE_URL=http://127.0.0.1:8741/profiles/madeleine-albright/preview.html node qa/profile-factory.mjs
```

After committing the candidate, prove clean rebuilds from a fresh archive (requires Bash, unzip, Python 3, and diff):

```sh
git archive --format=zip --prefix=IHH-FINAL/ HEAD -o /tmp/IHH-FINAL.zip
bash qa/rebuild.sh /tmp/IHH-FINAL.zip
```

Also review `qa/` for applicable reproduction harnesses. Keep actual outputs and limitations in the PR. Preserve all gates; never delete or weaken a test to pass. The `.gitignore` excludes dependencies, secrets, caches, and transient run reports; reviewed source, tests, generated publication artifacts, and the ledger remain versioned. Never commit credentials or present a stale successful report as current evidence.

## Publication boundary

Source and rights review, image inspection, named editorial approval, actual WordPress handoff, disabled-user testing, audience/branding decisions, cost approval, and appointment of maintainers require real people. Automated success cannot satisfy them. Leave unresolved media slots and uncertainty statements honest.
