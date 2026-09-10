"""Heterogeneous AI provider abstractions."""

from anne_core.providers.base import AIProvider, ProviderResult
from anne_core.providers.mock import MockProvider

__all__ = [
    "AIProvider",
    "ProviderResult",
    "MockProvider",
    "get_available_providers",
]


def get_available_providers() -> list[AIProvider]:
    """Return a list of usable providers.

    Always includes two MockProviders (A and B) so the system works offline.
    Optionally adds real providers when the corresponding API keys are present.
    """
    providers: list[AIProvider] = [
        MockProvider(variant="A"),
        MockProvider(variant="B"),
    ]

    # Optional real providers (lazy import to keep core deps minimal)
    try:
        from anne_core.providers.openai_provider import OpenAIProvider

        p = OpenAIProvider()
        if p.available():
            providers.append(p)
    except Exception:
        pass

    try:
        from anne_core.providers.grok_provider import GrokProvider

        p = GrokProvider()
        if p.available():
            providers.append(p)
    except Exception:
        pass

    return providers
