# The Living Museum: a guide for IHH staff

The Living Museum keeps the ten inductee pages growing without letting a single unchecked word onto them. A research tool looks for new facts in trusted archives. A checking tool tests every word against the original source. **A person on your team approves each change.** The public pages only ever show approved content.

## What it does

1. **Finds.** It reads pages from a fixed list of trusted sources (government archives, the Smithsonian, national biography dictionaries, official estates, halls of fame, encyclopedias). It looks for facts about an inductee that are not on our page yet.
2. **Checks.** A separate checker opens each source again and tests the proposed sentence in five ways:
   - **The words are really there.** The quoted passage must appear, word for word, on the source page, and the inductee's name must be close by.
   - **Every number and date matches.** Each year, date, number and word like "first" or "only" must appear in the quoted passage.
   - **Two sources agree.** Any date, number, award or "first" needs two independent websites, at least one of them official.
   - **It means what it says.** An AI judge, if one is set up, checks the meaning. Otherwise you are the judge, and the queue says so.
   - **No contradictions.** If it contradicts something we already publish, it becomes a correction for you to look at. Nothing is ever replaced automatically.
3. **Waits for you.** Anything that passes appears in a private review queue on your computer. Nothing changes on the website until you approve it *and* the change is merged on GitHub.
4. **Keeps watching.** The "watchdog" re-opens every source behind every published fact. If a source changes or disappears, the fact goes back into your queue for a second look. It never deletes anything by itself.

## What it can never do

- It never edits a public page on its own. Only the approval step changes a page, through a pull request a person merges.
- It never touches the live immigranthallofhonor.org website or WordPress. You paste approved content in yourself (see below).
- It never uses sources that aren't on the trusted list, and it never gets around a website that blocks it. A blocked page is recorded as "could not retrieve".
- It never marks anything "museum ready". That is always a person's decision.
- It never deletes a rejected idea. Every proposal and every decision is kept, with who decided and why.

## How to review the queue

Someone with the project on their computer runs:

```
python living/run.py review
```

and opens <http://127.0.0.1:8765/> in a browser. This page exists only on that computer and is never published.

Each card shows:

- the proposed sentence;
- each source, with the quoted words highlighted in context, the source's trust level ("Tier 1" is official or primary, "Tier 2" is an established reference) and how it was retrieved;
- the five checks and their results in plain words;
- exactly how the inductee's page would change.

- **Approve** records your name and decision. **Approve and create PR branch** also prepares the change on a new branch so a pull request can be opened.
- **Reject** needs a short reason. The idea stays on record.
- Items marked **CONFLICT** cannot be approved with a button. They mean our sources disagree, or a source disagrees with what we already publish. An editor looks into it and fixes the page by hand if needed.
- If the sentence is marked "the source's own wording", please rewrite it for 12–18-year-olds before approving. A rewritten sentence is checked again from scratch.

After approval, a developer runs `python living/run.py publish --id LM-0000 --branch`. The page is rebuilt, the evidence is saved for good, and the fact appears on "New at the Museum". Merging that pull request on GitHub is the final approval.

## How to pause it

Create an empty file called `PAUSED` in the `living` folder (commit it if the automated runs should stop too). While it exists, nothing runs: no searching, no checking, no publishing, no watchdog. Delete the file to resume. The automated GitHub run checks for it as well.

## What it costs

- **Without an AI key** the system costs nothing to run. The searching and checking are ordinary code. Every proposal that passes the automatic checks waits for a person to judge its meaning.
- **With an AI key** (Anthropic Claude), each proposal costs one judge call. With Claude Opus 5.5 at its published price ($4 per million input tokens, $20 per million output tokens, as listed in October 2026), our estimate is about **4 cents per proposal**, so a run of 15 proposals would be about 60 cents. This is an estimate, not a measurement: nothing has been run with a key yet. Each run has caps on searches, time and AI calls (`--max-fetches`, `--max-seconds`, `--max-llm-calls`), and `--dry-run` writes nothing.
- **GitHub Actions:** a run takes a few minutes. Public repositories don't pay for Actions minutes; private repositories have a monthly allowance.

## How it plugs into your WordPress site

No plugin is needed.

- **Inductee pages:** each inductee's page is one block of HTML: `inductees/<name>/copy.html`. Approved facts appear inside it, with a small "Verified · Sources · Last checked" note. Paste the whole file into one WordPress **Custom HTML** block, as described in `handover/INSTALL.md`. When a new fact is approved, paste the updated file again.
- **New at the Museum:** run `python living/run.py export-wp`, then paste the file it names into a Custom HTML block on any page you like. It lists only approved discoveries, each with its source. While nothing has been approved, it says "Nothing new yet".

## Turning on the scheduled run (optional)

The file `.github/workflows/living-museum.yml` only runs when someone presses "Run workflow" on GitHub.

1. In the repository settings, add the secret `ANTHROPIC_API_KEY` and the variable `ANTHROPIC_MODEL`, for example `claude-opus-5-5`. Both are optional; see "What it costs".
2. Turn on branch protection first (see `living/BRANCH-PROTECTION.md`).
3. Only then, if you want a weekly run, remove the `#` in front of the two `schedule` lines.

The automated run only ever opens a pull request containing new proposals. It cannot change a public page.
