"""XDG-compliant application paths."""

from __future__ import annotations

import os
from pathlib import Path


def _xdg(name: str, fallback: str) -> Path:
    value = os.environ.get(name)
    if value:
        candidate = Path(value).expanduser()
        if candidate.is_absolute():
            return candidate
    return Path.home() / fallback


CONFIG_HOME = _xdg("XDG_CONFIG_HOME", ".config") / "kali-ux"
DATA_HOME = _xdg("XDG_DATA_HOME", ".local/share") / "kali-ux"
CACHE_HOME = _xdg("XDG_CACHE_HOME", ".cache") / "kali-ux"
_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
RUNTIME_HOME = (
    Path(_runtime_dir).expanduser() / "kali-ux"
    if _runtime_dir and Path(_runtime_dir).expanduser().is_absolute()
    else None
)
