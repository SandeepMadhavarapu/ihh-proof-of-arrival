from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class Provenance(str, Enum):
    RECORD = "RECORD"
    QUOTATION = "QUOTATION"
    PARAPHRASE = "PARAPHRASE"
    INFERENCE = "INFERENCE"
    UNRESOLVED = "UNRESOLVED"


class Verdict(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class FetchStatus(str, Enum):
    RETRIEVED = "RETRIEVED"
    FETCH_FAILED = "FETCH_FAILED"
    UNPARSED = "UNPARSED"


@dataclass
class SourceDocument:
    source_id: str
    url: str
    status: FetchStatus
    title: str = ""
    retrieved_at: str = ""
    content_type: str = ""
    text: str = ""
    sha256: str = ""
    error: str = ""
    from_cache: bool = False
    research_excerpt_chars: int = 0
    research_truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class Claim:
    claim_id: str
    sentence: str
    provenance: Provenance
    source_ids: List[str] = field(default_factory=list)
    verdict: Verdict = Verdict.PENDING
    evidence_source_id: str = ""
    evidence_span: str = ""
    verifier_reason: str = ""
    suggested_rewrite: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["provenance"] = self.provenance.value
        d["verdict"] = self.verdict.value
        return d


@dataclass
class SentenceAudit:
    sentence_id: str
    sentence: str
    requires_evidence: bool
    claim_id: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationReport:
    profile_name: str
    generated_at: str
    gate_passed: bool
    claims: List[Claim]
    sentence_audit: List[SentenceAudit] = field(default_factory=list)
    removed_or_rewritten: List[Dict[str, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for claim in self.claims:
            counts[claim.verdict.value] = counts.get(claim.verdict.value, 0) + 1
        return {
            "profile_name": self.profile_name,
            "generated_at": self.generated_at,
            "gate_passed": self.gate_passed,
            "counts": counts,
            "claims": [c.to_dict() for c in self.claims],
            "sentence_audit": [s.to_dict() for s in self.sentence_audit],
            "removed_or_rewritten": self.removed_or_rewritten,
            "notes": self.notes,
        }


@dataclass
class HandoffRecord:
    at: str
    sender: str
    receiver: str
    summary: str
    artifact_hashes: Dict[str, str] = field(default_factory=dict)
    result: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProfileDraft:
    name: str
    slug: str
    seed_urls: List[str]
    out_dir: Path
    sources: Dict[str, SourceDocument] = field(default_factory=dict)
    copy_markdown: str = ""
    claims: List[Claim] = field(default_factory=list)
    sentence_audit: List[SentenceAudit] = field(default_factory=list)
    media_rows: List[Dict[str, str]] = field(default_factory=list)
    verification_report: Optional[VerificationReport] = None
    handoffs: List[HandoffRecord] = field(default_factory=list)
    status: str = "REQUIRES HUMAN SIGN-OFF"
    completed: bool = False
    failure_reason: str = ""

    def to_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "seed_urls": list(self.seed_urls),
            "out_dir": f"profiles/{self.slug}/",
            "status": self.status,
            "completed": self.completed,
            "human_signoff": "REQUIRED",
            "museum_ready": False,
            "failure_reason": self.failure_reason,
            "source_count": len(self.sources),
            "claim_count": len(self.claims),
            "verification_gate": self.verification_report.gate_passed if self.verification_report else None,
            "handoffs": [h.to_dict() for h in self.handoffs],
        }
