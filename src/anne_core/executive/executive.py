"""Executive ANNE — final synthesis layer.

Does NOT simply echo provider outputs.
Uses cognitive evaluation + memory context + evidence/confidence/contradiction
signals to produce a coherent final response.
"""

from __future__ import annotations

from anne_core.memory.models import CognitiveStructure


class ExecutiveANNE:
    """Synthesise a user-facing answer from a CognitiveStructure."""

    def synthesise(
        self,
        structure: CognitiveStructure,
        reused: bool = False,
    ) -> str:
        lines: list[str] = []

        if reused:
            lines.append(
                "[Executive] Reusing and updating prior cognitive structure "
                f"(id={structure.id[:8]}…, concept={structure.concept})"
            )
        else:
            lines.append(
                f"[Executive] Synthesising new response for concept: {structure.concept}"
            )

        lines.append("")
        lines.append("=== Synthesis ===")
        lines.append("")

        # Lead with highest-signal finding
        if structure.findings:
            # Prefer the longest / most informative finding
            primary = max(structure.findings, key=len)
            lines.append(primary)
            lines.append("")

        if structure.agreement:
            lines.append("Points of agreement across sources:")
            for a in structure.agreement[:8]:
                lines.append(f"  • {a}")
            lines.append("")

        if structure.contradictions:
            lines.append("Noted divergences / open questions:")
            for c in structure.contradictions:
                lines.append(f"  • {c}")
            lines.append("")

        lines.append(
            f"Overall confidence: {structure.confidence:.2f} | "
            f"Sources: {', '.join(structure.sources) or 'n/a'} | "
            f"Reusable: {structure.reusable}"
        )

        if structure.evidence:
            lines.append("")
            lines.append("Evidence trail (abbreviated):")
            for e in structure.evidence[:4]:
                lines.append(f"  – {e[:120]}{'…' if len(e) > 120 else ''}")

        return "\n".join(lines)
