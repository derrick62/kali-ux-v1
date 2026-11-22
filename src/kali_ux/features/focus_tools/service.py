"""Reversible XFCE focus-mode helper; does not kill notifications or processes."""

from __future__ import annotations

from kali_ux.platform.commands import run_command


class FocusMode:
    def __init__(self):
        self._previous: str | None = None
        self._created = False
        self.active = False

    def enable(self) -> bool:
        # Repeated enable requests must not replace the original value with True.
        if self.active:
            return True
        current = run_command(["xfconf-query", "-c", "xfce4-notifyd", "-p", "/do-not-disturb"])
        if not current.available:
            return False
        previous = current.stdout.strip() if current.returncode == 0 else ""
        if previous.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            # Older XFCE notification-daemon configurations may not have
            # created this property yet. Create it explicitly and remove it
            # again when the focus session ends.
            updated = run_command(
                [
                    "xfconf-query",
                    "-c",
                    "xfce4-notifyd",
                    "-p",
                    "/do-not-disturb",
                    "-n",
                    "-t",
                    "bool",
                    "-s",
                    "true",
                ]
            )
            if not updated.available or updated.returncode != 0:
                return False
            self._created = True
            self._previous = None
            self.active = True
            return True
        updated = run_command(
            [
                "xfconf-query",
                "-c",
                "xfce4-notifyd",
                "-p",
                "/do-not-disturb",
                "-n",
                "-t",
                "bool",
                "-s",
                "true",
            ]
        )
        if not updated.available or updated.returncode != 0:
            return False
        self._previous = previous
        self._created = False
        self.active = True
        return True

    def disable(self) -> bool:
        current = run_command(["xfconf-query", "-c", "xfce4-notifyd", "-p", "/do-not-disturb"])
        if (
            current.available
            and current.returncode == 0
            and current.stdout.strip().lower() in {"false", "0", "no"}
        ):
            # Respect a user who manually turned notifications back on during
            # the focus session rather than overwriting that newer choice.
            self.active = False
            self._previous = None
            self._created = False
            return True
        if self._created:
            restored = run_command(
                ["xfconf-query", "-c", "xfce4-notifyd", "-p", "/do-not-disturb", "-r"]
            )
        elif self._previous is not None:
            previous = self._previous.lower() in ("true", "1", "yes")
            restored = run_command(
                [
                    "xfconf-query",
                    "-c",
                    "xfce4-notifyd",
                    "-p",
                    "/do-not-disturb",
                    "-n",
                    "-t",
                    "bool",
                    "-s",
                    str(previous).lower(),
                ]
            )
        else:
            return False
        if not restored.available or restored.returncode != 0:
            # Keep the recovery value so the user can retry.
            return False
        self.active = False
        self._previous = None
        self._created = False
        return True
