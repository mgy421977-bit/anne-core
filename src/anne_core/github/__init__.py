"""GitHub installation support (optional, explicit consent only)."""

from anne_core.github.auth import GitHubAuth, AuthResult
from anne_core.github.client import GitHubClient
from anne_core.github.installer import GitHubInstaller, InstallResult
from anne_core.github.preview import InstallationPreview

__all__ = [
    "GitHubAuth",
    "AuthResult",
    "GitHubClient",
    "GitHubInstaller",
    "InstallResult",
    "InstallationPreview",
]
