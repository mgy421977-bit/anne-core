"""Read-only bootstrap connection for ANNE installations.

Every ANNE installation can discover the shared knowledge registry from the
project repository. This layer intentionally does not upload private data,
execute downloaded code, or enable P2P transport. It is a bootstrap/discovery
channel only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen


ANNE_REPOSITORY = "https://github.com/mgy421977-bit/anne-core"
ANNE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/mgy421977-bit/anne-core/main/"
    "knowledge/registry.json"
)


@dataclass(frozen=True)
class BootstrapConfig:
    repository: str = ANNE_REPOSITORY
    registry_url: str = ANNE_REGISTRY_URL
    mode: str = "read-only"
    upload_private_data: bool = False
    execute_remote_code: bool = False


class CentralKnowledgeBootstrap:
    """Fetch the public ANNE knowledge registry without sharing local data."""

    def __init__(self, config: BootstrapConfig | None = None, timeout: float = 10.0):
        self.config = config or BootstrapConfig()
        self.timeout = timeout

    def fetch_registry(self) -> dict:
        request = Request(
            self.config.registry_url,
            headers={"User-Agent": "ANNE-Core/0.2"},
            method="GET",
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8")
        registry = json.loads(payload)
        if not isinstance(registry, dict):
            raise ValueError("ANNE registry must be a JSON object")
        return registry

    def bootstrap(self) -> dict:
        """Return the public registry; never uploads or executes remote content."""
        return self.fetch_registry()
