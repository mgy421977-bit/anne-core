"""ANNE cognitive evaluation layer.

Takes MITOS exploration results and produces a CognitiveStructure
ready for persistent memory and executive synthesis.
"""

from __future__ import annotations

from typing import Any

from anne_core.memory.models import CognitiveStructure
from anne_core.mitos.engine import MITOSResult


class CognitiveEvaluator:
    """Evaluate / structure / learn."""

    def evaluate(
        self,
        mitos_result: MITOSResult,
        prior: CognitiveStructure | None = None,
    ) -> CognitiveStructure:
        """Transform MITOS output into a reusable CognitiveStructure.

        If a prior structure is supplied (memory reuse path), the new
        findings are merged rather than discarded.
        """
        findings: list[str] = []
        evidence: list[str] = []
        sources: list[str] = []

        for r in mitos_result.provider_results:
            if r.success and r.content.strip():
                findings.append(r.content.strip())
                sources.append(r.provider_name)
                evidence.append(
                    f"[{r.provider_name}] conf={r.confidence:.2f} "
                    f"meta={r.metadata}"
                )

        comparison = mitos_result.comparison

        # Derive a short concept label from the question
        concept = self._extract_concept(mitos_result.original_question)

        structure_payload: dict[str, Any] = {
            "subtasks": [
                {"id": st.id, "description": st.description}
                for st in mitos_result.subtasks
            ],
            "selected_providers": mitos_result.selected_providers,
            "comparison_notes": comparison.notes,
            "unique_points": comparison.unique_points,
        }

        if prior is not None:
            # Merge path
            findings = list(dict.fromkeys(prior.findings + findings))  # stable unique
            sources = list(dict.fromkeys(prior.sources + sources))
            evidence = prior.evidence + evidence
            agreement = list(dict.fromkeys(prior.agreement + comparison.agreements))
            contradictions = list(
                dict.fromkeys(prior.contradictions + comparison.contradictions)
            )
            confidence = max(prior.confidence, comparison.overall_confidence)
            structure_payload["updated_from"] = prior.id
            structure_payload["prior_timestamp"] = prior.timestamp
        else:
            agreement = comparison.agreements
            contradictions = comparison.contradictions
            confidence = comparison.overall_confidence

        return CognitiveStructure(
            concept=concept,
            question=mitos_result.original_question,
            findings=findings,
            sources=sources,
            agreement=agreement,
            contradictions=contradictions,
            confidence=confidence,
            evidence=evidence,
            structure=structure_payload,
            provenance={
                "mitos_notes": mitos_result.exploration_notes,
                "provider_count": len(mitos_result.provider_results),
            },
            reusable=True,
            tags=self._tags_from_question(mitos_result.original_question),
        )

    def _extract_concept(self, question: str) -> str:
        # Very light heuristic for the MVP
        q = question.lower().strip()
        if "urban heat" in q or "heat island" in q:
            return "urban heat islands"
        if "climate" in q:
            return "climate change"
        # Fallback: first 6 content words
        words = [w for w in q.replace("?", "").split() if len(w) > 2][:6]
        return " ".join(words) if words else "general"

    def _tags_from_question(self, question: str) -> list[str]:
        q = question.lower()
        tags = []
        for term in [
            "urban",
            "heat",
            "climate",
            "energy",
            "ai",
            "cognition",
            "memory",
        ]:
            if term in q:
                tags.append(term)
        return tags or ["general"]
