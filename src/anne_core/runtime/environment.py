"""Portable environment and hardware discovery for ANNE Core."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EnvironmentSnapshot:
    """A normalized, dependency-light description of the current runtime."""

    os_name: str
    os_release: str
    architecture: str
    machine: str
    python_version: str
    cpu_count: int
    memory_bytes: int | None
    executable: str
    available_commands: tuple[str, ...]
    accelerators: tuple[str, ...]
    network_available: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _memory_bytes() -> int | None:
    """Read physical memory without requiring psutil."""

    try:
        if sys.platform.startswith("linux"):
            for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
        if sys.platform == "darwin":
            import subprocess

            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(out.strip())
        if sys.platform.startswith("win"):
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_ulong),
                    ("memory_load", ctypes.c_ulong),
                    ("total_phys", ctypes.c_ulonglong),
                    ("avail_phys", ctypes.c_ulonglong),
                    ("total_page", ctypes.c_ulonglong),
                    ("avail_page", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong),
                    ("avail_virtual", ctypes.c_ulonglong),
                    ("avail_extended", ctypes.c_ulonglong),
                ]

            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.total_phys)
    except (OSError, ValueError, subprocess.SubprocessError if "subprocess" in locals() else OSError):
        return None
    return None


def _accelerators() -> tuple[str, ...]:
    """Detect well-known accelerator interfaces without importing vendor SDKs."""

    found: list[str] = []
    commands = {
        "nvidia-smi": "NVIDIA_GPU",
        "rocminfo": "AMD_GPU",
        "xpu-smi": "INTEL_GPU",
    }
    for command, label in commands.items():
        if shutil.which(command):
            found.append(label)

    # Linux device nodes are useful hints, not proof of usable acceleration.
    if sys.platform.startswith("linux"):
        if Path("/dev/kfd").exists() and "AMD_GPU" not in found:
            found.append("AMD_GPU_HINT")
        if list(Path("/dev").glob("dri/renderD*")):
            found.append("DRM_RENDER_NODE")

    return tuple(sorted(set(found)))


def _network_available() -> bool:
    """Return whether a basic hostname lookup succeeds."""

    try:
        import socket

        socket.gethostbyname("localhost")
        return True
    except OSError:
        return False


def inspect_environment() -> EnvironmentSnapshot:
    """Discover the execution environment using only standard-library APIs."""

    commands = ("python", "git", "curl", "ssh")
    return EnvironmentSnapshot(
        os_name=platform.system() or "unknown",
        os_release=platform.release() or "unknown",
        architecture=platform.architecture()[0],
        machine=platform.machine() or "unknown",
        python_version=platform.python_version(),
        cpu_count=os.cpu_count() or 1,
        memory_bytes=_memory_bytes(),
        executable=sys.executable,
        available_commands=tuple(c for c in commands if shutil.which(c)),
        accelerators=_accelerators(),
        network_available=_network_available(),
    )
