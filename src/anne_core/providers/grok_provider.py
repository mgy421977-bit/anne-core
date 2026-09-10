"""Optional xAI / Grok provider (OpenAI-compatible API)."""

from __future__ import annotations

import os
from typing import Any

from anne_core.providers.base import AIProvider, ProviderResult


class GrokProvider(AIProvider):
    """Thin wrapper around the xAI Grok API (OpenAI-compatible)."""

    name = "grok"

    def __init__(self) -> None:
        self.api_key = os.environ.get("XAI_API_KEY", "")
        self.base_url = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")
        self.model = os.environ.get("XAI_MODEL", "grok-3")

    def available(self) -> bool:
        return bool(self.api_key)

    def query(self, prompt: str, context: dict[str, Any] | None = None) -> ProviderResult:
        if not self.available():
            return ProviderResult(
                provider_name=self.name,
                content="",
                success=False,
                error="XAI_API_KEY not set",
            )
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            messages = [{"role": "user", "content": prompt}]
            if context:
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": f"Context: {context}",
                    },
                )
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            content = resp.choices[0].message.content or ""
            return ProviderResult(
                provider_name=self.name,
                content=content,
                confidence=0.75,
                metadata={"model": self.model, "base_url": self.base_url},
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                content="",
                success=False,
                error=str(exc),
            )
