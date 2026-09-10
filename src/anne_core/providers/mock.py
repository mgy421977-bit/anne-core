"""Deterministic MockProvider for offline / no-API-key operation."""

from __future__ import annotations

import hashlib
from typing import Any

from anne_core.providers.base import AIProvider, ProviderResult


_MOCK_KNOWLEDGE: dict[str, tuple[str, float]] = {
    "urban heat islands": (
        "Urban heat islands (UHI) are primarily caused by: "
        "(1) replacement of natural land cover with heat-absorbing surfaces "
        "(asphalt, concrete, dark roofs); "
        "(2) reduced vegetation and evapotranspiration; "
        "(3) anthropogenic heat from vehicles, HVAC and industry; "
        "(4) altered urban geometry that traps long-wave radiation; "
        "(5) air pollution that can enhance local greenhouse effects. "
        "Secondary factors include low surface albedo and limited wind corridors.",
        0.85,
    ),
    "causes of urban heat": (
        "Main drivers of the urban heat island effect include surface materials "
        "with high thermal mass and low albedo, loss of green space, waste heat "
        "from human activity, and canyon-like street geometry that reduces "
        "radiative cooling at night.",
        0.80,
    ),
    "heat island": (
        "The urban heat island phenomenon arises from the combination of "
        "impervious surfaces, reduced latent heat flux from vegetation, "
        "anthropogenic heat emissions, and three-dimensional urban form.",
        0.78,
    ),
    "climate change": (
        "Climate change is driven by increased concentrations of greenhouse "
        "gases (CO2, CH4, N2O, fluorinated gases) from fossil fuel combustion, "
        "land-use change and industrial processes, amplifying the natural "
        "greenhouse effect.",
        0.82,
    ),
    "default": (
        "Based on available knowledge, the topic involves multiple interacting "
        "factors that require careful decomposition and cross-source comparison. "
        "Further exploration of primary literature is recommended for higher confidence.",
        0.55,
    ),
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _select_answer(prompt: str) -> tuple[str, float]:
    """Select a deterministic answer based on keyword overlap."""
    norm = _normalize(prompt)
    best_key = "default"
    best_score = 0
    for key in _MOCK_KNOWLEDGE:
        if key == "default":
            continue
        key_tokens = set(key.split())
        prompt_tokens = set(norm.split())
        overlap = len(key_tokens & prompt_tokens)
        if overlap > best_score:
            best_score = overlap
            best_key = key
    return _MOCK_KNOWLEDGE[best_key]


class MockProvider(AIProvider):
    """Deterministic provider that never calls external APIs.

    Guarantees reproducible output for the same prompt so that the
    cognitive loop and memory-reuse demo can be demonstrated offline.
    """

    name = "mock"

    def __init__(self, variant: str = "A") -> None:
        self.variant = variant
        self.name = f"mock-{variant}"

    def query(self, prompt: str, context: dict[str, Any] | None = None) -> ProviderResult:
        content, confidence = _select_answer(prompt)

        if self.variant == "B":
            content = (
                content.replace("primarily caused by", "largely driven by")
                .replace("Main drivers", "Key contributing factors")
                .replace("arises from", "results from")
            )
            confidence = max(0.4, confidence - 0.12)

        seed = int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16) % 100

        return ProviderResult(
            provider_name=self.name,
            content=content,
            confidence=confidence,
            metadata={
                "variant": self.variant,
                "seed": seed,
                "source": "mock-knowledge-base",
                "tokens_approx": len(content.split()),
            },
            success=True,
        )

    def available(self) -> bool:
        return True
