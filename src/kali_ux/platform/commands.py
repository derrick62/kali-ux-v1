"""Safe wrappers for synchronous and detached desktop commands.

Never invoke a shell. Use :func:`run_command` for short-lived queries/actions and
:func:`start_command` for graphical applications that must outlive the caller.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    available: bool
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    started: bool = False


def _resolve(argv: Sequence[str]) -> tuple[list[str] | None, str]:
    if isinstance(argv, (str, bytes)):
        return None, "command arguments must be a sequence of strings, not a string"
    if not argv or not isinstance(argv[0], str) or not argv[0]:
        return None, "command not specified"
    if any(not isinstance(arg, str) for arg in argv):
        return None, "command arguments must be strings"
    executable = shutil.which(argv[0])
    if executable is None:
        return None, f"{argv[0]} not found"
    return [executable, *argv[1:]], ""


def run_command(argv: Sequence[str], timeout: float = 3.0) -> CommandResult:
    """Run a short-lived command and capture its output."""
    command, error = _resolve(argv)
    if command is None:
        return CommandResult(False, stderr=error)
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CommandResult(True, process.returncode, process.stdout, process.stderr)
    except subprocess.TimeoutExpired:
        return CommandResult(True, None, stderr=f"command timed out after {timeout:g}s")
    except OSError as exc:
        return CommandResult(True, None, stderr=str(exc))


def start_command(
    argv: Sequence[str],
    *,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Start a graphical/long-running command without waiting for its window.

    The child receives no inherited standard streams and starts a new session so
    closing the Control Center does not terminate the launched settings app.
    A successful result means process creation succeeded, not that the app later
    completed startup successfully.
    """
    command, error = _resolve(argv)
    if command is None:
        return CommandResult(False, stderr=error)
    try:
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            start_new_session=True,
            close_fds=True,
        )
        return CommandResult(True, started=True)
    except OSError as exc:
        return CommandResult(True, None, stderr=str(exc))
