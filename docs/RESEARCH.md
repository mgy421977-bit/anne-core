# ANNE Core — Research Protocol

## Research question

Can an open cognitive architecture transform heterogeneous AI outputs into persistent, evaluated, reusable cognitive structures so that structurally related future tasks require less repeated exploration while maintaining task success, provenance, and bounded agency?

## Status

This repository demonstrates the mechanism, not the hypothesis's superiority.

### Demonstrated
- executable decomposition/exploration/evaluation/memory/synthesis loop
- persistent CognitiveStructure storage
- deterministic offline memory reuse
- explicit semantic-candidate scoring using a lightweight local approximation
- evidence-aware executive synthesis
- default-deny Agency Gate

### Measured infrastructure
- provider calls and outcomes
- memory hits/misses
- reuse decisions
- similarity scores
- contradiction/agreement counts
- confidence

### Not yet established
- general reasoning superiority
- energy reduction
- hallucination reduction
- scalable scientific discovery
- AGI, consciousness, or unrestricted self-improvement

## Baselines

At minimum compare ANNE with a stateless execution path using the same provider/task set. Future work may add conventional RAG and multi-agent baselines.

## Evaluation classes

- NOVEL: no relevant prior structure
- REPEATED: same task repeated
- RELATED: paraphrased/structurally related task
- CONTRADICTORY: conflicting provider evidence
- CHAINED: prior result becomes input to a later task

## Falsification criteria

The central reuse hypothesis is weakened or rejected if, across a sufficiently controlled task distribution, memory reuse does not reduce repeated external work, or reduces it only by causing a material loss of task success, evidence quality, or provenance.

Small MVP datasets are infrastructure demonstrations and should not be treated as statistically conclusive evidence.
