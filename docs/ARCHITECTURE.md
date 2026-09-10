# ANNE Core — Architecture Mapping (Machine-Readable)

This document maps the executable prototype to the research preprint:

**Title:** ANNE — Open Cognitive Architecture  
**Author:** Mustafa Gökhan Yılmaz  
**Date:** September 2026  
**Type:** Research preprint (architecture, hypotheses, experimental protocol)

---

## 1. Conceptual loop (paper)

```
T → D → M → P → E → K → X → G → O
```

| Symbol | Paper meaning | anne-core implementation |
|--------|---------------|---------------------------|
| T | Task | CLI argument to `ask` / `demo` |
| D | Decomposition | `MITOSEngine.analyse_and_decompose()` |
| M | MITOS exploration | `MITOSEngine.explore()` |
| P | Provider computation | `AIProvider.query()` |
| E | Evaluation | `CognitiveEvaluator.evaluate()` |
| K | Cognitive memory | `CognitiveMemory.store()` / `.search()` |
| X | Executive synthesis | `ExecutiveANNE.synthesise()` |
| G | Agency governance | `AgencyGate.propose()` / `.approve()` / `.execute()` |
| O | Output | Final response string returned by `ANNECore.ask()` |

---

## 2. Re-entry / memory influence

Paper diagram shows a dashed edge from Persistent Cognitive Memory back to MITOS.

Implementation location: `ANNECore.ask()`

Algorithm:
1. Search memory for relevant CognitiveStructure (keyword + confidence).
2. If confidence ≥ 0.55 → enter **reuse path**.
3. Optionally run supplemental MITOS exploration if confidence < 0.75.
4. Merge new findings with prior structure via `CognitiveEvaluator.evaluate(..., prior=...)`.
5. Otherwise → full **NEW TASK** path.

---

## 3. Component responsibilities

### MITOS
- Not a provider.
- Process manager: decompose → select → explore → compare → identify gaps → re-enter.
- Code: `src/anne_core/mitos/engine.py`

### Providers
- Abstract resource pool.
- MockProvider is mandatory and deterministic.
- Real providers (OpenAI, Grok) are optional and activated only by environment variables.
- Code: `src/anne_core/providers/`

### Cognitive Evaluation
- Turns MITOS results into a CognitiveStructure.
- Records agreement, contradiction, confidence, evidence, provenance.
- Code: `src/anne_core/cognition/evaluator.py`

### Cognitive Memory
- Persistent, structured, reusable.
- Not conversation history.
- SQLite backend with clear abstraction boundary.
- Code: `src/anne_core/memory/`

### Executive ANNE
- Synthesises from CognitiveStructure, not raw provider text.
- Code: `src/anne_core/executive/executive.py`

### Agency Gate
- Default-deny boundary between inference and consequence.
- Required for any external-world action (including GitHub installer).
- Code: `src/anne_core/safety/agency_gate.py`

### Telemetry
- Optional, opt-out, fail-open, anonymous.
- Never a dependency of the cognitive loop.
- Code: `src/anne_core/telemetry/`

### GitHub Installer
- Optional deployment helper.
- Dry-run by default.
- Writes only after Agency Gate approval.
- Code: `src/anne_core/github/`

---

## 4. Research boundaries (must be respected by any summary)

- No claim of AGI or consciousness.
- No claim of demonstrated energy superiority.
- No claim of guaranteed hallucination reduction.
- “Fractal cognition” means re-entrant graph exploration, not biological equivalence.
- Hypotheses are testable and falsifiable; they are not results.

---

## 5. Two-run protocol (paper §16)

Required demonstration:

1. First run — no relevant memory → full exploration + consolidation.
2. Second run — relevant structure found → reuse reported + optional update.

Implemented by: `python -m anne_core demo`

---

## 6. Priority order (product principle)

```
SAFETY > PRIVACY > REPRODUCIBILITY > FUNCTIONALITY > CONVENIENCE
```

Any future change that violates this order is considered a regression.
