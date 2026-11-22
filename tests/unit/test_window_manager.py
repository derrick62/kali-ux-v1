from kali_ux.platform.commands import CommandResult
from kali_ux.platform.window_manager import WindowGeometry, X11WindowManager


def test_window_geometry_parser_keeps_identity_and_ignores_invalid_rows():
    parsed = WindowGeometry.parse(
        "0x1234 2 5678 -10 20 800 600 editor.Editor host title may contain spaces"
    )
    assert parsed == WindowGeometry("0x1234", 2, 5678, -10, 20, 800, 600, "editor.Editor")
    assert WindowGeometry.parse("invalid row") is None
    assert WindowGeometry.parse("0x1234 0 0 0 0 0 0 app.App host title") is None


def test_window_manager_snap_unmaximizes_before_geometry():
    calls = []

    def runner(argv):
        calls.append(argv)
        return CommandResult(True, 0)

    manager = X11WindowManager(runner)
    assert manager.snap_active(-960, 20, 960, 1040)
    assert calls == [
        ["wmctrl", "-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"],
        ["wmctrl", "-r", ":ACTIVE:", "-e", "0,-960,20,960,1040"],
    ]


def test_window_manager_does_not_issue_geometry_after_failed_unmaximize():
    calls = []

    def runner(argv):
        calls.append(argv)
        return CommandResult(True, 1)

    assert not X11WindowManager(runner).snap_active(0, 0, 400, 300)
    assert len(calls) == 1


def test_snap_geometry_covers_odd_workareas_without_overflow():
    from kali_ux.features.snap_assist.service import SnapService

    left = SnapService.geometry_for_preset("left", 1919, 1079)
    right = SnapService.geometry_for_preset("right", 1919, 1079)
    assert left == (0, 0, 960, 1079)
    assert right == (960, 0, 959, 1079)
    assert left[2] + right[2] == 1919


def test_window_manager_activates_only_valid_xids():
    calls = []
    manager = X11WindowManager(lambda argv: calls.append(argv) or CommandResult(True, 0))
    assert manager.activate("0x1234")
    assert not manager.activate("not-an-xid")
    assert calls == [["wmctrl", "-i", "-a", "0x1234"]]
