"""Observable metrics for a single cognitive loop run.

These counters make the core hypothesis measurable without claiming
superiority. They are intentionally simple and offline-safe.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class LoopMetrics:
    """Counters and decisions for one ANNECore.ask() execution."""

    provider_calls: int = 0
    provider_successes: int = 0
    provider_failures: int = 0
    memory_hits: int = 0
    memory_misses: int = 0
    reuse_decision: bool = False
    reuse_reason: str = ""
    source_structure_ids: list[str] = field(default_factory=list)
    new_exploration_required: bool = False
    structures_created: int = 0
    structures_reused: int = 0
    contradictions_detected: int = 0
    agreements_detected: int = 0
    confidence: float = 0.0
    influenced_decomposition: bool = False
    influenced_synthesis: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary_lines(self) -> list[str]:
        lines = [
            "--- METRICS ---",
            f"provider_calls            : {self.provider_calls}",
            f"provider_successes        : {self.provider_successes}",
            f"provider_failures         : {self.provider_failures}",
            f"memory_hits               : {self.memory_hits}",
            f"memory_misses             : {self.memory_misses}",
            f"reuse_decision            : {self.reuse_decision}",
            f"reuse_reason              : {self.reuse_reason or 'n/a'}",
            f"source_structure_ids      : {self.source_structure_ids or []}",
            f"new_exploration_required  : {self.new_exploration_required}",
            f"structures_created        : {self.structures_created}",
            f"structures_reused         : {self.structures_reused}",
            f"contradictions_detected   : {self.contradictions_detected}",
            f"agreements_detected       : {self.agreements_detected}",
            f"confidence                : {self.confidence:.2f}",
            f"influenced_decomposition  : {self.influenced_decomposition}",
            f"influenced_synthesis      : {self.influenced_synthesis}",
        ]
        return lines
