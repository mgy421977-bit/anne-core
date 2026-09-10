"""Anonymous telemetry client.

Fail-open: any error is swallowed so the cognitive loop is never blocked.
Only minimal, non-sensitive fields are ever transmitted.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from anne_core import __version__
from anne_core.telemetry.config import (
    get_or_create_installation_id,
    get_platform_string,
    is_telemetry_enabled,
    mark_notice_shown,
    notice_shown,
)


TELEMETRY_NOTICE = """\
ANNE Core can send anonymous installation statistics.
No prompts, AI responses, credentials or personal data are collected.
Collected fields: installation_id (random UUID), version, platform, timestamp.
Disable at any time with:  ANNE_TELEMETRY=0
or:  python -m anne_core telemetry disable
"""


class TelemetryClient:
    """Minimal, privacy-preserving telemetry client."""

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = (endpoint or os.environ.get("ANNE_TELEMETRY_ENDPOINT", "")).strip()

    def _enabled(self) -> bool:
        return is_telemetry_enabled() and bool(self.endpoint)

    def _payload(self, event: str) -> dict[str, Any]:
        return {
            "event": event,
            "installation_id": get_or_create_installation_id(),
            "anne_version": __version__,
            "platform": get_platform_string(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _post(self, payload: dict[str, Any]) -> bool:
        if not self.endpoint:
            return False
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": f"anne-core/{__version__}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return 200 <= resp.status < 300
        except Exception:
            return False

    def maybe_show_notice(self) -> str | None:
        """Return the notice text the first time; empty thereafter."""
        if notice_shown():
            return None
        mark_notice_shown()
        return TELEMETRY_NOTICE

    def track_installation(self) -> bool:
        """Send a one-time installation event if enabled."""
        if not self._enabled():
            return False
        return self._post(self._payload("installation"))

    def track_version_start(self) -> bool:
        """Optional lightweight start event (same privacy rules)."""
        if not self._enabled():
            return False
        return self._post(self._payload("version_start"))

    def status(self) -> dict[str, Any]:
        """Return non-sensitive status for the CLI."""
        return {
            "enabled": self._enabled(),
            "endpoint_configured": bool(self.endpoint),
            "installation_id": get_or_create_installation_id(),
            "anne_version": __version__,
            "platform": get_platform_string(),
            "notice_shown": notice_shown(),
        }
