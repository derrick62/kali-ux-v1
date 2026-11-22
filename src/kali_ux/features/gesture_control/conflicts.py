"""Read-only detection of other desktop gesture handlers."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

PROVIDERS = ("touchegg", "libinput-gestures", "fusuma", "gebaar")


@dataclass(frozen=True)
class GestureProviderStatus:
    name: str
    installed: bool
    running: bool
    autostart_entries: tuple[str, ...] = ()

    @property
    def may_conflict(self) -> bool:
        return self.running or bool(self.autostart_entries)


def _running_processes() -> set[str]:
    found: set[str] = set()
    proc = Path("/proc")
    try:
        entries = list(proc.iterdir())
    except OSError:
        return found
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            raw = (
                (entry / "cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", errors="ignore")
            )
        except OSError:
            continue
        for provider in PROVIDERS:
            if re.search(rf"(?:^|[/\s]){re.escape(provider)}(?:\s|$)", raw):
                found.add(provider)
    return found


def _autostart_matches(provider: str) -> tuple[str, ...]:
    roots = [Path.home() / ".config/autostart", Path("/etc/xdg/autostart")]
    matches: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        try:
            files = root.glob("*.desktop")
            for path in files:
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if re.search(rf"(?i)(?:^|[/\s]){re.escape(provider)}(?:\s|$)", content):
                    matches.append(str(path))
        except OSError:
            continue
    return tuple(sorted(set(matches)))


def inspect_gesture_providers() -> list[GestureProviderStatus]:
    """Report known providers without stopping, disabling or reconfiguring them."""
    running = _running_processes()
    return [
        GestureProviderStatus(
            name=provider,
            installed=shutil.which(provider) is not None,
            running=provider in running,
            autostart_entries=_autostart_matches(provider),
        )
        for provider in PROVIDERS
    ]


def format_conflict_report(statuses: list[GestureProviderStatus]) -> str:
    conflicts = [status for status in statuses if status.may_conflict]
    if not conflicts:
        return "No running or autostart gesture handlers were detected."
    lines = ["Other gesture handlers may overlap with Kali UX:"]
    for status in conflicts:
        state = "running" if status.running else "not running"
        lines.append(f"• {status.name}: {state}")
        lines.extend(f"  Autostart: {entry}" for entry in status.autostart_entries)
    lines.append("Review conflicts manually. Kali UX will not disable other services.")
    return "\n".join(lines)
