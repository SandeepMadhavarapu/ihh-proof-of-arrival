"""Validation, rate limiting and the moderation store, shared by every adapter.

A submission is plain text. Nothing here renders HTML: whatever displays a note escapes it
(voices/render.py on the server, textContent in margin-notes.js). Names and emails are
optional; an email is kept for the moderator only and is never in any public output.

Every submission becomes one moderation item (pending -> approved | rejected). Every change
appends a line to an audit log in which each line carries the SHA-256 of the line before it
(the same scheme as the Living Museum, checked by living.proposals.verify_chain).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import time
from collections import defaultdict, deque
from pathlib import Path

TYPES = {"perspective": "My perspective", "more": "I know more",
         "wrong": "Something looks wrong", "question": "Question"}
# margin note | Verify claim report | Verify general form | Verify verdict shared by a visitor
KINDS = ("note", "claim", "tip", "finding")
# A "finding" is the visitor's own verdict on one Verify claim (the agree/disagree step), tied to
# that claim's id like a note is tied to its passage. Its comment is optional: the verdict is the
# response. site-src/gen.py builds the Verify page's verdict radios from this same dict.
VERDICTS = {"confirmed": "Confirmed", "unsupported": "Not supported", "contradicted": "Contradicted"}
FINDING_LABEL = "My finding"
STATUSES = ("pending", "approved", "rejected")
LIMITS = {"text": 1000, "source": 300, "relationship": 100, "name": 40, "email": 120,
          "exact": 600, "prefix": 64, "suffix": 64}
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,80}")
EMAIL_RE = re.compile(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

CONFIRMATION = "Thanks — a curator reviews every note before it appears."
UNDER_13 = ("If you are under 13, please don’t include your name, email, school or anything "
            "else that identifies you. Just tell us what you know.")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def clean(value, limit: int) -> str:
    s = CONTROL.sub("", str(value or "")).replace("\r\n", "\n").strip()
    return s[:limit]


def validate(form: dict) -> tuple[dict | None, list[str]]:
    """(clean submission, []) or (None, [reasons]). A filled honeypot is reported as 'spam'."""
    if str(form.get("website") or "").strip():
        return None, ["spam"]
    errors = []
    kind = form.get("kind", "note")
    if kind not in KINDS:
        errors.append("unknown kind")
    typ = form.get("type", "")
    verdict = str(form.get("verdict") or "")
    if kind == "finding":
        typ = "finding"
        if verdict not in VERDICTS:
            errors.append("record your finding first")
    elif typ not in TYPES:
        errors.append("choose what kind of note this is")
    text = clean(form.get("text"), 10 ** 6)
    if not text and kind != "finding":      # a finding's verdict is its content; its comment is optional
        errors.append("write something first")
    elif len(text) > LIMITS["text"]:
        errors.append(f"keep it under {LIMITS['text']} characters")
    page = str(form.get("page") or "")
    anchor = str(form.get("anchor") or "")
    if not ID_RE.fullmatch(page):
        errors.append("missing page")
    if kind in ("note", "claim", "finding") and not ID_RE.fullmatch(anchor):
        errors.append("missing passage")
    email = clean(form.get("email"), LIMITS["email"])
    if email and not EMAIL_RE.fullmatch(email):
        errors.append("that email address does not look right (it is optional)")
    if errors:
        return None, errors
    sel = form.get("selector") or {}
    sub = {
        "kind": kind, "type": typ, "page": page, "anchor": anchor if kind != "tip" else "",
        "text": text,
        "source": clean(form.get("source"), LIMITS["source"]) if typ in ("more", "wrong") or kind == "tip" else "",
        "relationship": clean(form.get("relationship"), LIMITS["relationship"]) if kind == "tip" else "",
        "inductee": page if kind == "tip" else "",
        "verdict": verdict if kind == "finding" else "",
        "name": clean(form.get("name"), LIMITS["name"]),
        "email": email,
        "selector": {"type": "TextQuoteSelector",
                     "exact": clean(sel.get("exact"), LIMITS["exact"]),
                     "prefix": clean(sel.get("prefix"), LIMITS["prefix"]),
                     "suffix": clean(sel.get("suffix"), LIMITS["suffix"])} if kind in ("note", "finding") else {},
    }
    if kind in ("note", "finding") and not sub["selector"]["exact"]:
        return None, ["missing quoted passage"]
    return sub, []


class RateLimit:
    """At most `n` submissions per `window` seconds from one client."""

    def __init__(self, n: int = 5, window: float = 600, clock=time.monotonic) -> None:
        self.n, self.window, self.clock = n, window, clock
        self.hits: dict[str, deque] = defaultdict(deque)

    def allow(self, client: str) -> bool:
        t, q = self.clock(), self.hits[client]
        while q and t - q[0] > self.window:
            q.popleft()
        if len(q) >= self.n:
            return False
        q.append(t)
        return True


def display_name(name: str) -> str:
    first = re.sub(r"[^\w'\-]", "", (name or "").split()[0]) if (name or "").split() else ""
    return first[:20] if first and not EMAIL_RE.search(name) else "A visitor"


def type_label(item: dict) -> str:
    return FINDING_LABEL if item.get("kind") == "finding" else TYPES.get(item.get("type", ""), "Note")


def public(item: dict) -> dict:
    """The only fields of an item that may ever be shown: never the email, never the source link."""
    out = {"id": item["id"], "kind": item.get("kind", "note"), "page": item["page"], "anchor": item.get("anchor", ""),
           "selector": item.get("selector", {}), "type": item["type"], "type_label": type_label(item),
           "text": EMAIL_RE.sub("[email removed]", item["text"]),
           "by": display_name(item.get("name", "")), "date": item["created_at"][:10]}
    if item.get("kind") == "finding":
        out["verdict"] = item.get("verdict", "")
    return out


class Store:
    """One JSON file per item plus the hash-chained audit log, under one folder."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.items = self.root / "items"
        self.audit_log = self.root / "audit.log.jsonl"

    def _path(self, iid: str) -> Path:
        if not re.fullmatch(r"VV-\d{4,}", iid):
            raise ValueError(f"bad item id {iid!r}")
        return self.items / f"{iid}.json"

    def all(self) -> list[dict]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.items.glob("VV-*.json"))]

    def get(self, iid: str) -> dict:
        return json.loads(self._path(iid).read_text(encoding="utf-8"))

    def _write(self, item: dict) -> None:
        self.items.mkdir(parents=True, exist_ok=True)
        self._path(item["id"]).write_text(json.dumps(item, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8", newline="\n")

    def add(self, sub: dict, adapter: str) -> dict:
        nums = [int(p.stem[3:]) for p in self.items.glob("VV-*.json")] if self.items.exists() else []
        item = dict(sub, id=f"VV-{max(nums, default=0) + 1:04d}", status="pending",
                    created_at=now(), adapter=adapter, decisions=[], living_proposal="")
        self._write(item)
        self.audit("visitor", "submitted", item["id"], "", "pending", f"{item['kind']}/{item['type']} on {item['page']}")
        return item

    def decide(self, iid: str, action: str, actor: str, why: str = "") -> dict:
        item = self.get(iid)
        new = {"approve": "approved", "reject": "rejected"}.get(action)
        if new is None:
            raise ValueError(action)
        if item["status"] == new:
            return item
        old, item["status"] = item["status"], new
        item["decisions"].append({"by": actor, "at": now(), "action": action, "why": why})
        self._write(item)
        self.audit(actor, action, iid, old, new, why)
        return item

    def link_proposal(self, iid: str, pid: str) -> None:
        item = self.get(iid)
        item["living_proposal"] = pid
        self._write(item)
        self.audit("bridge", "sent to Living Museum", iid, item["status"], item["status"], pid)

    def audit(self, actor: str, action: str, iid: str, old: str, new: str, why: str) -> None:
        prev = "0" * 64
        if self.audit_log.exists():
            lines = [l for l in self.audit_log.read_bytes().splitlines() if l.strip()]
            if lines:
                prev = hashlib.sha256(lines[-1]).hexdigest()
        entry = {"at": now(), "actor": actor, "action": action, "item": iid, "from": old, "to": new,
                 "why": why[:300], "prev": prev}
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_log.open("a", encoding="utf-8", newline="\n") as f:     # append only
            f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
