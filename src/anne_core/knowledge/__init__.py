"""ANNE distributed knowledge primitives.

The v0.2 layer is local-first: identity, consent, content-addressing and
private-vault encryption are implemented without requiring a central file
store. The central bootstrap is read-only discovery; it does not upload
private data or execute remote code.
"""

from .identity import ANNEIdentity
from .manifest import KnowledgeManifest
from .network import ANNE_REGISTRY_URL, ANNE_REPOSITORY, BootstrapConfig, CentralKnowledgeBootstrap
from .vault import PrivateVault

__all__ = [
    "ANNEIdentity",
    "KnowledgeManifest",
    "PrivateVault",
    "ANNE_REPOSITORY",
    "ANNE_REGISTRY_URL",
    "BootstrapConfig",
    "CentralKnowledgeBootstrap",
]
