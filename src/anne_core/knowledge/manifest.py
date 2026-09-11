"""Content-addressed, consent-aware knowledge exchange manifest."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class KnowledgeManifest:
    """Metadata for a shareable knowledge package, not the private content itself."""

    concept: str
    owner_anne_id: str
    content_hash: str
    license: str = "private"
    share_scope: str = "private"
    confidence: float = 0.0
    provenance: list[str] = field(default_factory=list)
    knowledge_id: str = field(default_factory=lambda: f"GM-K-{uuid4().hex}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def from_content(
        cls,
        content: bytes,
        concept: str,
        owner_anne_id: str,
        *,
        license: str = "private",
        share_scope: str = "private",
        confidence: float = 0.0,
        provenance: list[str] | None = None,
    ) -> "KnowledgeManifest":
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        digest = hashlib.sha256(content).hexdigest()
        return cls(
            concept=concept,
            owner_anne_id=owner_anne_id,
            content_hash=f"sha256:{digest}",
            license=license,
            share_scope=share_scope,
            confidence=confidence,
            provenance=list(provenance or []),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, indent=2)

    @classmethod
    def from_json(cls, value: str) -> "KnowledgeManifest":
        return cls(**json.loads(value))
