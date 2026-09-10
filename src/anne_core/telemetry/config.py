"""Local configuration for anonymous installation identity and telemetry preferences.

Privacy principles:
- No usernames, emails, tokens, prompts, or AI content are stored or sent.
- Installation ID is a random UUID used only to avoid double-counting installs.
- Telemetry is OFF by default unless the user has not disabled it and an
  endpoint is configured. Explicit notice is shown on first run.
"""

from __future__ import annotations

import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any


def _config_dir() -> Path:
    """Return a per-user config directory (XDG-style on Unix)."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "anne-core"
    d.mkdir(parents=True, exist_ok=True)
    return d


def config_path() -> Path:
    return _config_dir() / "config.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(data: dict[str, Any]) -> None:
    path = config_path()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_or_create_installation_id() -> str:
    """Return a stable anonymous installation UUID.

    Generated once and stored locally. Never contains personal data.
    """
    cfg = load_config()
    iid = cfg.get("installation_id")
    if isinstance(iid, str) and len(iid) >= 32:
        return iid
    iid = str(uuid.uuid4())
    cfg["installation_id"] = iid
    save_config(cfg)
    return iid


def is_telemetry_enabled() -> bool:
    """Telemetry is enabled only when:
    - ANNE_TELEMETRY is not "0" / "false" / "off"
    - and a telemetry endpoint is configured (or a default is present).
    Default preference is opt-out friendly: if the env var is unset we still
    respect a local config flag, and we never send without an endpoint.
    """
    env = os.environ.get("ANNE_TELEMETRY", "").strip().lower()
    if env in ("0", "false", "no", "off", "disabled"):
        return False
    cfg = load_config()
    if cfg.get("telemetry_disabled") is True:
        return False
    # Endpoint must exist; otherwise nothing is sent.
    endpoint = os.environ.get("ANNE_TELEMETRY_ENDPOINT", "").strip()
    if not endpoint:
        return False
    return True


def set_telemetry_disabled(disabled: bool = True) -> None:
    cfg = load_config()
    cfg["telemetry_disabled"] = bool(disabled)
    save_config(cfg)


def get_platform_string() -> str:
    return f"{platform.system()}-{platform.machine()}-{platform.python_version()}"


def notice_shown() -> bool:
    return bool(load_config().get("telemetry_notice_shown"))


def mark_notice_shown() -> None:
    cfg = load_config()
    cfg["telemetry_notice_shown"] = True
    save_config(cfg)
