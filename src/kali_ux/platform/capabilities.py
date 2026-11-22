"""Read-only runtime capability detection; never changes system settings."""

from __future__ import annotations

import os
import re
import shutil
import subprocess


def _gtk_capabilities() -> tuple[bool, bool]:
    """Check GTK3 and libwnck introspection namespaces without loading the UI."""
    try:
        import gi
    except ImportError:
        return False, False

    try:
        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        gi.require_version("Pango", "1.0")
        from gi.repository import Gdk, Gtk, Pango  # noqa: F401
    except (ValueError, gi.RepositoryError):
        return False, False

    try:
        gi.require_version("Wnck", "3.0")
        from gi.repository import Wnck  # noqa: F401
    except (ValueError, gi.RepositoryError):
        return True, False
    return True, True


def _gdkx11_capability() -> bool:
    try:
        import gi

        gi.require_version("GdkX11", "3.0")
        from gi.repository import GdkX11  # noqa: F401
    except (ImportError, ValueError, AttributeError):
        return False
    return True


def _gesture_device_access() -> bool:
    """Check whether the current user can read a libinput gesture-capable device."""
    if not shutil.which("libinput"):
        return False
    try:
        output = subprocess.run(
            ["libinput", "list-devices"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    candidates: list[tuple[int, str]] = []
    for block in re.split(r"\n\s*\n", output):
        capabilities = re.search(r"(?im)^\s*Capabilities:\s*(.+)$", block)
        kernel = re.search(r"(?im)^\s*Kernel:\s*(/dev/input/event\d+)\b", block)
        if not capabilities or not kernel:
            continue
        names = set(capabilities.group(1).lower().split())
        if not {"pointer", "gesture"}.issubset(names):
            continue
        device_name = re.search(r"(?im)^\s*Device:\s*(.+)$", block)
        score = 2 if device_name and "touchpad" in device_name.group(1).lower() else 1
        candidates.append((score, kernel.group(1)))
    candidates.sort(reverse=True)
    return bool(candidates and os.access(candidates[0][1], os.R_OK))


def detect() -> dict[str, object]:
    session = os.environ.get("XDG_SESSION_TYPE", "unknown")
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "unknown")
    gtk3, libwnck = _gtk_capabilities()
    gdkx11 = _gdkx11_capability() if gtk3 else False
    input_access = _gesture_device_access()
    providers = ("touchegg", "libinput-gestures", "fusuma", "gebaar")
    return {
        "session_type": session,
        "desktop": desktop,
        "x11": bool(os.environ.get("DISPLAY")) and session.lower() != "wayland",
        "wayland": session.lower() == "wayland",
        "xfce": "xfce" in desktop.lower(),
        "xfwm4": bool(shutil.which("xfwm4")),
        "gtk3": gtk3,
        "libwnck": libwnck,
        "gdkx11": gdkx11,
        "wmctrl": bool(shutil.which("wmctrl")),
        "gio": bool(shutil.which("gio")),
        "xdotool": bool(shutil.which("xdotool")),
        "libinput": bool(shutil.which("libinput")),
        "input_access": input_access,
        "xclip": bool(shutil.which("xclip")),
        "xfconf_query": bool(shutil.which("xfconf-query")),
        "xfce4_notifyd_config": bool(shutil.which("xfce4-notifyd-config")),
        "gesture_provider": any(shutil.which(provider) for provider in providers),
        # Compositor-aware preview support is not implemented yet. Do not infer it
        # merely from the presence of a running compositor.
        "compositor": False,
    }
