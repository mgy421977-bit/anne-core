"""Cognitive memory data models."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import json
import uuid


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CognitiveStructure:
    """A reusable unit of cognitive knowledge produced by ANNE.

    This is deliberately richer than a simple conversation turn. It captures
    the outcome of a multi-provider comparison so that later related tasks
    can reuse the structured knowledge.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    concept: str = ""
    question: str = ""
    findings: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    agreement: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)
    structure: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utcnow)
    provenance: dict[str, Any] = field(default_factory=dict)
    reusable: bool = True
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CognitiveStructure":
        # Tolerate missing keys for forward compatibility
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def summary(self) -> str:
        parts = [
            f"Concept: {self.concept}",
            f"Question: {self.question}",
            f"Confidence: {self.confidence:.2f}",
            f"Findings: {len(self.findings)}",
            f"Agreements: {len(self.agreement)}",
            f"Contradictions: {len(self.contradictions)}",
            f"Reusable: {self.reusable}",
        ]
        return " | ".join(parts)


@dataclass
class MemoryEntry:
    """Thin wrapper used by the storage layer."""

    structure: CognitiveStructure
    raw_json: str = ""

    def __post_init__(self) -> None:
        if not self.raw_json:
            self.raw_json = json.dumps(self.structure.to_dict(), ensure_ascii=False)
