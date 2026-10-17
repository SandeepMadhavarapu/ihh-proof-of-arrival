# Positioning: a supplement and pilot, not a replacement

The board adjudication of 16 October 2026 is the adoption baseline: **option (c) today — take specific ideas — with a controlled pilot toward option (b), supplementing the existing WordPress site. No replacement is authorized at this stage.**

## What this project is

- **Four WordPress-ready-format profiles** (Albright, Lamarr, Pei, Cruz) in `handover/`, built from `inductees/<name>/`: authored text, archival images that were downloaded and viewed, item-level rights wording, and a search log for each. “Verified” here means only the specifically recorded checks; it is not independent historical, rights, accessibility, or publication certification. Byline/editorial placeholders remain and `handover/OPEN-ITEMS.md` lists checks still needing a person. They are not publication-ready.
- **The Verification Desk educational exhibit**, in the optional `site/` demo: five case files, twenty claims, and forty-seven evidence items. Automated interaction tests are evidence of tested behavior, not evidence of learning outcomes.
- **A build-time verification pipeline** that produces static draft profiles. Exact source membership, minimum span length, and lexical overlap reject some bad citations; they do not establish that a source is true or that its meaning supports the claim. Semantic judgment and human sign-off remain necessary. A passing fixture demo is not a newly researched biography.

The standalone demo includes ten photographic portraits with source records. These are separate from the archival images in the four profiles. Publication reuse review is still pending for both.

## What this project is not

It is not a replacement for the museum's content inventory or operating website. Ten profile drafts now exist; it does not provide approved publication of the full collection, community story intake and review, nominations, complete approved institutional pages, production donation/subscription services, or a named maintainer. It contains illustrative institutional pages with unresolved placeholders; they are not approved museum facts. No person has been appointed by this repository to operate it after the hackathon.

The demo's `example.invalid` sitemap URLs are intentional non-production placeholders. They must be replaced with approved deployment URLs or the sitemap omitted before serving a production site.

## Adoption boundary

Keep the museum's current website and services operational. First consider its evidence presentation, accessible interaction patterns, and resource-loading discipline. A WordPress pilot requires a museum-approved staging environment, completed media and editorial review, actual-theme testing, and an observed volunteer handoff. Pasting this fragment into WordPress does not remove the host's scripts or trackers.

The [ranked roadmap](ROADMAP.md) records outstanding conditions and unassigned accountable roles. Human-only conditions have not been completed by automation. Actual hosting/support costs, audience preference, educational benefit, full WCAG conformance, and future maintenance quality have not been established. There is no claim of being “100 times better.”

## Source and build discipline

See [CONTRIBUTING.md](CONTRIBUTING.md). Never repair a generated artifact by hand. Prove reproducibility with `bash qa/rebuild.sh`.

## Sponsor meeting update — 17 October 2026

Reported by team lead from sponsor meeting: IHH is open to considering a new website. This is not a written commitment, publication approval or authorization to replace the live site. All ten profiles are the content target; four is the minimum. A redesigned site remains optional and follows the content, verification and engagement workstreams.
