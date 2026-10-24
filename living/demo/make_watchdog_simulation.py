"""Build the LOCAL watchdog simulation used in the demo. It is a simulation, labelled as one.

    python living/demo/make_watchdog_simulation.py

Takes one fact whose two spans were verified on real pages (Einstein's 1940 citizenship:
docsteach.org and nobelprize.org, from living/eval/fixtures.json), keeps the first page excerpt as
fetched, and EDITS the second excerpt so its sentence now says 1941. Nothing here is fetched or
published; the watchdog reads this file instead of the network when given --simulate.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = json.loads((HERE.parent / "eval" / "fixtures.json").read_text(encoding="utf-8"))["pages"]
DT = "https://docsteach.org/document/declaration-intention-einstein/"
NOB = "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"
DT_SPAN = "In 1940, the man who had first proposed the theory of relativity in 1905 became a citizen of the United States."
NOB_SPAN = "He became a United States citizen in 1940"

edited = FIX[NOB]["text"].replace(NOB_SPAN, "He became a United States citizen in 1941")
assert edited != FIX[NOB]["text"], "span not found in the fixture"
sim = {
    "label": "SIMULATION: a local copy of a source page was edited on purpose to show the watchdog catching a change. "
             "Not real drift; nothing was fetched or published.",
    "facts": [{
        "id": "SIM-0001", "slug": "einstein", "section": "(simulation)",
        "sentence": "Albert Einstein became a citizen of the United States in 1940.",
        "source_items": [], "last_checked": "2026-10-17",
        "evidence": [
            {"url": DT, "span": DT_SPAN, "sha256": FIX[DT]["sha256"], "tier": 1},
            {"url": NOB, "span": NOB_SPAN, "sha256": FIX[NOB]["sha256"], "tier": 1},
        ],
    }],
    "pages": {
        DT: {"status": "RETRIEVED", "text": FIX[DT]["text"], "sha256": FIX[DT]["sha256"], "retrieved_at": "simulation"},
        NOB: {"status": "RETRIEVED", "text": edited, "sha256": "simulated-edit", "retrieved_at": "simulation"},
    },
}
(HERE / "watchdog-simulation.json").write_text(json.dumps(sim, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("wrote living/demo/watchdog-simulation.json (SIMULATION)")
