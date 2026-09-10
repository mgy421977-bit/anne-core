# ANNE Core — Experiments

## Experiment 1: memory reuse

Run:

```bash
python -m anne_core demo
```

Expected observable pattern:

1. First run: memory miss → exploration → structure creation.
2. Second run: memory candidate → reuse decision → synthesis influenced by prior structure.

The demo is deterministic and offline.

## Experiment 2: semantic retrieval

The MVP uses a dependency-free character n-gram + token cosine approximation. It is intentionally described as a **semantic approximation**, not as a learned embedding model.

Evaluate both:

- paraphrase recall
- unrelated-query rejection

The threshold is configurable on `CognitiveMemory`.

## Experiment 3: stateless baseline

Compare the same task set with and without persistent memory. Record:

- provider calls
- memory reuse
- task success
- contradiction handling
- provenance presence
- latency when measurable

Do not infer superiority from infrastructure metrics alone.

## Experiment hygiene

Keep task sets deterministic where possible. Do not use an answer oracle to influence ANNE's runtime. Expected properties should be used only by the evaluation harness.
