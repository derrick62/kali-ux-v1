from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

DEFAULTS = {
    "fingers": 3,
    "step_px": 80,
    "show_threshold_px": 35,
    "flick_min_px": 40,
    "invert_direction": False,
    "current_workspace_only": True,
    "order": "mru",
    "gesture_timeout": 3.0,
    "use_unaccelerated": False,
    "touchpad_device": "auto",
    "thumbnails": True,
    "thumb_budget_ms": 150,
    "theme": "auto",
    "monitor": "primary",
}


@dataclass
class Config:
    fingers: int = 3
    step_px: int = 80
    show_threshold_px: int = 35
    flick_min_px: int = 40
    invert_direction: bool = False
    current_workspace_only: bool = True
    order: str = "mru"
    gesture_timeout: float = 3.0
    use_unaccelerated: bool = False
    touchpad_device: str = "auto"
    thumbnails: bool = True
    thumb_budget_ms: int = 150
    theme: str = "auto"
    monitor: str = "primary"
    config_path: Path | None = None

    def validate(self):
        for key in (
            "invert_direction",
            "current_workspace_only",
            "use_unaccelerated",
            "thumbnails",
        ):
            if type(getattr(self, key)) is not bool:
                raise ValueError(f"{key} must be a boolean")
        if type(self.fingers) is not int or not 2 <= self.fingers <= 5:
            raise ValueError("fingers must be between 2 and 5")
        for key in ("step_px", "show_threshold_px", "flick_min_px", "thumb_budget_ms"):
            if type(getattr(self, key)) is not int or getattr(self, key) <= 0:
                raise ValueError(f"{key} must be greater than zero")
        if (
            isinstance(self.gesture_timeout, bool)
            or not isinstance(self.gesture_timeout, (int, float))
            or self.gesture_timeout <= 0
        ):
            raise ValueError("gesture_timeout must be a positive number")
        if not isinstance(self.touchpad_device, str) or not self.touchpad_device:
            raise ValueError("touchpad_device must be a non-empty string")
        if self.order not in {"mru", "fixed"}:
            raise ValueError("order must be 'mru' or 'fixed'")
        if self.theme not in {"dark", "light", "auto"}:
            raise ValueError("theme must be 'dark', 'light' or 'auto'")
        if self.monitor not in {"primary", "pointer"}:
            raise ValueError("monitor must be 'primary' or 'pointer'")
        return self


def default_config_path():
    configured = os.environ.get("XDG_CONFIG_HOME")
    config_home = Path(configured).expanduser() if configured else Path.home() / ".config"
    if not config_home.is_absolute():
        config_home = Path.home() / ".config"
    return config_home / "swipeswitch" / "config.toml"


def _write_default_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".config-", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(_default_text())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        path.chmod(0o600)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _default_text():
    return """# SwipeSwitch core preview configuration
touchpad_device = "auto"
step_px = 80
show_threshold_px = 35
flick_min_px = 40
invert_direction = false
current_workspace_only = true
order = "mru"
gesture_timeout = 3.0
use_unaccelerated = false
thumbnails = true
thumb_budget_ms = 150
theme = "auto"
monitor = "primary"
"""


def load_config(path=None):
    config_path = Path(path).expanduser() if path else default_config_path()
    if not config_path.exists():
        try:
            _write_default_config(config_path)
        except OSError as exc:
            log.warning("Could not create config file: %s", exc)

    raw = {}
    if config_path.exists():
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError as exc:
                raise RuntimeError("Python 3.11+ is required for TOML parsing.") from exc
        try:
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            log.warning("Invalid config (%s); using defaults", exc)

    values = {key: raw.get(key, value) for key, value in DEFAULTS.items()}
    cfg = Config(**values, config_path=config_path)
    try:
        return cfg.validate()
    except (TypeError, ValueError) as exc:
        log.warning("Invalid config value (%s); using defaults", exc)
        return Config(config_path=config_path).validate()
