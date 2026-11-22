"""Single-handler routing for recognized desktop gesture actions."""

from __future__ import annotations

from collections.abc import Callable


class GestureActionRouter:
    """Route each recognized action to exactly one registered feature handler."""

    def __init__(self):
        self._handlers: dict[str, Callable] = {}

    def register(self, action_name: str, handler: Callable) -> None:
        if not action_name or action_name in self._handlers:
            raise ValueError(f"Gesture action already registered or invalid: {action_name!r}")
        self._handlers[action_name] = handler

    def dispatch(self, action) -> bool:
        handler = self._handlers.get(getattr(action, "name", ""))
        if handler is None:
            return False
        handler(action)
        return True
