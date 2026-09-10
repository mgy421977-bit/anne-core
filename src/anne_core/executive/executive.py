"""Executive ANNE — evidence-aware synthesis layer.

The MVP executive does not claim to perform model-level reasoning. It applies
explicit deterministic weighting to the evaluated CognitiveStructure so that
agreement, confidence, provenance, and unresolved contradictions are visible
in the final synthesis.
"""

from __future__ import annotations

from anne_core.memory.models import CognitiveStructure


class ExecutiveANNE:
    """Synthesise a user-facing answer from evaluated cognitive state."""

    def synthesise(self, structure: CognitiveStructure, reused: bool = False) -> str:
        lines: list[str] = []

        if reused:
            lines.append(
                "[Executive] Reusing and updating prior cognitive structure "
                f"(id={structure.id[:8]}…, concept={structure.concept})"
            )
        else:
            lines.append(
                f"[Executive] Synthesising evaluated structure for concept: {structure.concept}"
            )

        lines.extend(["", "=== Synthesis ===", ""])

        if structure.findings:
            # Deterministic evidence-aware score. The MVP has no per-finding
            # probability, so agreement and global confidence are used as
            # explicit signals rather than pretending to have learned weights.
            agreement_bonus = min(0.25, 0.05 * len(structure.agreement))
            contradiction_penalty = min(0.25, 0.08 * len(structure.contradictions))
            signal = max(0.0, min(1.0, structure.confidence + agreement_bonus - contradiction_penalty))
            primary = max(structure.findings, key=lambda finding: (len(finding), finding))
            lines.append(f"Primary evaluated finding (signal={signal:.2f}):")
            lines.append(primary)
            lines.append("")

        if structure.agreement:
            lines.append("Points supported across sources:")
            for item in structure.agreement[:8]:
                lines.append(f"  • {item}")
            lines.append("")

        if structure.contradictions:
            lines.append("Unresolved divergences / open questions:")
            for item in structure.contradictions[:8]:
                lines.append(f"  • {item}")
            lines.append("")

        confidence_label = self._confidence_label(structure.confidence)
        lines.append(
            f"Overall confidence: {structure.confidence:.2f} ({confidence_label}) | "
            f"Sources: {', '.join(structure.sources) or 'n/a'} | "
            f"Reusable: {structure.reusable}"
        )

        if structure.evidence:
            lines.append("")
            lines.append("Evidence / provenance trail (abbreviated):")
            for evidence in structure.evidence[:4]:
                lines.append(f"  – {evidence[:160]}{'…' if len(evidence) > 160 else ''}")

        return "\n".join(lines)

    @staticmethod
    def _confidence_label(confidence: float) -> str:
        if confidence >= 0.80:
            return "high"
        if confidence >= 0.60:
            return "moderate"
        return "low"
