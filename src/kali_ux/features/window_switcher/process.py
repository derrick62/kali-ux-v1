"""Managed user-session lifecycle for the SwipeSwitch process."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
from collections.abc import Callable
from pathlib import Path

from kali_ux.core.paths import DATA_HOME


class SwipeSwitchProcess:
    def __init__(
        self,
        executable: str = "kali-ux-swipeswitch",
        log_path: Path | None = None,
        *,
        popen: Callable = subprocess.Popen,
        which: Callable = shutil.which,
    ):
        self.executable = executable
        self.log_path = log_path or DATA_HOME / "logs" / "swipeswitch.log"
        self._popen = popen
        self._which = which
        self._process = None

    @property
    def running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def has_process(self) -> bool:
        return self._process is not None

    def start(self) -> tuple[bool, str]:
        if self.running:
            return False, "SwipeSwitch is already running."
        if self._process is not None:
            self.collect_exit_code()
        executable = self._which(self.executable)
        if executable is None:
            return False, f"Could not find {self.executable}. Install Kali UX first."

        output = subprocess.DEVNULL
        stream = None
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            stream = self.log_path.open("a", encoding="utf-8")
            os.chmod(self.log_path, 0o600)
            output = stream
        except OSError:
            if stream is not None:
                stream.close()
            stream = None
        try:
            self._process = self._popen(
                [executable],
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
        except OSError as exc:
            self._process = None
            return False, f"Could not start SwipeSwitch: {exc}"
        finally:
            if stream is not None:
                stream.close()
        message = (
            "SwipeSwitch started. Its log is stored under Kali UX user data."
            if stream is not None
            else "SwipeSwitch started, but its log file could not be opened."
        )
        return True, message

    def collect_exit_code(self) -> int | None:
        if self._process is None:
            return None
        returncode = self._process.poll()
        if returncode is not None:
            self._process = None
        return returncode

    def reload(self) -> bool:
        if not self.running or not hasattr(signal, "SIGHUP"):
            return False
        try:
            self._process.send_signal(signal.SIGHUP)
            return True
        except OSError:
            return False

    def terminate(self) -> bool:
        if not self.running:
            return False
        try:
            self._process.terminate()
            return True
        except OSError:
            return False

    def kill(self) -> bool:
        if not self.running:
            return False
        try:
            self._process.kill()
            return True
        except OSError:
            return False

    def shutdown(self, timeout: float = 1.5) -> int | None:
        if self._process is None:
            return None
        process = self._process
        if process.poll() is None:
            try:
                process.terminate()
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    returncode = process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    returncode = process.poll()
                except OSError:
                    returncode = process.poll()
            except OSError:
                returncode = process.poll()
        else:
            returncode = process.poll()
        self._process = None
        return returncode
