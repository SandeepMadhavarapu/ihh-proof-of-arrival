#!/usr/bin/env python3
"""List everything a person still has to check, from every manifest and search log.

    python3 tools/open_items.py > handover/OPEN-ITEMS.md
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAG = re.compile(r"CONFIRM(?!ED)|FOLLOW UP|RETRY|TO DO|UNRESOLVED|NOT OPENED|FOUND IN SEARCH|NOT EXAMINED|NOT RE-VERIFIED|NOT CHECKED|REVIEW|VERIFY", re.I)

print("# Open items\n")
print("Everything below needs a person with a web browser (or a phone call). Generated from the")
print("manifests and search logs by `tools/open_items.py`; fix the item there, then re-run.\n")
for name in sorted(os.listdir(os.path.join(ROOT, "inductees"))):
    d = os.path.join(ROOT, "inductees", name)
    if not os.path.exists(os.path.join(d, "media-manifest.csv")):
        continue
    lines = ["- **Editorial sign-off pending.** A named human must check the profile and its evidence before publication.",
             "- **Reconciliation review pending.** Review ihh-content-reconciliation.md; proposals do not authorize changing copy.md."]
    note_path = os.path.join(ROOT, "handover", name, "ihh-content-reconciliation.md")
    if os.path.isfile(note_path) and "## Repository correction requiring team-lead approval" in open(note_path, encoding="utf-8").read():
        lines.append("- **Profile correction approval required.** See the repository-correction section of ihh-content-reconciliation.md before publication; the profile is unchanged.")
    log_path = os.path.join(d, "search-log.csv")
    if not os.path.isfile(log_path):
        lines.append("- **MISSING SEARCH LOG: search-log.csv.** Research took place outside this repository. The team lead will supply the actual research record. No substitute log was fabricated.")
    for r in csv.DictReader(open(os.path.join(d, "media-manifest.csv"), encoding="utf-8")):
        flags = " ".join([r["status"], r["recommendation"], r["our_rights_determination"]])
        if FLAG.search(flags) and not r["recommendation"].upper().startswith("DROP"):
            lines.append(f"- **Source item {r['item_no']}, {r['title']}.** {r['recommendation']}. "
                         f"{r['our_rights_determination']} <{r['stable_item_url']}>")
    log_rows = list(csv.DictReader(open(log_path, encoding="utf-8"))) if os.path.isfile(log_path) else []
    for r in log_rows:
        if FLAG.search(r["decision"]):
            what = r["url_or_query"]
            lines.append(f"- **Search: {r['content_type']} at {r['archive']}.** {r['decision']}. "
                         f"{r['reason']} (`{what}`)".replace(" ()", ""))
    print(f"## {name.capitalize()}\n")
    print("\n".join(lines) if lines else "Nothing open.")
    print()
