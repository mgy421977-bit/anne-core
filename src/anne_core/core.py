"""ANNE Core — main cognitive loop orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anne_core.cognition.evaluator import CognitiveEvaluator
from anne_core.executive.executive import ExecutiveANNE
from anne_core.memory.models import CognitiveStructure
from anne_core.memory.sqlite import CognitiveMemory
from anne_core.mitos.engine import MITOSEngine, MITOSResult
from anne_core.safety.agency_gate import AgencyGate


@dataclass
class LoopResult:
    """Outcome of a single cognitive loop execution."""

    question: str
    response: str
    structure: CognitiveStructure
    reused: bool
    mitos: MITOSResult | None
    log: list[str]


class ANNECore:
    """Top-level orchestrator implementing the MVP cognitive loop."""

    def __init__(
        self,
        memory: CognitiveMemory | None = None,
        mitos: MITOSEngine | None = None,
        evaluator: CognitiveEvaluator | None = None,
        executive: ExecutiveANNE | None = None,
        agency_gate: AgencyGate | None = None,
    ) -> None:
        self.memory = memory or CognitiveMemory()
        self.mitos = mitos or MITOSEngine()
        self.evaluator = evaluator or CognitiveEvaluator()
        self.executive = executive or ExecutiveANNE()
        self.agency_gate = agency_gate or AgencyGate()

    def ask(self, question: str, force_new: bool = False) -> LoopResult:
        """Run the full cognitive loop for a user question.

        Memory reuse path is taken automatically when a relevant prior
        structure exists and force_new is False.
        """
        log: list[str] = []
        log.append("ANNE CORE")
        log.append(f"Question: {question}")

        prior: CognitiveStructure | None = None
        reused = False
        mitos_result: MITOSResult | None = None

        if not force_new:
            candidates = self.memory.search(question, limit=3)
            if candidates:
                prior = candidates[0]
                log.append(f"[MEMORY] Relevant cognitive structure found (id={prior.id[:8]}…)")
                log.append(f"[MEMORY] Concept={prior.concept} conf={prior.confidence:.2f}")
                log.append("[MITOS] Evaluating reuse")
                # Simple heuristic: reuse if confidence is decent and concept overlaps
                if prior.confidence >= 0.55:
                    reused = True
                    log.append("[MEMORY] Reusing previous structure")
                    # Decide whether additional exploration is still useful
                    need_more = prior.confidence < 0.75
                    log.append(
                        f"[MITOS] Additional exploration required: {'YES' if need_more else 'NO'}"
                    )
                    if need_more:
                        log.append("[MITOS] Performing supplemental exploration")
                        mitos_result = self.mitos.explore(question)
                        structure = self.evaluator.evaluate(mitos_result, prior=prior)
                        log.append("[ANNE] Updating cognitive structure")
                    else:
                        structure = prior
                        log.append("[ANNE] Cognitive structure reused as-is")
                else:
                    log.append("[MEMORY] Prior structure confidence too low — treating as new")
                    prior = None

        if not reused:
            log.append("[NEW TASK]")
            log.append("[MITOS] Decomposing task")
            mitos_result = self.mitos.explore(question)
            for note in mitos_result.exploration_notes:
                log.append(f"  {note}")
            log.append(f"[MITOS] Selecting providers → {mitos_result.selected_providers}")
            for r in mitos_result.provider_results:
                status = "OK" if r.success else f"FAIL ({r.error})"
                log.append(f"[AI] {r.provider_name} → {status}")
            log.append("[MITOS] Comparing results")
            log.append(
                f"  agreements={len(mitos_result.comparison.agreements)} "
                f"contradictions={len(mitos_result.comparison.contradictions)} "
                f"conf={mitos_result.comparison.overall_confidence:.2f}"
            )
            log.append("[ANNE] Cognitive evaluation")
            structure = self.evaluator.evaluate(mitos_result)
            log.append("[MEMORY] New cognitive structure created")

        # Persist (always store the latest view)
        self.memory.store(structure)
        log.append(f"[MEMORY] Stored structure id={structure.id[:8]}…")

        log.append("[EXECUTIVE] Synthesizing response")
        response = self.executive.synthesise(structure, reused=reused)

        return LoopResult(
            question=question,
            response=response,
            structure=structure,
            reused=reused,
            mitos=mitos_result,
            log=log,
        )

    def memory_summary(self) -> str:
        items = self.memory.list_all(limit=20)
        if not items:
            return "Cognitive memory is empty."
        lines = [f"Cognitive memory ({self.memory.count()} structures):", ""]
        for s in items:
            lines.append(f"• [{s.id[:8]}] {s.summary()}")
        return "\n".join(lines)
