"""Agency Gate — default-deny safety boundary.

Any action that would affect the external world requires an explicit
ActionProposal and human approval before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionProposal:
    """Structured proposal that must be approved before execution."""

    action: str
    reason: str
    scope: str = "local"
    risk: str = "unknown"
    evidence: list[str] = field(default_factory=list)
    validation: str = ""
    rollback: str = ""
    authority: str = "user"
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class AgencyGate:
    """Default-deny gate for external-world actions."""

    def __init__(self) -> None:
        self._pending: list[ActionProposal] = []
        self._history: list[ActionProposal] = []

    def propose(self, proposal: ActionProposal) -> ActionProposal:
        """Register a proposal. It is NOT executed."""
        self._pending.append(proposal)
        return proposal

    def approve(self, proposal: ActionProposal) -> bool:
        """Explicit approval. Only after this may execute() succeed."""
        proposal.approved = True
        if proposal in self._pending:
            self._pending.remove(proposal)
        self._history.append(proposal)
        return True

    def deny(self, proposal: ActionProposal) -> bool:
        proposal.approved = False
        if proposal in self._pending:
            self._pending.remove(proposal)
        self._history.append(proposal)
        return False

    def execute(self, proposal: ActionProposal) -> dict[str, Any]:
        """Attempt execution. Raises if not approved (default deny)."""
        if not proposal.approved:
            raise PermissionError(
                f"AgencyGate DENIED action '{proposal.action}'. "
                "Explicit approval required."
            )
        # MVP: no real external side-effects are performed.
        result = {
            "status": "executed-demo",
            "action": proposal.action,
            "message": (
                "Action recorded as approved. No external side-effect performed "
                "in this MVP (safety boundary)."
            ),
        }
        return result

    def pending(self) -> list[ActionProposal]:
        return list(self._pending)

    def history(self) -> list[ActionProposal]:
        return list(self._history)
