"""Proposal records and the append-only audit log.

One JSON file per proposal in living/proposals/. Files are never deleted: a rejected proposal
stays, with its reasons. Every state change appends one line to audit.log.jsonl recording who,
what, when and why. Each line carries the SHA-256 of the previous line, so an edited or deleted
line breaks the chain and `verify_chain()` reports it.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import AUDIT_LOG, PROPOSALS

KINDS = ("fact", "media", "correction", "reverify", "tip")   # tip: from a visitor, voices/bridge.py
STATUSES = ("pending", "approved", "rejected", "published")
VERDICTS = ("NOT_VERIFIED", "PASSED_ALL_GATES", "NEEDS_HUMAN_JUDGMENT", "CONFLICT", "REJECTED")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Evidence:
    url: str
    span: str
    retrieved_at: str = ""
    sha256: str = ""
    retrieved_by: str = ""      # network | human | fixture
    snapshot: str = ""          # local path of the cached bytes (gitignored)
    tier: int | None = None
    title: str = ""


@dataclass
class Proposal:
    id: str
    kind: str                   # fact | media | correction | reverify | tip
    slug: str
    section: str                # target section heading in copy.md
    sentence: str               # proposed visitor-facing copy (ages 12-18)
    claim: str                  # the plain factual claim
    evidence: list[Evidence]
    finder: dict[str, Any] = field(default_factory=dict)   # confidence, rationale, mode: never shown to the verifier
    media: dict[str, Any] = field(default_factory=dict)    # for kind=media: manifest fields
    status: str = "pending"
    verdict: str = "NOT_VERIFIED"
    gates: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now)
    decision: dict[str, Any] = field(default_factory=dict)  # by, at, action, reason
    related: str = ""           # e.g. the fact a reverify item refers to

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=1) + "\n"

    @classmethod
    def from_dict(cls, d: dict) -> "Proposal":
        d = dict(d)
        d["evidence"] = [Evidence(**e) for e in d.get("evidence", [])]
        return cls(**d)


class Store:
    def __init__(self, root: Path = PROPOSALS, audit_log: Path | None = None) -> None:
        self.root = Path(root)
        self.audit_log = Path(audit_log) if audit_log else self.root / AUDIT_LOG.name

    def path(self, pid: str) -> Path:
        if not re.fullmatch(r"LM-\d{4,}", pid):
            raise ValueError(f"bad proposal id {pid!r}")
        return self.root / f"{pid}.json"

    def next_id(self) -> str:
        nums = [int(p.stem[3:]) for p in self.root.glob("LM-*.json") if p.stem[3:].isdigit()]
        return f"LM-{max(nums, default=0) + 1:04d}"

    def all(self) -> list[Proposal]:
        return [Proposal.from_dict(json.loads(p.read_text(encoding="utf-8")))
                for p in sorted(self.root.glob("LM-*.json"))]

    def get(self, pid: str) -> Proposal:
        return Proposal.from_dict(json.loads(self.path(pid).read_text(encoding="utf-8")))

    def create(self, p: Proposal, actor: str, why: str) -> Proposal:
        self.root.mkdir(parents=True, exist_ok=True)
        if self.path(p.id).exists():
            raise FileExistsError(p.id)
        self.path(p.id).write_text(p.to_json(), encoding="utf-8", newline="\n")
        self.audit(actor, "created", p.id, "", p.status, why)
        return p

    def update(self, p: Proposal, actor: str, action: str, why: str, old_status: str) -> None:
        self.path(p.id).write_text(p.to_json(), encoding="utf-8", newline="\n")
        self.audit(actor, action, p.id, old_status, p.status, why)

    # -- audit log ---------------------------------------------------------------------------
    def _last_hash(self) -> str:
        if not self.audit_log.exists():
            return "0" * 64
        last = ""
        with self.audit_log.open("rb") as f:
            for line in f:
                if line.strip():
                    last = line
        return hashlib.sha256(last.rstrip(b"\r\n")).hexdigest() if last else "0" * 64

    def audit(self, actor: str, action: str, pid: str, old: str, new: str, why: str) -> dict:
        entry = {"at": now(), "actor": actor, "action": action, "proposal": pid,
                 "from": old, "to": new, "why": why, "prev": self._last_hash()}
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_log.open("a", encoding="utf-8", newline="\n") as f:   # append only
            f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        return entry


def verify_chain(path: Path) -> tuple[bool, str]:
    """True if every line's `prev` is the SHA-256 of the line before it."""
    if not Path(path).exists():
        return True, "no audit log yet"
    prev = "0" * 64
    for n, line in enumerate(Path(path).read_bytes().splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False, f"line {n} is not valid JSON"
        if entry.get("prev") != prev:
            return False, f"line {n}: chain broken (a line was edited, removed or inserted before it)"
        prev = hashlib.sha256(line).hexdigest()
    return True, "audit chain intact"
