#!/usr/bin/env python3
import sys, os, json, csv, datetime
_TODAY=datetime.date.today()
_ISO=_TODAY.isoformat()
_HUMAN=_TODAY.strftime("%-d %B %Y")
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from findings import F
from collections import Counter

# The count is substituted at emit time. A hardcoded total in the finding about
# not overclaiming went stale once already (AR-05); it cannot now.
for _f in F:
    for _k in ('fix','concern','evidence'):
        if '{LEDGER_COUNT}' in _f.get(_k,''):
            _f[_k]=_f[_k].replace('{LEDGER_COUNT}', str(len(F)))

COLS=["id","sev","status","source","concern","files","repro","cause","fix","evidence","limit"]
for f in F:
    for c in COLS: f.setdefault(c,"")

json.dump({"generated":_ISO,"count":len(F),
  "by_status":dict(Counter(f["status"] for f in F)),
  "by_severity":dict(Counter(f["sev"] for f in F)),
  "findings":F}, open(os.path.join(HERE,"CLOSURE-LEDGER.json"),"w",encoding="utf-8"),
  indent=1, ensure_ascii=False)

with open(os.path.join(HERE,"CLOSURE-LEDGER.csv"),"w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=COLS); w.writeheader(); w.writerows(F)

SEVNAME={"P0":"Privacy / false claim","P1":"Missing content or assets","P2":"Source traceability",
         "P3":"Accessibility","P4":"Layout","P5":"Integration","P6":"Documentation"}
st=Counter(f["status"] for f in F)
md=[f"""# Closure ledger

**{len(F)} findings.** Generated {_HUMAN} by `emit.py` from `findings.py`.
Machine-readable copies: `CLOSURE-LEDGER.json`, `CLOSURE-LEDGER.csv`.

| Status | Count |
|---|---|
| FIXED&ndash;VERIFIED | {st.get('FIXED-VERIFIED',0)} |
| BLOCKED&ndash;EXTERNAL | {st.get('BLOCKED-EXTERNAL',0)} |
| NOT APPLICABLE&ndash;JUSTIFIED | {st.get('NOT-APPLICABLE-JUSTIFIED',0)} |
| OPEN | {st.get('OPEN',0)} |

> **This ledger does not close the 72-finding audit.** `IHH-V3-DEEP-AUDIT.md` was named as
> required reading but was not supplied to this session; only the evidence ZIP arrived. See
> META-01. Any of those 72 findings not independently rediscovered here remains unaddressed.

---
"""]
order=["P0","P1","P2","P3","P4","P5","P6"]
for sev in order:
    rows=[f for f in F if f["sev"]==sev]
    if not rows: continue
    md.append(f"\n## {sev} &mdash; {SEVNAME[sev]} ({len(rows)})\n")
    for f in rows:
        md.append(f"""### {f['id']} &mdash; {f['status']}

**Concern.** {f['concern']}
**Source of the concern.** {f['source']}
**Affected.** `{f['files']}`
**Our reproduction / verification.** {f['repro']}
**Root cause.** {f['cause']}
**Correction.** {f['fix']}
**Evidence of closure.** {f['evidence']}
""" + (f"**Remaining limitation.** {f['limit']}\n" if f['limit'] else ""))
open(os.path.join(HERE,"CLOSURE-LEDGER.md"),"w",encoding="utf-8").write("\n".join(md))
print(f"emitted {len(F)} findings -> .json .csv .md")
