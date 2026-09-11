"""Stable, non-personal ANNE installation identity."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class ANNEIdentity:
    """A local ANNE-ID. It is not an account number and contains no PII."""

    anne_id: str

    @classmethod
    def create(cls) -> "ANNEIdentity":
        return cls(f"ANNE-{uuid4().hex}")

    @classmethod
    def load_or_create(cls, path: str | Path) -> "ANNEIdentity":
        p = Path(path)
        if p.exists():
            value = p.read_text(encoding="utf-8").strip()
            if value.startswith("ANNE-"):
                return cls(value)
        identity = cls.create()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(identity.anne_id + "\n", encoding="utf-8")
        return identity
