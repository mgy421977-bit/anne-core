"""ANNE Core GitHub installer.

All write operations go through Agency Gate (default-deny).
Dry-run never touches GitHub.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anne_core.github.auth import GitHubAuth
from anne_core.github.client import GitHubClient
from anne_core.github.preview import FileChange, InstallationPreview
from anne_core.safety.agency_gate import ActionProposal, AgencyGate


INSTALL_MANIFEST: list[tuple[str, str]] = [
    (
        "anne_core_snippet/README_ANNE.md",
        "# ANNE Core integration\n\nThis repository includes ANNE Core as a cognitive architecture component.\nSee https://github.com/mgy421977-bit/anne-core\n",
    ),
    (
        "anne_core_snippet/.anne_core_installed",
        "anne-core installed\n",
    ),
]


@dataclass
class InstallResult:
    success: bool
    dry_run: bool
    message: str
    preview: InstallationPreview | None = None
    details: dict[str, Any] | None = None


class GitHubInstaller:
    """Install ANNE Core scaffolding into a user-owned GitHub repository."""

    def __init__(
        self,
        client: GitHubClient | None = None,
        gate: AgencyGate | None = None,
    ) -> None:
        self.client = client or GitHubClient()
        self.gate = gate or AgencyGate()
        self.auth = GitHubAuth()

    def build_preview(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
    ) -> InstallationPreview:
        """Inspect target and build a human-readable preview."""
        files_add: list[FileChange] = []
        files_mod: list[FileChange] = []
        notes: list[str] = []

        try:
            self.client.ensure_authenticated()
            for path, _ in INSTALL_MANIFEST:
                existing = self.client.get_file_contents(owner, repo, path, ref=branch)
                if existing is None:
                    files_add.append(FileChange(path=path, action="add"))
                else:
                    files_mod.append(FileChange(path=path, action="modify", detail="would overwrite"))
        except Exception as exc:
            notes.append(f"Could not fully inspect repository: {exc}")
            for path, _ in INSTALL_MANIFEST:
                files_add.append(FileChange(path=path, action="add"))

        risk = "LOW"
        if files_mod:
            risk = "MEDIUM"
            notes.append("Existing files would be modified — review carefully.")

        return InstallationPreview(
            owner=owner,
            repo=repo,
            branch=branch,
            files_to_add=files_add,
            files_to_modify=files_mod,
            files_to_delete=[],
            permissions=["contents:write"],
            risk=risk,
            notes=notes or ["No existing ANNE files detected."],
        )

    def install(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
        dry_run: bool = True,
        approve: bool = False,
    ) -> InstallResult:
        """Run installation flow.

        dry_run=True  → never write, only show preview.
        approve=False → even if not dry_run, Agency Gate will block.
        """
        auth = self.client.ensure_authenticated()
        if not auth.success and not dry_run:
            return InstallResult(
                success=False,
                dry_run=dry_run,
                message=auth.error or "GitHub authentication required.",
            )

        preview = self.build_preview(owner, repo, branch)

        if dry_run:
            return InstallResult(
                success=True,
                dry_run=True,
                message="Dry-run complete. No changes were made to GitHub.",
                preview=preview,
            )

        proposal = ActionProposal(
            action="install_anne_core",
            reason="Install ANNE Core into selected GitHub repository",
            scope=f"{owner}/{repo}",
            risk=preview.risk,
            evidence=[preview.render()],
            validation="User must explicitly approve installation preview",
            rollback="Manual removal of added files; no automatic rollback in MVP",
            authority="user",
        )
        self.gate.propose(proposal)

        if not approve:
            return InstallResult(
                success=False,
                dry_run=False,
                message=(
                    "Agency Gate DENIED. Explicit approval required. "
                    "Re-run with --approve after reviewing the preview."
                ),
                preview=preview,
            )

        self.gate.approve(proposal)

        try:
            self.gate.execute(proposal)
        except PermissionError as exc:
            return InstallResult(
                success=False,
                dry_run=False,
                message=str(exc),
                preview=preview,
            )

        written: list[str] = []
        try:
            for path, content in INSTALL_MANIFEST:
                existing = self.client.get_file_contents(owner, repo, path, ref=branch)
                sha = existing.get("sha") if existing else None
                self.client.create_or_update_file(
                    owner=owner,
                    repo=repo,
                    path=path,
                    content=content,
                    message=f"Install ANNE Core: add {path}",
                    branch=branch,
                    sha=sha,
                )
                written.append(path)
        except Exception as exc:
            return InstallResult(
                success=False,
                dry_run=False,
                message=f"Installation failed: {exc}",
                preview=preview,
                details={"written": written},
            )

        return InstallResult(
            success=True,
            dry_run=False,
            message=f"ANNE Core installed into {owner}/{repo}. Files: {', '.join(written)}",
            preview=preview,
            details={"written": written},
        )
