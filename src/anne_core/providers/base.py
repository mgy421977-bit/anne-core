"""Provider abstraction for heterogeneous AI systems."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    """Result returned by an AI provider for a given subtask."""

    provider_name: str
    content: str
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: str | None = None


class AIProvider(ABC):
    """Abstract base for AI providers.

    Implementations must be able to answer a prompt and return a structured
    ProviderResult. No API keys are required for the MockProvider.
    """

    name: str = "base"

    @abstractmethod
    def query(self, prompt: str, context: dict[str, Any] | None = None) -> ProviderResult:
        """Execute a query against this provider.

        Args:
            prompt: The question or subtask text.
            context: Optional shared context (e.g. previous findings).

        Returns:
            ProviderResult with content and metadata.
        """
        ...

    def available(self) -> bool:
        """Return True if this provider can be used (e.g. API key present)."""
        return True
