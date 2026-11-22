from kali_ux.features.focus_tools import service as focus_tools
from kali_ux.features.layout_memory import service as layout_memory
from kali_ux.features.snap_assist import service as snap_assist
from kali_ux.platform.commands import CommandResult
from kali_ux.platform.window_manager import WindowGeometry


def test_focus_mode_preserves_original_value_on_repeated_enable(monkeypatch):
    calls = []
    responses = [
        CommandResult(True, 0, "false"),
        CommandResult(True, 0),
        CommandResult(True, 0, "true"),
        CommandResult(True, 0),
    ]

    def fake_run(argv):
        calls.append(argv)
        return responses.pop(0)

    monkeypatch.setattr(focus_tools, "run_command", fake_run)
    focus = focus_tools.FocusMode()
    assert focus.enable()
    assert focus.enable()
    assert len(calls) == 2
    assert focus.disable()
    assert calls[-1][-1] == "false"
    assert not focus.active


def test_focus_mode_keeps_recovery_state_if_restore_fails(monkeypatch):
    responses = [
        CommandResult(True, 0, "false"),
        CommandResult(True, 0),
        CommandResult(True, 0, "true"),
        CommandResult(True, 1),
    ]
    monkeypatch.setattr(focus_tools, "run_command", lambda _argv: responses.pop(0))
    focus = focus_tools.FocusMode()
    assert focus.enable()
    assert not focus.disable()
    assert focus.active
    assert focus._previous == "false"


class FakeWindowManager:
    def __init__(self, windows=None, snap_result=True):
        self.windows = windows if windows is not None else []
        self.snap_result = snap_result
        self.geometry_calls = []
        self.workspace_calls = []

    def list_windows(self):
        return self.windows

    def snap_active(self, x, y, width, height):
        self.geometry_calls.append((x, y, width, height))
        return self.snap_result

    def set_geometry(self, window_id, x, y, width, height):
        self.geometry_calls.append((window_id, x, y, width, height))
        return True

    def set_workspace(self, window_id, desktop):
        self.workspace_calls.append((window_id, desktop))
        return True


def test_snap_uses_shared_backend_and_rejects_invalid_preset():
    backend = FakeWindowManager(snap_result=False)
    snap = snap_assist.SnapService(backend)
    assert not snap.snap_active("left", 1920, 1080)
    assert backend.geometry_calls == [(0, 0, 960, 1080)]
    assert not snap.snap_active("unknown", 1920, 1080)


def test_snap_uses_workarea_origin_and_dimensions():
    backend = FakeWindowManager()
    assert snap_assist.SnapService(backend).snap_active("right", 1000, 800, -1000, 40)
    assert backend.geometry_calls == [(-500, 40, 500, 800)]


def test_layout_capture_omits_private_window_titles_and_writes_private_file(tmp_path):
    backend = FakeWindowManager(
        [
            WindowGeometry("0x01234567", 0, 4321, 10, 20, 800, 600, "editor.Editor"),
        ]
    )
    target = tmp_path / "nested" / "layouts.json"
    layouts = layout_memory.LayoutMemory(target, backend)
    assert layouts.capture("Work")
    content = target.read_text()
    assert "private-title" not in content
    assert "editor.Editor" in content
    assert layouts.names() == ["Work"]
    assert target.stat().st_mode & 0o777 == 0o600


def test_layout_restore_validates_window_identity_and_geometry(tmp_path):
    target = tmp_path / "layouts.json"
    target.write_text(
        '{"Desk": ['
        '{"id":"0x1234","pid":222,"wm_class":"editor.Editor",'
        '"desktop":1,"x":1,"y":2,"width":300,"height":200},'
        '{"id":"rm -rf /","x":0,"y":0,"width":1,"height":1}]}'
    )
    backend = FakeWindowManager([WindowGeometry("0x1234", 0, 222, 1, 2, 300, 200, "editor.Editor")])
    assert layout_memory.LayoutMemory(target, backend).restore("Desk") == 1
    assert backend.workspace_calls == [("0x1234", 1)]
    assert backend.geometry_calls == [("0x1234", 1, 2, 300, 200)]


def test_layout_restore_skips_stale_or_reused_window_ids(tmp_path):
    target = tmp_path / "layouts.json"
    target.write_text(
        '{"Desk": [{"id":"0x1234","pid":222,"wm_class":"editor.Editor",'
        '"x":1,"y":2,"width":300,"height":200}]}'
    )
    backend = FakeWindowManager([WindowGeometry("0x1234", 0, 333, 1, 2, 300, 200, "other.App")])
    assert layout_memory.LayoutMemory(target, backend).restore("Desk") == 0
    assert backend.geometry_calls == []


def test_layout_rejects_empty_and_path_like_names(tmp_path):
    layouts = layout_memory.LayoutMemory(tmp_path / "layouts.json")
    assert not layouts.capture("../outside")
    assert not layouts.capture("  ")
    assert layouts.restore("../outside") == 0


def test_layout_delete_removes_only_selected_snapshot(tmp_path):
    target = tmp_path / "layouts.json"
    layouts = layout_memory.LayoutMemory(target)
    layouts._write({"Desk": [], "Work": []})
    assert layouts.delete("Desk")
    assert layouts.names() == ["Work"]
    assert not layouts.delete("Missing")


def test_focus_mode_creates_missing_property_and_removes_it_on_restore(monkeypatch):
    calls = []
    responses = [
        CommandResult(True, 1),
        CommandResult(True, 0),
        CommandResult(True, 0, "true"),
        CommandResult(True, 0),
    ]

    def fake_run(argv):
        calls.append(argv)
        return responses.pop(0)

    monkeypatch.setattr(focus_tools, "run_command", fake_run)
    focus = focus_tools.FocusMode()
    assert focus.enable()
    assert focus.active and focus._created
    assert focus.disable()
    assert calls[-1][-1] == "-r"
    assert not focus.active


def test_focus_mode_respects_user_turning_dnd_off_during_session(monkeypatch):
    responses = [
        CommandResult(True, 0, "false"),
        CommandResult(True, 0),
        CommandResult(True, 0, "false"),
    ]
    monkeypatch.setattr(focus_tools, "run_command", lambda _argv: responses.pop(0))
    focus = focus_tools.FocusMode()
    assert focus.enable()
    assert focus.disable()
    assert not focus.active
    assert focus._previous is None
