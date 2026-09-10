"""MITOS — cognitive exploration / process management layer.

MITOS is NOT merely an AI provider. It:
- analyses the incoming problem
- decomposes it into subtasks
- selects appropriate AI sources
- requests results from those sources
- compares results
- identifies differences / contradictions
- decides whether further research is needed
- hands structured findings to ANNE's evaluation layer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from anne_core.providers.base import AIProvider, ProviderResult
from anne_core.providers import get_available_providers


@dataclass
class SubTask:
    """A single decomposed unit of work."""

    id: str
    description: str
    prompt: str
    priority: int = 1


@dataclass
class ComparisonResult:
    """Outcome of comparing multiple provider answers."""

    agreements: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    unique_points: dict[str, list[str]] = field(default_factory=dict)
    overall_confidence: float = 0.5
    needs_further_research: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class MITOSResult:
    """Full output of a MITOS exploration cycle."""

    original_question: str
    subtasks: list[SubTask]
    provider_results: list[ProviderResult]
    comparison: ComparisonResult
    selected_providers: list[str]
    exploration_notes: list[str] = field(default_factory=list)


class MITOSEngine:
    """Core MITOS process manager."""

    def __init__(self, providers: list[AIProvider] | None = None) -> None:
        self.providers = providers or get_available_providers()

    def analyse_and_decompose(self, question: str) -> list[SubTask]:
        """Naive but deterministic task decomposition for the MVP.

        Real systems would use a stronger planner; here we keep it transparent
        and testable.
        """
        q = question.strip()
        subtasks = [
            SubTask(
                id="st-1",
                description="Core causal / definitional analysis",
                prompt=(
                    f"Provide a clear, structured analysis of the main factors "
                    f"or causes related to the following question. Be concise "
                    f"and list the key points:\n\n{q}"
                ),
                priority=1,
            ),
            SubTask(
                id="st-2",
                description="Supporting evidence and secondary factors",
                prompt=(
                    f"What supporting evidence, secondary factors, or "
                    f"alternative explanations exist for:\n\n{q}\n\n"
                    f"List them briefly."
                ),
                priority=2,
            ),
        ]
        return subtasks

    def select_providers(self, n: int = 2) -> list[AIProvider]:
        """Select available providers (prefer real ones if present, else mocks)."""
        available = [p for p in self.providers if p.available()]
        if not available:
            from anne_core.providers.mock import MockProvider
            available = [MockProvider("A"), MockProvider("B")]
        return available[:n]

    def collect_results(
        self,
        subtasks: list[SubTask],
        providers: list[AIProvider],
    ) -> list[ProviderResult]:
        results: list[ProviderResult] = []
        for st in subtasks:
            for prov in providers:
                res = prov.query(st.prompt)
                results.append(res)
        return results

    def compare(self, results: list[ProviderResult]) -> ComparisonResult:
        """Simple textual comparison to surface agreement / contradiction."""
        successful = [r for r in results if r.success and r.content.strip()]
        if not successful:
            return ComparisonResult(
                needs_further_research=True,
                notes=["No successful provider results"],
            )

        def tokens(text: str) -> set[str]:
            return set(text.lower().replace(".", " ").replace(",", " ").split())

        all_tokens = [tokens(r.content) for r in successful]
        shared: set[str] = set.intersection(*all_tokens) if all_tokens else set()
        stop = {
            "the", "a", "an", "of", "and", "or", "to", "in", "for", "is", "are",
            "by", "from", "with", "that", "this", "on", "as", "be", "can", "may",
        }
        shared = {t for t in shared if t not in stop and len(t) > 3}

        agreements = sorted(list(shared))[:12]

        unique: dict[str, list[str]] = {}
        for r in successful:
            unique_tokens = tokens(r.content) - shared - stop
            unique[r.provider_name] = sorted(
                [t for t in unique_tokens if len(t) > 4]
            )[:8]

        confidences = [r.confidence for r in successful]
        avg_conf = sum(confidences) / len(confidences)
        conf_spread = max(confidences) - min(confidences) if confidences else 0.0

        contradictions: list[str] = []
        if conf_spread > 0.25:
            contradictions.append(
                f"Confidence spread across providers is high ({conf_spread:.2f})"
            )
        if len(set(r.provider_name for r in successful)) > 1:
            contradictions.append(
                "Multiple independent sources produced partially divergent wording "
                "(expected under heterogeneous providers)"
            )

        needs_more = avg_conf < 0.6 or len(agreements) < 2

        return ComparisonResult(
            agreements=agreements,
            contradictions=contradictions,
            unique_points=unique,
            overall_confidence=avg_conf,
            needs_further_research=needs_more,
            notes=[
                f"Compared {len(successful)} successful results",
                f"Shared meaningful tokens: {len(agreements)}",
            ],
        )

    def explore(self, question: str) -> MITOSResult:
        """Full MITOS cycle: decompose → select → collect → compare."""
        notes: list[str] = []
        notes.append(f"Analysing question: {question[:80]}...")

        subtasks = self.analyse_and_decompose(question)
        notes.append(f"Decomposed into {len(subtasks)} subtasks")

        providers = self.select_providers()
        selected_names = [p.name for p in providers]
        notes.append(f"Selected providers: {selected_names}")

        results = self.collect_results(subtasks, providers)
        notes.append(f"Collected {len(results)} provider results")

        comparison = self.compare(results)
        notes.append(
            f"Comparison complete — confidence={comparison.overall_confidence:.2f}, "
            f"further_research={comparison.needs_further_research}"
        )

        return MITOSResult(
            original_question=question,
            subtasks=subtasks,
            provider_results=results,
            comparison=comparison,
            selected_providers=selected_names,
            exploration_notes=notes,
        )
