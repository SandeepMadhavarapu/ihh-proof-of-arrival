"""Passages and W3C TextQuoteSelectors.

tools/build_profile.py gives every paragraph, fact, quote and caption a stable id
(<slug>-<section>-<hash of its text>) and the attribute data-ihh-anchor. A note stores that id
plus a TextQuoteSelector (https://www.w3.org/TR/annotation-model/#text-quote-selector):
the exact words chosen, and up to 32 characters either side.

When the copy is edited, a passage's id changes. `reattach` then finds where the note belongs:

  1. "exact"  the stored id still exists and still contains the quoted words
  2. "moved"  prefix + exact + suffix (or exact alone, if it occurs once) found in another passage
  3. "fuzzy"  the closest passage window is at least 85% similar to the quoted words
  4. "flagged" none of the above: the note is not shown, and a moderator is told

It never guesses between two equally good places: an ambiguous match is flagged, not attached.
"""
from __future__ import annotations

import difflib
import re
from html import unescape
from html.parser import HTMLParser

CONTEXT = 32
FUZZY = 0.85


def norm(s: str) -> str:
    return " ".join(unescape(s).split())


class _Passages(HTMLParser):
    """Collect the text of every element marked data-ihh-anchor, skipping badges and note controls."""

    VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None, bool]] = []   # tag, anchor id, skipping
        self.found: dict[str, list[str]] = {}
        self.order: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        a = dict(attrs)
        aid = a.get("id") if "data-ihh-anchor" in a else None
        classes = (a.get("class") or "").split()
        skip = "vbadge" in classes or "vv-ui" in classes or bool(self.stack and self.stack[-1][2])
        if aid:
            self.found[aid] = []
            self.order.append(aid)
        self.stack.append((tag, aid, skip))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.stack and self.stack[-1][2]:
            return
        for _, aid, _ in self.stack:
            if aid:
                self.found[aid].append(data)


def passages(page_html: str) -> dict[str, str]:
    """{anchor id: normalized text}, in page order."""
    p = _Passages()
    p.feed(page_html)
    return {aid: norm("".join(p.found[aid])) for aid in p.order}


def selector(text: str, start: int, end: int) -> dict:
    """TextQuoteSelector for text[start:end] of one passage."""
    return {"type": "TextQuoteSelector", "exact": text[start:end],
            "prefix": text[max(0, start - CONTEXT):start], "suffix": text[end:end + CONTEXT]}


def _best_window(exact: str, text: str) -> float:
    if not exact or not text:
        return 0.0
    n = len(exact)
    if len(text) <= n:
        return difflib.SequenceMatcher(None, exact, text, autojunk=False).ratio()
    best, step = 0.0, max(1, n // 8)
    for i in range(0, len(text) - n + step, step):
        r = difflib.SequenceMatcher(None, exact, text[i:i + n], autojunk=False).ratio()
        best = max(best, r)
    return best


def reattach(anchor: str, sel: dict, pages: dict[str, str]) -> tuple[str | None, str]:
    """(anchor id, how) for where this note belongs now; (None, "flagged") if nowhere safely."""
    exact = norm(sel.get("exact", ""))
    prefix, suffix = norm(sel.get("prefix", "")), norm(sel.get("suffix", ""))
    if not exact:
        return None, "flagged"
    if anchor in pages and exact in pages[anchor]:
        return anchor, "exact"
    full = f"{prefix} {exact} {suffix}".strip() if (prefix or suffix) else exact
    hits = [a for a, t in pages.items() if full in t] or [a for a, t in pages.items() if exact in t]
    if len(hits) == 1:
        return hits[0], "moved"
    if len(hits) > 1:
        return None, "flagged"
    scores = sorted(((_best_window(exact, t), a) for a, t in pages.items()), reverse=True)
    if scores and scores[0][0] >= FUZZY and (len(scores) == 1 or scores[1][0] < scores[0][0]):
        return scores[0][1], "fuzzy"
    return None, "flagged"
