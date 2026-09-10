# ANNE Core — Open Cognitive Architecture

**Executable research prototype** demonstrating that outputs from heterogeneous AI systems can be discovered, compared, evaluated, structured, and turned into persistent cognitive memory that is reusable on later related tasks.

> **Status:** MVP / Alpha (v0.1.0)  
> **License:** MIT  
> **Python:** ≥ 3.11

---

## 1. What is ANNE Core?

ANNE Core is the **working, minimal, demonstrable prototype** of the broader ANNE research programme.

It implements a transparent cognitive loop:

```
User
  ↓
ANNE Core
  ↓
Task Decomposition
  ↓
MITOS  (think / explore / delegate / compare)
  ↓
Heterogeneous AI Providers
  ↓
Result Collection
  ↓
Comparison / Cognitive Evaluation
  ↓
Cognitive Structure
  ↓
Persistent Cognitive Memory
  ↓
Executive ANNE  (evaluate / structure / learn / remember)
  ↓
Response
```

An **Agency Gate** sits as a default-deny safety boundary: any action that would affect the external world requires an explicit `ActionProposal` and human approval.

---

## 2. Why it exists

The central hypothesis that this repository makes **executable** (not “proven”) is:

> Different artificial intelligence systems’ outputs can be explored, compared, evaluated, structured, and converted into persistent cognitive memory inside a single cognitive process; that structured knowledge can later be reused on related tasks.

ANNE Core is a **testbed**, not a product claim.

---

## 3. Architecture (high level)

| Layer            | Role                                                                 |
|------------------|----------------------------------------------------------------------|
| **CLI**          | Clean entry points: `ask`, `memory`, `demo`                          |
| **ANNE Core**    | Orchestrates the full loop                                           |
| **MITOS**        | Cognitive exploration & process management (not a simple provider)   |
| **Providers**    | Abstraction over heterogeneous AI sources (Mock, OpenAI, Grok, …)    |
| **Cognition**    | Evaluation → CognitiveStructure                                      |
| **Memory**       | Persistent, structured, reusable cognitive memory (SQLite MVP)       |
| **Executive**    | Final synthesis that does **not** merely echo providers              |
| **Agency Gate**  | Default-deny external-world actions                                  |

---

## 4. Cognitive loop (MVP)

1. User asks a question.  
2. Memory is searched for a relevant prior CognitiveStructure.  
3. If none (or confidence too low) → **NEW TASK** path:  
   - MITOS decomposes the problem  
   - selects providers  
   - collects results  
   - compares them (agreement / contradiction / confidence)  
   - hands findings to the cognitive evaluator  
4. A CognitiveStructure is created and stored.  
5. Executive ANNE synthesises the final answer.  
6. On a second, related question the **reuse path** is taken: prior structure is retrieved, optionally updated with supplemental exploration, and the executive re-synthesises.

---

## 5. MITOS

MITOS is **not** “just another AI provider”.

In this prototype it is the **cognitive exploration / process-management layer**:

- analyse the incoming problem  
- decompose into subtasks  
- select appropriate AI sources  
- request results  
- compare results  
- surface differences / contradictions  
- decide whether further research is needed  
- forward structured findings to ANNE’s evaluation layer  

Mnemonic: **think / explore / delegate / compare**.

---

## 6. Heterogeneous AI providers

```
AIProvider
├── MockProvider     (always available, deterministic, offline)
├── OpenAIProvider   (optional, OPENAI_API_KEY)
└── GrokProvider     (optional, XAI_API_KEY)
```

- API keys are **never** stored in the repository.  
- Environment variables only (see `.env.example`).  
- If no keys are present the system still runs the **full cognitive loop** via MockProvider.  
- Real providers plug into the same abstraction; the rest of the architecture does not change.

---

## 7. Cognitive memory

Memory is **not** conversation history.

A `CognitiveStructure` stores:

| Field            | Purpose                                      |
|------------------|----------------------------------------------|
| concept          | Short label                                  |
| question         | Original question                            |
| findings         | Provider outputs (structured)                |
| sources          | Which providers contributed                  |
| agreement        | Shared points                                |
| contradictions   | Divergences / open issues                    |
| confidence       | Aggregate confidence                         |
| evidence         | Provenance trail                             |
| structure        | Extra structured payload                     |
| timestamp        | When created / updated                       |
| provenance       | MITOS notes, etc.                            |
| reusable         | Whether future tasks may reuse it            |
| tags             | Lightweight indexing                         |

Storage backend for the MVP: **SQLite**.  
The `CognitiveMemory` class is the abstraction point for future backends (vector, graph, …).

---

## 8. Executive ANNE

- Does **not** simply repeat provider text.  
- Receives the evaluated CognitiveStructure.  
- Considers evidence, confidence, contradictions and (when present) prior memory.  
- Produces a coherent synthesis.

---

## 9. Agency Gate

Default **deny**.

Any action that would affect the external world must be expressed as an `ActionProposal`:

```
action, reason, scope, risk, evidence, validation, rollback, authority
```

Explicit approval is required before `execute()`.  
In the MVP the gate is a **demonstration boundary** only; no real external side-effects are performed.

---

## 10. Running locally

```bash
# Clone
git clone https://github.com/mgy421977-bit/anne-core.git
cd anne-core

# Create virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install (editable + test deps)
pip install -e ".[dev]"

# Optional: copy env template
cp .env.example .env
# (fill API keys only if you want real providers)
```

### Ask a question

```bash
python -m anne_core ask "What are the main causes of urban heat islands?"
```

### Inspect memory

```bash
python -m anne_core memory
```

### Run the memory-reuse demo (most important)

```bash
python -m anne_core demo
```

The demo:

1. Runs a question for the first time (full exploration).  
2. Stores a CognitiveStructure.  
3. Runs the same / related question again.  
4. Shows the memory-hit + reuse path in the terminal log.

No API key is required.

---

## 11. Demo output (illustrative)

```
FIRST RUN
ANNE CORE
[NEW TASK]
[MITOS] Decomposing task
[MITOS] Selecting providers
[AI] mock-A
[AI] mock-B
[MITOS] Comparing results
[ANNE] Cognitive evaluation
[MEMORY] New cognitive structure created
[EXECUTIVE] Synthesizing response

SECOND RUN
ANNE CORE
[MEMORY] Relevant cognitive structure found
[MITOS] Evaluating reuse
[MEMORY] Reusing previous structure
[MITOS] Additional exploration required: YES/NO
[ANNE] Updating cognitive structure
[EXECUTIVE] Synthesizing response
```

---

## 12. Tests

```bash
pytest
```

Covered areas:

- task decomposition  
- provider abstraction & MockProvider  
- cognitive evaluation  
- contradiction / agreement surfaces  
- memory write / read / search  
- memory reuse  
- executive synthesis  
- Agency Gate default-deny  
- end-to-end cognitive loop  

All tests are designed to pass offline with MockProvider only.

---

## 13. Real providers

Set the appropriate environment variables (see `.env.example`):

| Variable          | Provider   |
|-------------------|------------|
| `OPENAI_API_KEY`  | OpenAI     |
| `XAI_API_KEY`     | xAI / Grok |

Optional model overrides: `OPENAI_MODEL`, `XAI_MODEL`, `XAI_BASE_URL`.

When keys are present, `get_available_providers()` automatically includes the real providers alongside the mocks. The rest of the architecture is unchanged.

---

## 14. Research hypotheses (explicitly marked)

The following are **hypotheses / future experiments**, **not** claims demonstrated by this repository:

- Energy reduction relative to monolithic LLM usage  
- Hallucination reduction via multi-source comparison  
- Measurable self-improvement loops  
- Fractal / multi-scale intelligence properties  
- Cognitive superiority over single-provider baselines  

This MVP only shows that the **architectural behaviour** (explore → compare → structure → remember → reuse) is executable and observable.

---

## 15. Limitations (honest)

- Task decomposition is heuristic, not a learned planner.  
- Comparison is lightweight (token overlap + confidence heuristics).  
- Memory search is keyword-based; no embeddings yet.  
- MockProvider knowledge is tiny and static.  
- Agency Gate does not yet guard real external tools.  
- No multi-turn dialogue state beyond cognitive structures.  
- No claim of AGI, consciousness, or production readiness.

---

## 16. Roadmap (indicative)

- Semantic / embedding memory search  
- Richer MITOS planner (still transparent)  
- Additional providers (local models, other APIs)  
- Stronger contradiction & confidence models  
- Agency Gate integration with real tool sandboxes  
- Evaluation suite for the research hypotheses above  
- Optional visualisation of cognitive structures  

---

## ANNE Core is NOT

- a new foundation model  
- a replacement for LLMs  
- a claim of AGI  
- a consciousness system  
- proof of energy efficiency  

## ANNE Core IS

- an **executable research prototype**  
- an **open cognitive architecture**  
- a **coordination layer** for heterogeneous AI systems  
- a **persistent cognitive memory** experiment  
- a **testbed** for cognitive orchestration and reuse  

---

## Citation / contact

Repository: https://github.com/mgy421977-bit/anne-core  

Author: Mustafa Gökhan Yılmaz  

If you use this prototype in academic or experimental work, please cite the repository and clearly distinguish demonstrated behaviour from open hypotheses.
