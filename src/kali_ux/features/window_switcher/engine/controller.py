"""Coordinates recognized gesture actions with desktop services and GTK views."""

from __future__ import annotations

import logging

from kali_ux.features.gesture_control.router import GestureActionRouter

from .activator import activate_window
from .desktop import DesktopVisibilityManager
from .gestures import GestureRecognizer
from .workspaces import WorkspaceManager

log = logging.getLogger(__name__)


class SwipeSwitchController:
    def __init__(self, screen, tracker, switcher, task_view, Gdk, config, feature_enabled=None):
        self.screen = screen
        self.tracker = tracker
        self.switcher = switcher
        self.task_view = task_view
        self.Gdk = Gdk
        self.config = config
        self.feature_enabled = dict(feature_enabled or {})
        self.recognizer = GestureRecognizer(
            config.show_threshold_px,
            config.step_px,
            flick_min_px=config.flick_min_px,
            invert_direction=config.invert_direction,
        )
        self.desktop = DesktopVisibilityManager(screen, tracker)
        self.workspaces = WorkspaceManager(screen, wrap=False)
        self.switch_windows = []
        self.selected = 0
        self.action_router = GestureActionRouter()
        self._register_actions()

    def _register_actions(self):
        for name, handler in (
            ("switch_begin", self._switch_begin),
            ("switch_move", self._switch_move),
            ("switch_commit", self._switch_commit),
            ("switch_cancel", self._switch_cancel),
            ("workspace", self._workspace),
            ("show_desktop", self._show_desktop),
            ("task_view", self._task_view),
        ):
            self.action_router.register(name, handler)

    def update_feature_preferences(self, preferences):
        self.feature_enabled = dict(preferences)
        if not self.feature_enabled.get("window_overview", True):
            self.task_view.hide()
        elif not self.feature_enabled.get("window_peek", True):
            self.task_view.hide()

    def update_config(self, config):
        if self.switch_windows:
            self.switcher.hide()
            self.switch_windows = []
        self.config = config
        self.recognizer = GestureRecognizer(
            config.show_threshold_px,
            config.step_px,
            flick_min_px=config.flick_min_px,
            invert_direction=config.invert_direction,
        )
        self.tracker.update_config(config)
        self.switcher.update_config(config)

    def activate_xid(self, xid):
        """Resolve a Task View selection against live windows before activation."""
        self.screen.force_update()
        target = next(
            (
                window
                for window in (self.screen.get_windows() or [])
                if int(window.get_xid()) == int(xid)
            ),
            None,
        )
        if target is None:
            log.info("Task View selection %s is no longer available", xid)
            return False
        return activate_window(target, self.Gdk, log)

    def handle_event(self, event):
        for action in self.recognizer.handle(event):
            self.action_router.dispatch(action)

    def check_timeout(self):
        for action in self.recognizer.check_timeout(self.config.gesture_timeout):
            self.action_router.dispatch(action)

    def _switch_begin(self, _action):
        self.switch_windows = self.tracker.get_switchable_windows()
        self.selected = 0
        if len(self.switch_windows) < 2:
            self.switch_windows = []
            return
        self.switcher.show(self.switch_windows, self.selected)

    def _switch_move(self, action):
        if not self.switch_windows:
            return
        # Follow the physical swipe: right advances through MRU order, left
        # moves toward the previously focused item.
        delta = action.steps * (1 if action.direction == "right" else -1)
        self.selected = (self.selected + delta) % len(self.switch_windows)
        self.switcher.update_selection(self.selected)

    def _switch_commit(self, _action):
        self.switcher.hide()
        if self.switch_windows:
            target_xid = int(self.switch_windows[self.selected].get_xid())
            self.screen.force_update()
            live = {int(window.get_xid()): window for window in (self.screen.get_windows() or [])}
            target = live.get(target_xid)
            if target is not None:
                activate_window(target, self.Gdk, log)
        self.switch_windows = []

    def _switch_cancel(self, _action):
        self.switcher.hide()
        self.switch_windows = []

    def _workspace(self, action):
        self.task_view.hide()
        for _ in range(max(1, action.steps)):
            if not self.workspaces.navigate(action.direction):
                break
        self.switch_windows = []

    def _show_desktop(self, _action):
        self.task_view.hide()
        self.desktop.show_desktop()
        self.switch_windows = []

    def _task_view(self, _action):
        if self.desktop.has_snapshot:
            self.desktop.restore()
        elif self.feature_enabled.get("window_overview", True):
            self.switcher.hide()
            windows = self.tracker.get_switchable_windows()
            if windows:
                self.task_view.show(windows)
        else:
            log.info("Task View gesture ignored because Window Overview is disabled")
        self.switch_windows = []
