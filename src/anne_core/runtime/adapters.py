"""Safe capability and adapter selection for ANNE Core.

ANNE Core may select a built-in adapter automatically. It never downloads or
executes arbitrary driver code as part of discovery. External driver
installation remains an explicitly authorized deployment operation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from anne_core.runtime.environment import EnvironmentSnapshot


@dataclass(frozen=True)
class AdapterPlan:
    name: str
    interface: str
    status: str
    reason: str
    requires_approval: bool = False


@dataclass(frozen=True)
class Adapter:
    name: str
    interface: str
    predicate: Callable[[EnvironmentSnapshot], bool]


class AdapterRegistry:
    """Registry for trusted, built-in runtime adapters."""

    def __init__(self) -> None:
        self._adapters = [
            Adapter("python-runtime", "python", lambda env: bool(env.python_version)),
            Adapter(
                "nvidia-discovery",
                "gpu",
                lambda env: "NVIDIA_GPU" in env.accelerators,
            ),
            Adapter(
                "amd-discovery",
                "gpu",
                lambda env: any(a.startswith("AMD_GPU") for a in env.accelerators),
            ),
            Adapter(
                "drm-render-node",
                "graphics",
                lambda env: "DRM_RENDER_NODE" in env.accelerators,
            ),
            Adapter(
                "network-socket",
                "network",
                lambda env: env.network_available,
            ),
        ]

    def plan(self, environment: EnvironmentSnapshot) -> list[AdapterPlan]:
        plans: list[AdapterPlan] = []
        for adapter in self._adapters:
            if adapter.predicate(environment):
                plans.append(
                    AdapterPlan(
                        adapter.name,
                        adapter.interface,
                        "available",
                        "Trusted built-in adapter matched the discovered environment.",
                    )
                )
        if not any(p.interface == "gpu" for p in plans):
            plans.append(
                AdapterPlan(
                    "cpu-fallback",
                    "compute",
                    "available",
                    "No supported GPU adapter was discovered; CPU execution remains available.",
                )
            )
        return plans

    def required_external_adapters(self, environment: EnvironmentSnapshot) -> list[AdapterPlan]:
        """Describe missing capabilities without attempting installation."""

        plans: list[AdapterPlan] = []
        if not environment.accelerators:
            plans.append(
                AdapterPlan(
                    "optional-accelerator",
                    "gpu-or-npu",
                    "not-installed",
                    "No supported accelerator interface was discovered.",
                    requires_approval=True,
                )
            )
        return plans
