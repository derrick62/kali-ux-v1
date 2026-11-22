"""Application-facing model for Control Center feature management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kali_ux.core.config import load_config, save_config
from kali_ux.core.registry import FEATURES
from kali_ux.platform.capabilities import detect


class ControlCenterModel:
    """Coordinates feature metadata, runtime capabilities and user preferences.

    The model deliberately does not start services or mutate desktop settings. A
    feature's enabled preference is separate from its implementation maturity and
    whether the current machine satisfies its runtime requirements.
    """

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path
        self.config = load_config(config_path)
        self.capabilities = detect()
        self._features = {feature.key: feature for feature in FEATURES}

    def refresh_capabilities(self) -> dict[str, object]:
        self.capabilities = detect()
        return self.capabilities

    def rows(self) -> list[dict[str, Any]]:
        rows = []
        for feature in FEATURES:
            settings = self.config["features"].get(feature.key, {})
            enabled = settings.get("enabled", False) is True
            missing = [
                requirement
                for requirement in feature.requires
                if not self._requirement_available(requirement)
            ]
            implemented = feature.status != "planned"
            available = implemented and not missing
            rows.append(
                {
                    "key": feature.key,
                    "title": feature.title,
                    "description": feature.description,
                    "implementation": feature.status,
                    "enabled": enabled,
                    "available": available,
                    "can_enable": available or enabled,
                    "missing_requirements": missing,
                    "requirements": list(feature.requires),
                    "state": self._state(feature.status, enabled, available, missing),
                }
            )
        return rows

    def _requirement_available(self, requirement: str) -> bool:
        key = requirement.lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "x11": "x11",
            "gtk3": "gtk3",
            "libwnck": "libwnck",
            "xfwm4": "xfwm4",
            "xfconf_query": "xfconf_query",
            "xfce4-notifyd-config": "xfce4_notifyd_config",
            "xfce": "xfce",
            "wmctrl": "wmctrl",
            "gio": "gio",
            "libinput": "libinput",
            "input_access": "input_access",
            "gdkx11": "gdkx11",
            "gesture_provider": "gesture_provider",
            "gtk_clipboard": "gtk3",
            "x11_compositor": "compositor",
        }
        capability = aliases.get(key)
        if capability is None:
            return False
        return bool(self.capabilities.get(capability, False))

    @staticmethod
    def _state(implementation, enabled, available, missing):
        if implementation == "planned":
            return "planned"
        if enabled and not available:
            return "enabled · unavailable"
        if enabled:
            return "enabled"
        if not available:
            return "unavailable"
        return "available"

    def set_enabled(self, key: str, enabled: bool) -> dict[str, Any]:
        if key not in self._features:
            raise KeyError(key)
        if type(enabled) is not bool:
            raise TypeError("enabled must be a boolean")
        if enabled:
            row = next(row for row in self.rows() if row["key"] == key)
            if row["implementation"] == "planned":
                raise ValueError(
                    f"Cannot enable {row['title']}: this feature is not implemented yet"
                )
            if not row["available"]:
                requirements = ", ".join(row["missing_requirements"])
                raise ValueError(f"Cannot enable {row['title']}: {requirements}")
        self.config["features"].setdefault(key, {})["enabled"] = enabled
        save_config(self.config, self.config_path)
        return next(row for row in self.rows() if row["key"] == key)

    def get_feature(self, key: str) -> dict[str, Any]:
        for row in self.rows():
            if row["key"] == key:
                return row
        raise KeyError(key)
