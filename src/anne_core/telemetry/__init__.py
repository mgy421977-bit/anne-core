"""Anonymous installation telemetry (opt-out, fail-open, privacy-by-design)."""

from anne_core.telemetry.client import TelemetryClient, TELEMETRY_NOTICE
from anne_core.telemetry.config import (
    get_or_create_installation_id,
    is_telemetry_enabled,
    set_telemetry_disabled,
)

__all__ = [
    "TelemetryClient",
    "TELEMETRY_NOTICE",
    "get_or_create_installation_id",
    "is_telemetry_enabled",
    "set_telemetry_disabled",
]
