"""Pure, desktop-independent recognition for SwipeSwitch gestures."""

from __future__ import annotations

import time
from dataclasses import dataclass

from .events import GestureEvent


@dataclass(frozen=True)
class GestureAction:
    name: str
    fingers: int
    direction: str | None = None
    steps: int = 0


class GestureRecognizer:
    """Classify one-finger-count swipe lifecycle into product-level actions.

    libinput reports deltas, not absolute positions. We therefore accumulate
    the full gesture and emit window-selection steps as thresholds are crossed.
    A gesture is classified once; it can never be routed to two features.
    """

    def __init__(
        self,
        threshold_px: float = 35,
        step_px: float = 80,
        horizontal_dominance: float = 1.25,
        flick_min_px: float = 40,
        invert_direction: bool = False,
    ):
        self.threshold_px = float(threshold_px)
        self.step_px = float(step_px)
        self.horizontal_dominance = float(horizontal_dominance)
        self.flick_min_px = float(flick_min_px)
        self.invert_direction = bool(invert_direction)
        self.reset()

    def reset(self):
        self.fingers = 0
        self.dx = 0.0
        self.dy = 0.0
        self.axis = None
        self.direction = None
        self.last_step = 0
        self.cancelled = False
        self.started_at = None
        self.last_activity = None

    def handle(self, event: GestureEvent) -> list[GestureAction]:
        actions: list[GestureAction] = []
        if event.kind == "begin":
            # A new BEGIN before the previous END means the old sequence was
            # interrupted. Close any visible switcher before accepting it.
            if self.fingers == 3 and self.axis == "horizontal":
                actions.append(GestureAction("switch_cancel", 3, self.direction))
            self.reset()
            if event.fingers not in (3, 4):
                return actions
            self.fingers = event.fingers
            self.started_at = time.monotonic()
            self.last_activity = self.started_at
            return actions

        if self.fingers not in (3, 4):
            return actions
        if event.fingers != self.fingers:
            # Finger-count changes invalidate the current gesture immediately;
            # do not leave an overlay waiting for the timeout to expire.
            if self.fingers == 3 and self.axis == "horizontal":
                actions.append(GestureAction("switch_cancel", 3, self.direction))
            self.reset()
            return actions

        if event.kind == "update":
            self.last_activity = time.monotonic()
            self.dx += event.dx
            self.dy += event.dy
            if self.axis is None:
                if max(abs(self.dx), abs(self.dy)) < self.threshold_px:
                    return actions
                if abs(self.dx) >= abs(self.dy) * self.horizontal_dominance:
                    self.axis = "horizontal"
                    logical_dx = -self.dx if self.invert_direction else self.dx
                    self.direction = "left" if logical_dx < 0 else "right"
                    if self.fingers == 3:
                        actions.append(GestureAction("switch_begin", 3, self.direction))
                elif abs(self.dy) >= abs(self.dx) * self.horizontal_dominance:
                    self.axis = "vertical"
                    self.direction = "up" if self.dy < 0 else "down"
                else:
                    # A diagonal gesture remains undecided until it becomes
                    # sufficiently dominant or ends; ambiguous gestures do nothing.
                    return actions

            if self.axis == "horizontal" and self.fingers in (3, 4):
                # Both horizontal gestures consume distance incrementally.
                # Reversals therefore take effect before finger-up.
                logical_dx = -self.dx if self.invert_direction else self.dx
                step = int(logical_dx / self.step_px)
                delta = step - self.last_step
                if delta:
                    move_direction = "left" if delta < 0 else "right"
                    action_name = "switch_move" if self.fingers == 3 else "workspace"
                    actions.append(
                        GestureAction(action_name, self.fingers, move_direction, abs(delta))
                    )
                    self.last_step = step
            return actions

        if event.kind == "end":
            if event.cancelled:
                if self.fingers == 3 and self.axis == "horizontal":
                    actions.append(GestureAction("switch_cancel", 3, self.direction))
            elif self.axis == "horizontal" and self.fingers == 4:
                # A deliberate short flick should move one workspace even if
                # it did not cross a full repeat interval during updates.
                if self.last_step == 0 and abs(self.dx) >= self.flick_min_px:
                    logical_dx = -self.dx if self.invert_direction else self.dx
                    direction = "left" if logical_dx < 0 else "right"
                    actions.append(GestureAction("workspace", 4, direction, 1))
            elif self.axis == "vertical" and self.fingers == 3:
                actions.append(
                    GestureAction(
                        "task_view" if self.direction == "up" else "show_desktop", 3, self.direction
                    )
                )
            elif self.axis == "horizontal" and self.fingers == 3:
                actions.append(GestureAction("switch_commit", 3, self.direction))
            self.reset()
        return actions

    def check_timeout(self, timeout_seconds: float) -> list[GestureAction]:
        """Cancel an unfinished gesture after inactivity; never commit it."""
        if self.fingers == 0 or self.last_activity is None:
            return []
        if time.monotonic() - self.last_activity <= timeout_seconds:
            return []
        actions = []
        if self.fingers == 3 and self.axis == "horizontal":
            actions.append(GestureAction("switch_cancel", 3, self.direction))
        self.reset()
        return actions
