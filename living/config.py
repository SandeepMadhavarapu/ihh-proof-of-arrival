"""Paths, the source allowlist, and the global kill switch for the Living Museum."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LIVING = ROOT / "living"
PROPOSALS = LIVING / "proposals"
AUDIT_LOG = PROPOSALS / "audit.log.jsonl"
CACHE = LIVING / ".cache"            # gitignored: fetched bytes, snapshots, human imports
PAUSED = LIVING / "PAUSED"           # kill switch: if this file exists, nothing runs
HEALTH = LIVING / "health.json"
SOURCES_FILE = LIVING / "sources.yaml"

# Paths no agent may write. Only living/publisher.py (the approval step) touches them, and only
# on a branch that a person merges through a reviewed pull request.
PROTECTED = ("inductees/*/copy.md", "inductees/*/media-manifest.csv", "site/**")


class Paused(RuntimeError):
    pass


def check_not_paused() -> None:
    if PAUSED.exists():
        shown = PAUSED.relative_to(ROOT) if PAUSED.is_relative_to(ROOT) else PAUSED
        raise Paused(f"Living Museum is paused: {shown} exists. Delete it to resume.")


@dataclass
class Sources:
    version: int
    user_agent: str
    rate_limit_seconds: float
    timeout: int
    suffixes: dict[str, tuple[int, str]] = field(default_factory=dict)
    domains: dict[str, tuple[int, str]] = field(default_factory=dict)
    entities: dict[str, list[str]] = field(default_factory=dict)
    seeds: dict[str, list[str]] = field(default_factory=dict)

    def tier(self, url: str) -> int | None:
        """1 or 2 for an allowlisted https URL, otherwise None."""
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if p.scheme != "https" or not host:
            return None
        for name, (tier, _) in self.domains.items():   # explicit domains override suffixes
            if host == name or host.endswith("." + name):
                return tier
        for suffix, (tier, _) in self.suffixes.items():
            if host.endswith(suffix):
                return tier
        return None

    def note(self, url: str) -> str:
        host = (urlparse(url).hostname or "").lower()
        for name, (_, note) in {**self.domains}.items():
            if host == name or host.endswith("." + name):
                return note
        for suffix, (_, note) in self.suffixes.items():
            if host.endswith(suffix):
                return note
        return ""


def registrable_domain(url: str) -> str:
    """Two-label domain used for independence (si.edu, biographi.ca, fiba.basketball)."""
    host = (urlparse(url).hostname or "").lower()
    return ".".join(host.split(".")[-2:])


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split("|")]


def parse_sources(text: str) -> Sources:
    """Strict parser for the documented sources.yaml shape. Unknown keys are errors."""
    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {"suffixes": [], "domains": []}
    maps: dict[str, dict[str, str]] = {"entities": {}, "seeds": {}}
    section = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if not line.startswith(" "):
            key, sep, value = line.partition(":")
            if not sep:
                raise ValueError(f"sources.yaml line {n}: expected 'key: value'")
            key, value = key.strip(), value.strip()
            if key in lists or key in maps:
                if value:
                    raise ValueError(f"sources.yaml line {n}: '{key}' takes indented entries")
                section = key
            elif key in {"version", "user_agent", "rate_limit_seconds", "request_timeout_seconds"}:
                scalars[key] = value
                section = None
            else:
                raise ValueError(f"sources.yaml line {n}: unknown key '{key}'")
            continue
        item = line.strip()
        if section in lists:
            if not item.startswith("- "):
                raise ValueError(f"sources.yaml line {n}: expected '- name | tier | note'")
            lists[section].append(item[2:])
        elif section in maps:
            key, sep, value = item.partition(":")
            if not sep or not re.fullmatch(r"[a-z0-9-]+", key.strip()):
                raise ValueError(f"sources.yaml line {n}: expected 'slug: values'")
            maps[section][key.strip()] = value.strip()
        else:
            raise ValueError(f"sources.yaml line {n}: indented line outside a section")

    def tiered(entries: list[str], label: str) -> dict[str, tuple[int, str]]:
        out = {}
        for entry in entries:
            name, tier, note = (_split(entry) + ["", ""])[:3]
            if tier not in {"1", "2"} or not name:
                raise ValueError(f"sources.yaml {label}: bad entry {entry!r}")
            out[name.lower()] = (int(tier), note)
        return out

    return Sources(
        version=int(scalars.get("version", "0")),
        user_agent=scalars["user_agent"],
        rate_limit_seconds=float(scalars.get("rate_limit_seconds", "3")),
        timeout=int(scalars.get("request_timeout_seconds", "25")),
        suffixes=tiered(lists["suffixes"], "suffixes"),
        domains=tiered(lists["domains"], "domains"),
        entities={k: _split(v) for k, v in maps["entities"].items()},
        seeds={k: _split(v) for k, v in maps["seeds"].items()},
    )


def load_sources(path: Path = SOURCES_FILE) -> Sources:
    return parse_sources(path.read_text(encoding="utf-8"))
