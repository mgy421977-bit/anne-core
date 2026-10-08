"""Runtime health and recovery diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anne_core.runtime.environment import EnvironmentSnapshot


@dataclass(frozen=True)
class DiagnosticResult:
    healthy: bool
    checks: dict[str, bool]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "checks": dict(self.checks),
            "warnings": list(self.warnings),
        }


def diagnose(environment: EnvironmentSnapshot) -> DiagnosticResult:
    checks = {
        "python_runtime": bool(environment.python_version),
        "cpu": environment.cpu_count > 0,
        "filesystem": bool(environment.executable),
    }
    warnings: list[str] = []
    if environment.memory_bytes is None:
        warnings.append("Physical memory could not be measured.")
    if not environment.network_available:
        warnings.append("Network unavailable; offline mode is active.")
    return DiagnosticResult(
        healthy=all(checks.values()),
        checks=checks,
        warnings=tuple(warnings),
    )
