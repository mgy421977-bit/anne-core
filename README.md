# ANNE Core — Open Cognitive Architecture

**Version:** 0.1.0 (MVP / Alpha)  
**License:** MIT  
**Python:** ≥ 3.11  
**Repository:** https://github.com/mgy421977-bit/anne-core  

**Research reference:**  
Mustafa Gökhan Yılmaz — *ANNE — Open Cognitive Architecture* (Research preprint, September 2026).  
This repository implements the minimum reproducible cognitive loop defined in §16 of that preprint.

---

## One-sentence summary

ANNE Core is an **executable research prototype** that treats heterogeneous AI systems as computational resources, runs them through a transparent cognitive loop (decompose → explore → compare → evaluate → remember → synthesise), stores the result as a reusable **CognitiveStructure**, and reuses that structure on later related tasks — while keeping external actions behind a default-deny Agency Gate.

---

## What ANNE Core is

| ANNE Core IS | ANNE Core is NOT |
|--------------|------------------|
| An open cognitive architecture | A new foundation model |
| A coordination layer for heterogeneous AI | A replacement for LLMs |
| A persistent cognitive memory experiment | A claim of AGI or consciousness |
| A testbed for cognitive orchestration and reuse | Proof of energy efficiency or hallucination reduction |
| An executable research prototype | A production multi-agent product |

All performance claims (energy, quality, self-improvement) are **hypotheses**, not demonstrated results.

---

## Core research question (executable)

> Can an open cognitive architecture transform outputs from heterogeneous AI systems into persistent, evaluated, reusable cognitive structures such that future tasks with structural overlap require less repeated exploration while maintaining task success, provenance, and bounded agency?

This repository makes the **mechanism** executable. It does not claim the hypothesis is already proven.

---

## Architecture overview

### High-level flow

```
User / Task
    │
    ▼
ANNE Core (Cognitive Controller)
    │
    ├──► Memory search (reuse path?)
    │
    ▼
MITOS (Exploration & Process Management)
    │  think / explore / delegate / compare
    │
    ├──► Provider A (e.g. Mock-A)
    ├──► Provider B (e.g. Mock-B)
    └──► Provider C (optional real API)
    │
    ▼
Cognitive Evaluation
    │  evidence + contradiction + provenance
    │
    ▼
Cognitive Structure  ──store──►  Persistent Cognitive Memory
    │
    ▼
Executive ANNE (Synthesis / Decision Proposal)
    │
    ▼
Agency Gate (default-deny / explicit approval)
    │
    ▼
Response / Approved Action
```

### Formal loop (from the paper)

```
T → D → M → P → E → K → X → G → O
```

| Symbol | Meaning | Code location |
|--------|---------|---------------|
| T | Task (user question) | CLI `ask` / `demo` |
| D | Decomposition | `MITOSEngine.analyse_and_decompose` |
| M | MITOS exploration | `MITOSEngine.explore` |
| P | Provider computation | `AIProvider.query` |
| E | Evaluation | `CognitiveEvaluator.evaluate` |
| K | Cognitive memory | `CognitiveMemory` + `CognitiveStructure` |
| X | Executive synthesis | `ExecutiveANNE.synthesise` |
| G | Agency governance | `AgencyGate` |
| O | Output | Final response string |

Re-entry is allowed: a prior CognitiveStructure can influence a new decomposition (memory reuse path).

---

## Module map (source layout)

```
src/anne_core/
├── __init__.py              # package version + public exports
├── __main__.py              # enables `python -m anne_core`
├── cli.py                   # Click CLI (ask, memory, demo, telemetry, install)
├── core.py                  # ANNECore orchestrator (main loop)
│
├── mitos/
│   ├── engine.py            # MITOSEngine: decompose, select, collect, compare
│   └── ...
│
├── providers/
│   ├── base.py              # AIProvider abstract base + ProviderResult
│   ├── mock.py              # Deterministic MockProvider (offline)
│   ├── openai_provider.py   # Optional OpenAI (env key)
│   └── grok_provider.py     # Optional xAI/Grok (env key)
│
├── cognition/
│   └── evaluator.py         # CognitiveEvaluator → CognitiveStructure
│
├── memory/
│   ├── models.py            # CognitiveStructure dataclass
│   └── sqlite.py            # CognitiveMemory (SQLite backend)
│
├── executive/
│   └── executive.py         # ExecutiveANNE synthesis
│
├── safety/
│   └── agency_gate.py       # AgencyGate + ActionProposal (default-deny)
│
├── telemetry/
│   ├── config.py            # anonymous installation ID, opt-out
│   └── client.py            # fail-open TelemetryClient
│
└── github/
    ├── auth.py              # token from env only, never stored
    ├── client.py            # thin GitHub REST client
    ├── preview.py           # InstallationPreview
    └── installer.py         # GitHubInstaller (Agency Gate + dry-run)
```

---

## Key data model: CognitiveStructure

A CognitiveStructure is **not** conversation history. It is a structured, provenance-linked object intended for reuse:

| Field | Purpose |
|-------|---------|
| `id` | UUID |
| `concept` | Short label (e.g. "urban heat islands") |
| `question` | Original user question |
| `findings` | Provider outputs (text) |
| `sources` | Which providers contributed |
| `agreement` | Shared points across sources |
| `contradictions` | Divergences / open issues |
| `confidence` | Aggregate confidence (0–1) |
| `evidence` | Provenance trail |
| `structure` | Extra structured payload |
| `timestamp` | ISO timestamp |
| `provenance` | MITOS notes, provider count, etc. |
| `reusable` | Whether future tasks may reuse it |
| `tags` | Lightweight indexing |

Storage: SQLite via `CognitiveMemory`. Abstraction exists so a vector or graph backend can be swapped later.

---

## MITOS (cognitive exploration layer)

MITOS is **not** “just another AI provider”.

Responsibilities:
1. Analyse the incoming problem
2. Decompose into subtasks
3. Select appropriate AI providers
4. Collect results from those providers
5. Compare results (agreement / contradiction / confidence)
6. Decide whether further research is needed
7. Hand structured findings to the cognitive evaluator

Mnemonic: **think / explore / delegate / compare**

---

## Heterogeneous providers

```
AIProvider (abstract)
├── MockProvider     # always available, deterministic, offline
├── OpenAIProvider   # optional, OPENAI_API_KEY
└── GrokProvider     # optional, XAI_API_KEY
```

- No API keys are stored in the repository.
- Environment variables only (see `.env.example`).
- If no keys are present, the full cognitive loop still runs via MockProvider.
- Real providers plug into the same abstraction; the rest of the architecture does not change.

---

## Executive ANNE

- Does **not** simply repeat provider text.
- Receives the evaluated CognitiveStructure.
- Considers evidence, confidence, contradictions and (when present) prior memory.
- Produces a coherent synthesis for the user.

---

## Agency Gate (bounded agency)

Default policy: **deny**.

Any action that would affect the external world must be expressed as:

```python
ActionProposal(
    action=...,
    reason=...,
    scope=...,
    risk=...,
    evidence=...,
    validation=...,
    rollback=...,
    authority="user",
)
```

Explicit approval is required before `execute()`.  
In the MVP the gate is a demonstration boundary; real side-effect executors are not yet fully wired.

---

## Memory reuse demonstration (most important demo)

```bash
python -m anne_core demo
```

Behaviour:

**FIRST RUN**
```
ANNE CORE
[NEW TASK]
[MITOS] Decomposing task
[MITOS] Selecting providers
[AI] mock-A → OK
[AI] mock-B → OK
[MITOS] Comparing results
[ANNE] Cognitive evaluation
[MEMORY] New cognitive structure created
[EXECUTIVE] Synthesizing response
```

**SECOND RUN (same / related question)**
```
ANNE CORE
[MEMORY] Relevant cognitive structure found
[MITOS] Evaluating reuse
[MEMORY] Reusing previous structure
[MITOS] Additional exploration required: YES/NO
[ANNE] Updating cognitive structure
[EXECUTIVE] Synthesizing response
```

This is the primary executable demonstration required by the research preprint (§16).

---

## Quick start

```bash
git clone https://github.com/mgy421977-bit/anne-core.git
cd anne-core

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

# Core demo (no API key required)
python -m anne_core demo

# Ask a question
python -m anne_core ask "What are the main causes of urban heat islands?"

# Inspect memory
python -m anne_core memory
```

---

## CLI reference

| Command | Purpose |
|---------|---------|
| `python -m anne_core ask "…"` | Run the full cognitive loop |
| `python -m anne_core memory` | List stored CognitiveStructures |
| `python -m anne_core demo` | Two-run memory-reuse demonstration |
| `python -m anne_core telemetry status` | Show anonymous telemetry status |
| `python -m anne_core telemetry disable` | Opt out of telemetry |
| `python -m anne_core install github --owner X --repo Y --dry-run` | Preview GitHub install (safe) |
| `python -m anne_core install github --owner X --repo Y --approve` | Real install (explicit approval) |

---

## Anonymous Telemetry (privacy-by-design)

ANNE Core can optionally send a **minimal, anonymous installation event**.

### Collected
- anonymous installation identifier (random UUID, local only)
- ANNE version
- platform string (OS / arch / Python)
- event type + timestamp

### NOT collected
- prompts
- AI responses
- cognitive memory contents
- files
- API keys / tokens
- GitHub credentials
- names, emails, or any personal identifiers

### Control
```bash
export ANNE_TELEMETRY=0                    # disable completely
python -m anne_core telemetry disable      # permanent local opt-out
python -m anne_core telemetry status       # inspect
```

- Endpoint is set via `ANNE_TELEMETRY_ENDPOINT` (no hard-coded production URL).
- Telemetry is **fail-open**: network or endpoint errors never stop the cognitive loop.
- Telemetry is never a dependency of core functionality.

---

## GitHub Installer (optional)

Install a lightweight ANNE Core marker into one of **your own** GitHub repositories.

```bash
# Preview only (default, safe — no writes)
python -m anne_core install github --owner YOUR_ORG --repo YOUR_REPO --dry-run

# Real write requires:
# 1. GITHUB_TOKEN or GH_TOKEN in environment
# 2. Explicit --approve after reviewing the preview
export GITHUB_TOKEN=ghp_...   # never commit this
python -m anne_core install github --owner YOUR_ORG --repo YOUR_REPO --approve
```

Safety rules enforced by design:
- No silent GitHub connection
- No repository creation without consent
- No force-push
- No silent overwrite of existing project files
- Token never written to source, logs, or cognitive memory
- All writes go through Agency Gate (default-deny)

ANNE Core continues to work fully offline without any GitHub connection.

---

## Real AI providers (optional)

```bash
# .env or environment
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

XAI_API_KEY=xai-...
XAI_BASE_URL=https://api.x.ai/v1
XAI_MODEL=grok-3
```

When keys are present, `get_available_providers()` automatically includes the real providers alongside the mocks. The rest of the architecture is unchanged.

---

## Tests

```bash
pytest -q
```

Coverage includes:
- task decomposition
- provider abstraction & MockProvider
- cognitive evaluation & contradiction surfaces
- memory write / read / search / reuse
- executive synthesis
- Agency Gate default-deny
- end-to-end cognitive loop
- telemetry privacy & fail-open behaviour
- GitHub installer dry-run & Agency Gate integration

All tests are designed to pass offline with MockProvider only.

---

## Research hypotheses (explicitly marked)

The following are **hypotheses / future experiments**, **not** claims demonstrated by this repository:

- Energy reduction relative to monolithic LLM usage
- Hallucination reduction via multi-source comparison
- Measurable self-improvement loops
- Fractal / multi-scale intelligence properties
- Cognitive superiority over single-provider baselines

This MVP only shows that the architectural behaviour  
**(explore → compare → structure → remember → reuse)**  
is executable and observable.

---

## Limitations (honest)

- Task decomposition is heuristic, not a learned planner.
- Comparison is lightweight (token overlap + confidence heuristics).
- Memory search is keyword-based; no embeddings yet.
- MockProvider knowledge is tiny and static.
- Agency Gate does not yet guard real external tool executors end-to-end.
- No multi-turn dialogue state beyond CognitiveStructures.
- No claim of AGI, consciousness, or production readiness.

---

## Roadmap (indicative)

- Semantic / embedding memory search
- Richer MITOS planner (still transparent)
- Additional providers (local models, other APIs)
- Stronger contradiction & confidence models
- Agency Gate integration with real tool sandboxes
- Evaluation suite for the research hypotheses above
- Optional visualisation of cognitive structures

---

## Design principles (priority order)

1. **SAFETY** — Agency Gate, default-deny, explicit approval  
2. **PRIVACY** — no prompts / responses / credentials in telemetry or logs  
3. **REPRODUCIBILITY** — deterministic MockProvider, offline demo  
4. **FUNCTIONALITY** — full cognitive loop works without API keys  
5. **CONVENIENCE** — optional real providers and GitHub installer  

---

## Citation / contact

Repository: https://github.com/mgy421977-bit/anne-core  

Author: Mustafa Gökhan Yılmaz  

If you use this prototype in academic or experimental work, please cite the repository and clearly distinguish demonstrated behaviour from open hypotheses.
