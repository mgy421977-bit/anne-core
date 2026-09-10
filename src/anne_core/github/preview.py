"""Installation preview model — shown before any write."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FileChange:
    path: str
    action: str  # "add" | "modify" | "delete"
    detail: str = ""


@dataclass
class InstallationPreview:
    owner: str
    repo: str
    branch: str = "main"
    files_to_add: list[FileChange] = field(default_factory=list)
    files_to_modify: list[FileChange] = field(default_factory=list)
    files_to_delete: list[FileChange] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    risk: str = "LOW"
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            "ANNE Core Installation Preview",
            "",
            f"Target:  {self.owner}/{self.repo}  (branch: {self.branch})",
            "",
            "Files to add:",
        ]
        if self.files_to_add:
            for f in self.files_to_add:
                lines.append(f"  + {f.path}")
        else:
            lines.append("  (none)")

        lines.append("")
        lines.append("Files to modify:")
        if self.files_to_modify:
            for f in self.files_to_modify:
                lines.append(f"  ~ {f.path}")
        else:
            lines.append("  (none)")

        lines.append("")
        lines.append("Files to delete:")
        if self.files_to_delete:
            for f in self.files_to_delete:
                lines.append(f"  - {f.path}")
        else:
            lines.append("  NONE")

        lines.append("")
        lines.append("Permissions required:")
        for p in self.permissions or ["contents:write"]:
            lines.append(f"  - {p}")

        lines.append("")
        lines.append(f"Risk: {self.risk}")
        if self.notes:
            lines.append("")
            lines.append("Notes:")
            for n in self.notes:
                lines.append(f"  • {n}")

        lines.append("")
        lines.append("[Cancel]  [Approve Installation]")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "owner": self.owner,
            "repo": self.repo,
            "branch": self.branch,
            "files_to_add": [f.path for f in self.files_to_add],
            "files_to_modify": [f.path for f in self.files_to_modify],
            "files_to_delete": [f.path for f in self.files_to_delete],
            "permissions": self.permissions,
            "risk": self.risk,
            "notes": self.notes,
        }
