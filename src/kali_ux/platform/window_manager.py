"""Shared X11/xfwm4 window operations backed by wmctrl.

This adapter deliberately does not replace xfwm4. It sends explicit EWMH
requests through wmctrl and reports whether the request was accepted.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from kali_ux.platform.commands import CommandResult, run_command

_WINDOW_ID = re.compile(r"0x[0-9a-fA-F]+\Z")


@dataclass(frozen=True)
class WindowGeometry:
    window_id: str
    desktop: int
    pid: int
    x: int
    y: int
    width: int
    height: int
    wm_class: str

    @classmethod
    def parse(cls, line: str) -> WindowGeometry | None:
        parts = line.split(None, 9)
        if len(parts) < 9 or not _WINDOW_ID.fullmatch(parts[0]):
            return None
        try:
            desktop, pid, x, y, width, height = map(int, parts[1:7])
        except ValueError:
            return None
        if width <= 0 or height <= 0:
            return None
        return cls(parts[0], desktop, pid, x, y, width, height, parts[7])


class X11WindowManager:
    """Small, injectable adapter for the window operations shared by features."""

    def __init__(self, runner: Callable[..., CommandResult] | None = None):
        self._run = runner or run_command

    def list_windows(self) -> list[WindowGeometry] | None:
        result = self._run(["wmctrl", "-lpGx"])
        if not result.available or result.returncode != 0:
            return None
        windows = []
        for line in result.stdout.splitlines():
            window = WindowGeometry.parse(line)
            if window is not None:
                windows.append(window)
        return windows

    def activate(self, window_id: str) -> bool:
        if not _WINDOW_ID.fullmatch(window_id):
            return False
        result = self._run(["wmctrl", "-i", "-a", window_id])
        return result.available and result.returncode == 0

    def set_geometry(self, window_id: str, x: int, y: int, width: int, height: int) -> bool:
        if not _WINDOW_ID.fullmatch(window_id) or width <= 0 or height <= 0:
            return False
        result = self._run(["wmctrl", "-ir", window_id, "-e", f"0,{x},{y},{width},{height}"])
        return result.available and result.returncode == 0

    def set_workspace(self, window_id: str, desktop: int) -> bool:
        if not _WINDOW_ID.fullmatch(window_id) or desktop < 0:
            return False
        result = self._run(["wmctrl", "-ir", window_id, "-t", str(desktop)])
        return result.available and result.returncode == 0

    def snap_active(self, x: int, y: int, width: int, height: int) -> bool:
        if width <= 0 or height <= 0:
            return False
        unmaximize = self._run(
            ["wmctrl", "-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"]
        )
        if not unmaximize.available or unmaximize.returncode != 0:
            return False
        result = self._run(["wmctrl", "-r", ":ACTIVE:", "-e", f"0,{x},{y},{width},{height}"])
        return result.available and result.returncode == 0
