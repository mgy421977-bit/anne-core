"""ANNE distributed knowledge primitives.

The v0.2 layer is local-first: identity, consent, content-addressing and
private-vault encryption are implemented without requiring a central file
store. P2P transport can be added behind the exchange manifest later.
"""

from .identity import ANNEIdentity
from .manifest import KnowledgeManifest
from .vault import PrivateVault

__all__ = ["ANNEIdentity", "KnowledgeManifest", "PrivateVault"]
