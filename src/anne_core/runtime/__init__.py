"""ANNE Core adaptive runtime layer.

The runtime layer is responsible for environment discovery, capability
normalization, safe adapter selection, and health diagnostics. It deliberately
does not install arbitrary software or execute untrusted code.
"""

from anne_core.runtime.adapters import AdapterPlan, AdapterRegistry
from anne_core.runtime.environment import EnvironmentSnapshot, inspect_environment
from anne_core.runtime.runtime import ANNERuntime, RuntimeStatus

__all__ = [
    "AdapterPlan",
    "AdapterRegistry",
    "EnvironmentSnapshot",
    "inspect_environment",
    "ANNERuntime",
    "RuntimeStatus",
]
