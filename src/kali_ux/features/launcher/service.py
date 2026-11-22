"""XDG desktop-entry discovery and safe application launching."""

from __future__ import annotations

import configparser
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from kali_ux.platform.commands import start_command


@dataclass(frozen=True)
class AppEntry:
    name: str
    command: str
    path: str
    icon: str = ""
    description: str = ""
    categories: tuple[str, ...] = ()


class ApplicationLauncher:
    def __init__(self):
        self.entries = self._scan()

    def _scan(self) -> list[AppEntry]:
        entries: dict[str, AppEntry] = {}
        seen_files: set[str] = set()
        default_home = Path.home() / ".local/share"
        configured_home = os.environ.get("XDG_DATA_HOME")
        data_home = Path(configured_home).expanduser() if configured_home else default_home
        if not data_home.is_absolute():
            data_home = default_home
        data_dirs = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
        system_roots = tuple(
            candidate / "applications"
            for root in data_dirs.split(":")
            if root
            for candidate in (Path(root).expanduser(),)
            if candidate.is_absolute()
        )
        roots = (data_home / "applications",) + system_roots
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*.desktop"):
                # A user-local Hidden/NoDisplay entry must mask a system entry
                # with the same desktop-file ID, not reveal it as a fallback.
                desktop_id = path.relative_to(root).as_posix().replace("/", "-")
                if desktop_id in seen_files:
                    continue
                seen_files.add(desktop_id)
                parser = configparser.ConfigParser(interpolation=None, strict=False)
                parser.optionxform = str
                try:
                    parser.read(path, encoding="utf-8")
                    values = parser["Desktop Entry"]
                except (OSError, KeyError, configparser.Error):
                    continue
                name = values.get("Name")
                command = values.get("Exec")
                if (
                    not name
                    or not command
                    or values.get("Type", "Application") != "Application"
                    or values.get("NoDisplay", "false").lower() == "true"
                    or values.get("Hidden", "false").lower() == "true"
                ):
                    continue
                try_exec = values.get("TryExec")
                if try_exec and not (
                    (Path(try_exec).is_absolute() and os.access(try_exec, os.X_OK))
                    or shutil.which(try_exec)
                ):
                    continue
                current_desktops = {
                    item for item in os.environ.get("XDG_CURRENT_DESKTOP", "").split(":") if item
                }
                only_show = {item for item in values.get("OnlyShowIn", "").split(";") if item}
                not_show = {item for item in values.get("NotShowIn", "").split(";") if item}
                if (
                    only_show and not current_desktops.intersection(only_show)
                ) or current_desktops.intersection(not_show):
                    continue
                categories = tuple(
                    category for category in values.get("Categories", "").split(";") if category
                )
                entries[desktop_id] = AppEntry(
                    name=name,
                    command=command,
                    path=str(path),
                    icon=values.get("Icon", ""),
                    description=values.get("Comment", ""),
                    categories=categories,
                )
        return sorted(entries.values(), key=lambda item: item.name.casefold())

    def refresh(self) -> int:
        """Rescan XDG application directories and return the new entry count."""
        self.entries = self._scan()
        return len(self.entries)

    def search(self, query: str) -> list[AppEntry]:
        needle = query.casefold().strip()
        return sorted(
            (
                entry
                for entry in self.entries
                if needle in entry.name.casefold()
                or needle in entry.description.casefold()
                or any(needle in category.casefold() for category in entry.categories)
            ),
            key=lambda entry: entry.name.casefold(),
        )[:80]

    def launch(self, entry: AppEntry) -> bool:
        result = start_command(["gio", "launch", entry.path])
        return result.started
