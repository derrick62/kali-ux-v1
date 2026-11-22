"""Single-owner gesture input lifecycle shared by gesture-driven features.

The initial XFCE/X11 provider is the existing libinput-tools listener. It is
explicitly started by the user and does not change device permissions or stop
other gesture applications.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable

from kali_ux.features.window_switcher.engine.events import GestureEvent

log = logging.getLogger(__name__)


class GestureInputService:
    """Own one input listener and fan normalized events out to subscribers."""

    def __init__(
        self,
        device: str = "auto",
        fingers: tuple[int, ...] = (3, 4),
        *,
        debug: bool = False,
        use_unaccelerated: bool = False,
        listener_factory=None,
    ):
        self.device = device
        self.fingers = fingers
        self.debug = debug
        self.use_unaccelerated = bool(use_unaccelerated)
        self._listener_factory = listener_factory
        self._listener = None
        self._subscribers: list[Callable[[GestureEvent], None]] = []

    @property
    def running(self) -> bool:
        if self._listener is None:
            return False
        return bool(getattr(self._listener, "running", True))

    def subscribe(self, callback: Callable[[GestureEvent], None]) -> None:
        if callback in self._subscribers:
            return
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[GestureEvent], None]) -> None:
        try:
            self._subscribers.remove(callback)
        except ValueError:
            pass

    def start(self) -> str:
        if self._listener is not None:
            return self.device
        from kali_ux.features.window_switcher.engine.listener import (
            LibinputListener,
            detect_touchpad,
        )

        selected = detect_touchpad(self.device)
        if not os.access(selected, os.R_OK):
            raise PermissionError(
                f"Cannot read {selected}. Review the device permissions; Kali UX will not "
                "change input-group membership or device permissions automatically."
            )
        from kali_ux.features.gesture_control.conflicts import inspect_gesture_providers

        conflicts = [status.name for status in inspect_gesture_providers() if status.may_conflict]
        if conflicts:
            log.warning("Other gesture handlers detected: %s", ", ".join(conflicts))
        factory = self._listener_factory or LibinputListener
        listener = factory(
            selected,
            self.fingers,
            self._publish,
            debug=self.debug,
            use_unaccelerated=self.use_unaccelerated,
        )
        listener.start()
        self.device = selected
        self._listener = listener
        log.info("Gesture input started on %s", selected)
        return selected

    def set_use_unaccelerated(self, enabled: bool) -> None:
        self.use_unaccelerated = bool(enabled)
        if self._listener is not None:
            self._listener.use_unaccelerated = self.use_unaccelerated

    def stop(self) -> None:
        listener, self._listener = self._listener, None
        if listener is not None:
            listener.stop()
            log.info("Gesture input stopped")

    def _publish(self, event: GestureEvent) -> None:
        for callback in tuple(self._subscribers):
            try:
                callback(event)
            except Exception:
                log.exception("Gesture subscriber failed")
