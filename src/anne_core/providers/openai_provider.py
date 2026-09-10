"""Optional OpenAI provider (requires OPENAI_API_KEY)."""

from __future__ import annotations

import os
from typing import Any

from anne_core.providers.base import AIProvider, ProviderResult


class OpenAIProvider(AIProvider):
    """Thin wrapper around the OpenAI chat completions API."""

    name = "openai"

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def available(self) -> bool:
        return bool(self.api_key)

    def query(self, prompt: str, context: dict[str, Any] | None = None) -> ProviderResult:
        if not self.available():
            return ProviderResult(
                provider_name=self.name,
                content="",
                success=False,
                error="OPENAI_API_KEY not set",
            )
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
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
                confidence=0.7,
                metadata={"model": self.model},
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                content="",
                success=False,
                error=str(exc),
            )
