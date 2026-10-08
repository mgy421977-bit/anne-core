"""ANNE Core adaptive runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from anne_core.runtime.adapters import AdapterPlan, AdapterRegistry
from anne_core.runtime.diagnostics import DiagnosticResult, diagnose
from anne_core.runtime.environment import EnvironmentSnapshot, inspect_environment


@dataclass(frozen=True)
class RuntimeStatus:
    environment: EnvironmentSnapshot
    adapters: tuple[AdapterPlan, ...]
    missing_optional_adapters: tuple[AdapterPlan, ...]
    diagnostics: DiagnosticResult

    @property
    def operational(self) -> bool:
        return self.diagnostics.healthy

    def to_dict(self) -> dict[str, Any]:
        return {
            "environment": self.environment.to_dict(),
            "adapters": [a.__dict__ for a in self.adapters],
            "missing_optional_adapters": [a.__dict__ for a in self.missing_optional_adapters],
            "diagnostics": self.diagnostics.to_dict(),
            "operational": self.operational,
        }


class ANNERuntime:
    """Hardware- and OS-aware runtime boundary for the ANNE cognitive layer.

    The runtime does not promise universal hardware independence. Instead it
    normalizes the host environment and selects trusted adapters so that the
    cognitive architecture can remain above platform-specific details.
    """

    def __init__(self, registry: AdapterRegistry | None = None) -> None:
        self.registry = registry or AdapterRegistry()
        self._status: RuntimeStatus | None = None

    def bootstrap(self) -> RuntimeStatus:
        environment = inspect_environment()
        status = RuntimeStatus(
            environment=environment,
            adapters=tuple(self.registry.plan(environment)),
            missing_optional_adapters=tuple(
                self.registry.required_external_adapters(environment)
            ),
            diagnostics=diagnose(environment),
        )
        self._status = status
        return status

    def status(self) -> RuntimeStatus:
        return self._status or self.bootstrap()

    def recover(self) -> RuntimeStatus:
        """Re-discover the environment after a runtime fault or topology change."""

        return self.bootstrap()

    def capability(self, interface: str) -> bool:
        return any(
            adapter.interface == interface and adapter.status == "available"
            for adapter in self.status().adapters
        )
