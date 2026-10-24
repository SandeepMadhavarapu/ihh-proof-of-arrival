"""Deterministic text rules shared by the gates. No model, no network.

Everything here is conservative on purpose: when in doubt a token is extracted, so the claim has
to find it in a quoted span. Missing a real match costs a proposal; inventing one could publish
a falsehood.
"""
from __future__ import annotations

import re

# Characters that differ between a browser's rendering and raw page text without changing
# meaning. Quotes and apostrophes are NOT folded: a quotation must match its source literally.
_INVISIBLE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"), None)


def norm(text: str) -> str:
    """Collapse whitespace (incl. NBSP and line breaks) and drop invisible characters."""
    return re.sub(r"\s+", " ", text.translate(_INVISIBLE).replace(" ", " ")).strip()


_UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
_ORD_UNITS = {w: i + 1 for i, w in enumerate(
    "first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth "
    "fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth".split())}
_ORD_TENS = {w: 10 * (i + 2) for i, w in enumerate(
    "twentieth thirtieth fortieth fiftieth sixtieth seventieth eightieth ninetieth".split())}
_SCALE = {"hundred": 100, "thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000}
MONTHS = {m: i + 1 for i, m in enumerate(
    "january february march april may june july august september october november december".split())}
_MONTH_ABBR = {m[:3]: i for m, i in MONTHS.items()} | {"sept": 9}

SUPERLATIVES = frozenset("""first only last sole earliest oldest youngest largest biggest
highest greatest best most least longest tallest smallest fastest richest finest lowest
original unique unprecedented""".split())

AWARD_WORDS = re.compile(
    r"\b(award(?:ed|s)?|prize|medal|honou?r(?:ed|s|ary)?|inducted|induction|hall of fame|trophy|"
    r"oscar|grammy|emmy|tony|peabody|knight(?:ed|hood)?|order of|laureate|decorat(?:ed|ion)|"
    r"degree|doctorate|ll\.?d|d\.?d)\b", re.I)


def _word_number(tokens: list[str], i: int) -> tuple[int | None, bool, int]:
    """Parse a written number starting at tokens[i]. Returns (value, is_ordinal, length)."""
    total, current, j, ordinal = 0, None, i, False
    while j < len(tokens):
        w = tokens[j]
        parts = w.split("-")
        if len(parts) == 2 and parts[0] in _TENS and (parts[1] in _UNITS or parts[1] in _ORD_UNITS):
            current = (current or 0) + _TENS[parts[0]] + _UNITS.get(parts[1], _ORD_UNITS.get(parts[1], 0))
            ordinal = parts[1] in _ORD_UNITS
            j += 1
            if ordinal:
                break
            continue
        if w in _UNITS or w in _TENS:
            current = (current or 0) + _UNITS.get(w, _TENS.get(w, 0))
        elif w in _ORD_UNITS or w in _ORD_TENS:
            current = (current or 0) + _ORD_UNITS.get(w, _ORD_TENS.get(w, 0))
            ordinal, j = True, j + 1
            break
        elif w in _SCALE and current is not None:
            current *= _SCALE[w]
            if _SCALE[w] >= 1000:
                total, current = total + current, 0
        elif w == "and" and current is not None and j + 1 < len(tokens) and (
                tokens[j + 1] in _UNITS or tokens[j + 1].split("-")[0] in _TENS):
            pass
        else:
            break
        j += 1
    if current is None and total == 0:
        return None, False, 0
    return total + (current or 0), ordinal, j - i


def facts(text: str) -> set[str]:
    """Numbers, ordinals and calendar months a reader would treat as factual content.

    Cardinals come back as "29", ordinals as "ord:1", months as "month:6". Commas inside
    numbers are removed ("1,500" -> "1500"). Numeric dates are split into day/month/year:
    YYYY-MM-DD, MM/DD/YYYY (US) and DD.MM.YYYY (European).
    """
    t = norm(text)
    out: set[str] = set()

    def add_date(day: str, month: str, year: str) -> None:
        out.add(str(int(day)))
        out.add(f"month:{int(month)}")
        out.add(str(int(year)))

    for y, m, d in re.findall(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", t):
        add_date(d, m, y)
    t = re.sub(r"\b\d{4}-\d{1,2}-\d{1,2}\b", " ", t)
    for m, d, y in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", t):
        add_date(d, m, y)
    t = re.sub(r"\b\d{1,2}/\d{1,2}/\d{4}\b", " ", t)
    for d, m, y in re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", t):
        add_date(d, m, y)
    t = re.sub(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", " ", t)

    for decade in re.findall(r"\b(\d{3}0)s\b", t):          # "the 1920s" -> 1920
        out.add(decade)
    for num, suffix in re.findall(r"(?<![\w.])(\d[\d,]*)(st|nd|rd|th)?(?![\w])", t, re.I):
        value = num.replace(",", "").lstrip("0") or "0"
        out.add(value)
        if suffix:                                             # "26th" also counts as 26
            out.add(f"ord:{value}")

    # A month name counts only beside a number ("March 28", "28 March", "March 1868"), so the
    # verb "may" and place names such as "March Field" are not read as dates.
    month_re = "|".join(sorted(list(MONTHS) + [a for a in _MONTH_ABBR if a not in MONTHS], key=len, reverse=True))
    for m in re.finditer(rf"\b({month_re})\b\.?,?\s+\d|\d\s+({month_re})\b", t, re.I):
        name = (m.group(1) or m.group(2)).lower()
        out.add(f"month:{MONTHS.get(name) or _MONTH_ABBR[name]}")

    words = re.findall(r"[a-z]+(?:-[a-z]+)?", t.lower())
    i = 0
    while i < len(words):
        w = words[i]
        # "one of", "no one", "one another": pronoun uses, not quantities.
        if w == "one" and ((i + 1 < len(words) and words[i + 1] in {"of", "another"})
                           or (i > 0 and words[i - 1] in {"no", "any", "every", "some", "each", "the"})):
            i += 1
            continue
        value, ordinal, length = _word_number(words, i)
        if length:
            out.add(f"ord:{value}" if ordinal else str(value))
            i += length
            continue
        i += 1
    return out


def years(text: str) -> set[int]:
    return {int(x) for x in facts(text) if x.isdigit() and 1000 <= int(x) <= 2100}


def superlatives(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", norm(text).lower()) if w in SUPERLATIVES}


def needs_corroboration(sentence: str) -> list[str]:
    """Why a sentence needs two independent sources (empty list: it does not)."""
    why = []
    if facts(sentence):
        why.append("contains a date, number or ordinal")
    if AWARD_WORDS.search(sentence):
        why.append("describes an award or honour")
    if superlatives(sentence):
        why.append("contains a superlative or 'first'")
    return why
