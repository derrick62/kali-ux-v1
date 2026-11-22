from kali_ux.features.window_switcher.engine.controller import SwipeSwitchController


class FakeTaskView:
    def __init__(self):
        self.shown = []

    def show(self, windows):
        self.shown.append(windows)


class FakeDesktop:
    def __init__(self, has_snapshot=False):
        self.has_snapshot = has_snapshot
        self.restored = 0

    def restore(self):
        self.restored += 1


class FakeTracker:
    def get_switchable_windows(self):
        return ["window-a", "window-b"]


class FakeSwitcher:
    def __init__(self):
        self.hidden = 0

    def hide(self):
        self.hidden += 1


def controller_with_preferences(enabled, has_snapshot=False):
    controller = object.__new__(SwipeSwitchController)
    controller.feature_enabled = {"window_overview": enabled}
    controller.desktop = FakeDesktop(has_snapshot)
    controller.task_view = FakeTaskView()
    controller.tracker = FakeTracker()
    controller.switcher = FakeSwitcher()
    controller.switch_windows = []
    return controller


def test_task_view_gesture_obeys_window_overview_preference():
    controller = controller_with_preferences(False)
    controller._task_view(None)
    assert controller.task_view.shown == []
    assert controller.switcher.hidden == 0


def test_task_view_gesture_restores_show_desktop_snapshot_even_when_overview_disabled():
    controller = controller_with_preferences(False, has_snapshot=True)
    controller._task_view(None)
    assert controller.desktop.restored == 1
    assert controller.task_view.shown == []


def test_task_view_gesture_opens_overview_when_enabled():
    controller = controller_with_preferences(True)
    controller._task_view(None)
    assert controller.switcher.hidden == 1
    assert controller.task_view.shown == [["window-a", "window-b"]]
