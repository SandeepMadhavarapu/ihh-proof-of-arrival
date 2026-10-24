# Branch protection: settings for the repository owner to turn on

Nothing in this repository changes GitHub settings. These settings make "a person merges the pull request" the real, enforced approval. Without them, `.github/CODEOWNERS` is only advisory.

On GitHub: **Settings → Branches → Add branch protection rule** (or **Rules → Rulesets → New branch ruleset**) for the branch `main`:

| Setting | Value | Why |
|---|---|---|
| Branch name pattern | `main` | The branch the public site is built from. |
| Require a pull request before merging | **On** | No direct pushes, including by the Living Museum workflow. |
| Required approvals | **1** | A person approves every change. |
| Dismiss stale pull request approvals when new commits are pushed | **On** | An approval covers exactly what was reviewed. |
| Require review from Code Owners | **On** | Activates `.github/CODEOWNERS` for `inductees/`, `site/`, `site-data/`, `site-src/`, `tools/`, `pipeline/`, `living/`, `.github/`. |
| Require approval of the most recent reviewable push | **On** | The person who pushed last cannot approve their own change. |
| Require status checks to pass before merging | **On**: select **`test`** (Profile Factory CI) | Unit tests, the gate eval (fails on any false accept) and the rebuild check must pass. |
| Require branches to be up to date before merging | **On** | Checks run against what will actually merge. |
| Require conversation resolution before merging | **On** | Review questions get answered. |
| Do not allow bypassing the above settings | **On** | Applies to admins too. |
| Allow force pushes | **Off** | History, including the audit log, cannot be rewritten. |
| Allow deletions | **Off** | |

Also check:

- **Settings → Actions → General → Workflow permissions:** "Read repository contents" by default. `living-museum.yml` asks for `contents: write` and `pull-requests: write` itself, and only to open a pull request.
- **"Allow GitHub Actions to create and approve pull requests":** allow *create* only if you use the scheduled run. A bot must never approve.
- **Secrets:** only `ANTHROPIC_API_KEY`, added by you. Nothing in the repository contains or prints a key; `qa/secrets.py` checks that on every CI run.
