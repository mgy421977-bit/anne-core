# ANNE Core — Open Cognitive Architecture

**Version:** 0.2.0 (Distributed Knowledge / Alpha)  
**License:** MIT  
**Python:** ≥ 3.11  
**Repository:** https://github.com/mgy421977-bit/anne-core  

ANNE Core is an executable research prototype for cognitive orchestration, evaluated persistent memory, bounded agency, and now local-first distributed-knowledge primitives.

## v0.2.0: ANNE Knowledge Layer

The new `anne_core.knowledge` package establishes the first implementation boundary for the next ANNE concept:

```text
ANNE Core
  ├─ local cognitive memory
  ├─ MITOS exploration
  ├─ Agency Gate
  └─ Knowledge Layer
       ├─ ANNE-ID                 local non-PII installation identity
       ├─ KnowledgeManifest       content hash + provenance + consent scope
       └─ PrivateVault            AES-128-GCM local encryption
```

### Local-first privacy model

Private or institutional material should remain in a user-controlled local vault unless the user explicitly chooses to share it. The knowledge manifest contains metadata and a SHA-256 content address; it does not publish the private content itself.

`PrivateVault` derives a 128-bit AES key from a user passphrase with `scrypt` and encrypts content with authenticated AES-128-GCM. The passphrase is never stored by ANNE.

Example:

```python
from anne_core.knowledge import ANNEIdentity, KnowledgeManifest, PrivateVault

identity = ANNEIdentity.load_or_create(".anne/anne_id")

private_blob = PrivateVault.encrypt(
    b"institutional or personal document",
    "user-chosen passphrase",
)

manifest = KnowledgeManifest.from_content(
    b"validated research result",
    "photobioreactor optimization",
    identity.anne_id,
    license="cc-by-4.0",
    share_scope="anonymous-network",
    confidence=0.90,
    provenance=["MITOS", "source-id"],
)
```

### Consent is explicit

A knowledge package is not public merely because it exists. `share_scope` and `license` are explicit fields. Future P2P transport must enforce these permissions before any content leaves the local machine.

Planned scopes include private/local, institution-only, and explicitly shared anonymous-network knowledge. The protocol must never infer permission from technical availability.

### Distributed knowledge roadmap

The current implementation deliberately stops before introducing a production P2P transport. The next layer can add a BitTorrent-compatible/content-addressed transport behind the manifest and consent boundary.

Target architecture:

```text
Local ANNE
   ↓
MITOS research / validation
   ↓
KnowledgeManifest
   ↓
Consent + provenance + trust checks
   ↓
P2P transport (future)
   ↓
Other ANNE installations
```

This is an architectural hypothesis, not a claim that a global ANNE knowledge network already exists.

## Original cognitive loop

```text
User / Task
    │
    ▼
ANNE Core
    │
    ├──► Memory search
    ▼
MITOS
    │
    ├──► heterogeneous AI providers
    ▼
Cognitive Evaluation
    │
    ▼
Cognitive Structure → Persistent Memory
    │
    ▼
Executive ANNE
    │
    ▼
Agency Gate (default deny)
    │
    ▼
Response / Approved Action
```

The original MVP loop remains intact. v0.2 adds privacy-aware knowledge primitives without silently enabling external sharing or autonomous external actions.

## Security notes

- No API keys are stored in the repository.
- Private-vault passphrases are not persisted by the library.
- AES-128-GCM provides authenticated encryption; changing the passphrase requires re-encryption.
- A 128-bit encryption key is not the same thing as a 128-bit user password. ANNE derives the 128-bit key from the user's passphrase.
- Private files must not be placed in a public/shared knowledge directory unless the user intentionally chooses that policy.
- P2P/DHT discovery and automated sharing are **not enabled by this release**.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

The v0.2 test suite covers stable local identity, authenticated private-vault round trips, wrong-passphrase rejection, content addressing, provenance, and explicit sharing scope.

## Research status

ANNE Core is a research prototype. Energy reduction, hallucination reduction, self-improvement, distributed learning effects, and cognitive superiority remain hypotheses requiring controlled experiments.

The v0.2 distributed-knowledge layer is likewise a prototype boundary: it demonstrates the data model and privacy mechanism, not a deployed global knowledge network or a financial Green Money system.
