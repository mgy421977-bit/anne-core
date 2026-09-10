"""GitHub authentication abstraction.

No credentials are ever stored in source, logs, or cognitive memory.
Tokens are read only from environment variables or an interactive prompt
and never written back to disk by this module.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class AuthResult:
    success: bool
    token: str | None = None
    error: str | None = None
    method: str = "none"


class GitHubAuth:
    """Resolve a GitHub token without persisting it.

    Supported sources (in order):
    1. GITHUB_TOKEN environment variable
    2. GH_TOKEN environment variable (GitHub CLI convention)
    3. Future: device-flow / OAuth (not implemented in MVP)
    """

    def authenticate(self, interactive: bool = False) -> AuthResult:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token and token.strip():
            return AuthResult(success=True, token=token.strip(), method="env")
        if interactive:
            return AuthResult(
                success=False,
                error=(
                    "GitHub authentication required. "
                    "Set GITHUB_TOKEN or GH_TOKEN environment variable "
                    "(classic PAT with repo scope, or fine-grained token with contents:write)."
                ),
                method="none",
            )
        return AuthResult(
            success=False,
            error="GitHub authentication required.",
            method="none",
        )

    def has_token(self) -> bool:
        return bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
