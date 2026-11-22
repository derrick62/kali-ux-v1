"""Explicit, privacy-conscious window geometry snapshots."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from kali_ux.core.paths import DATA_HOME
from kali_ux.platform.window_manager import X11WindowManager

_WINDOW_ID = re.compile(r"0x[0-9a-fA-F]+\Z")


class LayoutMemory:
    def __init__(
        self,
        path: Path | None = None,
        window_manager: X11WindowManager | None = None,
    ):
        self.path = path or DATA_HOME / "layouts.json"
        self.window_manager = window_manager or X11WindowManager()

    @staticmethod
    def _valid_name(name: str) -> str | None:
        if not isinstance(name, str):
            return None
        clean = name.strip()
        if (
            not clean
            or clean in {".", ".."}
            or "/" in clean
            or "\\" in clean
            or len(clean) > 64
            or any(ord(char) < 32 for char in clean)
        ):
            return None
        return clean

    def _read(self) -> dict[str, list[dict[str, object]]]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        if not isinstance(data, dict):
            return {}
        return {
            key: value
            for key, value in data.items()
            if isinstance(key, str) and isinstance(value, list)
        }

    def _write(self, data: dict[str, list[dict[str, object]]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".layouts-", dir=self.path.parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(data, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            self.path.chmod(0o600)
        except Exception:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise

    def capture(self, name: str) -> bool:
        clean_name = self._valid_name(name)
        if clean_name is None:
            return False
        windows = self.window_manager.list_windows()
        if windows is None:
            return False
        # Window titles are deliberately omitted because they can contain private data.
        snapshot = [
            {
                "id": window.window_id,
                "desktop": window.desktop,
                "pid": window.pid,
                "wm_class": window.wm_class,
                "x": window.x,
                "y": window.y,
                "width": window.width,
                "height": window.height,
            }
            for window in windows
        ]
        data = self._read()
        data[clean_name] = snapshot
        try:
            self._write(data)
        except OSError:
            return False
        return True

    def names(self) -> list[str]:
        return sorted(self._read())

    def restore(self, name: str) -> int:
        clean_name = self._valid_name(name)
        if clean_name is None:
            return 0
        windows = self._read().get(clean_name, [])
        current = self.window_manager.list_windows()
        if current is None:
            return 0
        live_windows = {window.window_id: window for window in current}
        restored = 0
        for saved in windows:
            if not isinstance(saved, dict):
                continue
            window_id = saved.get("id")
            if not isinstance(window_id, str) or not _WINDOW_ID.fullmatch(window_id):
                continue
            live = live_windows.get(window_id)
            if live is None:
                continue
            saved_pid = saved.get("pid")
            saved_class = saved.get("wm_class")
            if saved_pid is not None and saved_pid != live.pid:
                continue
            if saved_class and saved_class != live.wm_class:
                continue
            try:
                x, y, width, height = (int(saved[key]) for key in ("x", "y", "width", "height"))
            except (KeyError, TypeError, ValueError):
                continue
            if width <= 0 or height <= 0:
                continue
            desktop = saved.get("desktop")
            if isinstance(desktop, int) and desktop >= 0 and desktop != live.desktop:
                self.window_manager.set_workspace(window_id, desktop)
            restored += int(self.window_manager.set_geometry(window_id, x, y, width, height))
        return restored

    def delete(self, name: str) -> bool:
        clean_name = self._valid_name(name)
        if clean_name is None:
            return False
        data = self._read()
        if clean_name not in data:
            return False
        del data[clean_name]
        try:
            self._write(data)
        except OSError:
            return False
        return True
