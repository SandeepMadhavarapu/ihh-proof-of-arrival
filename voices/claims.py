"""The Verify page's claims, loaded once from site-src/gen.py (claim ids are stable there).

Shared by voices/demo_server.py and voices/migrate_anchors.py so both read claims the same way.
"""
from __future__ import annotations

import functools
import html
import importlib.util
import re
from pathlib import Path

from .anchors import norm

ROOT = Path(__file__).resolve().parents[1]


@functools.lru_cache(maxsize=None)
def load_gen(root: Path = ROOT):
    spec = importlib.util.spec_from_file_location("ihh_gen", Path(root) / "site-src" / "gen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def claim_texts(root: Path = ROOT) -> dict[str, str]:
    """claim id -> its text, tags removed and whitespace normalized."""
    return {cl["id"]: norm(re.sub(r"<[^>]+>", "", cl["text"])) for c in load_gen(root).CASES for cl in c["claims"]}


def claim_cases(root: Path = ROOT) -> dict[str, str]:
    """claim id -> inductee slug (each Verify case file is named by its inductee's slug)."""
    return {cl["id"]: c["id"] for c in load_gen(root).CASES for cl in c["claims"]}
