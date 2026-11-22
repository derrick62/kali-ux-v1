from kali_ux.features.gesture_control import conflicts


def test_conflict_report_is_read_only_and_names_conflicting_handlers(monkeypatch):
    monkeypatch.setattr(conflicts, "_running_processes", lambda: {"touchegg"})
    monkeypatch.setattr(
        conflicts,
        "_autostart_matches",
        lambda name: ("/home/user/.config/autostart/fusuma.desktop",) if name == "fusuma" else (),
    )
    monkeypatch.setattr(conflicts.shutil, "which", lambda name: f"/usr/bin/{name}")
    result = conflicts.inspect_gesture_providers()
    report = conflicts.format_conflict_report(result)
    assert "touchegg: running" in report
    assert "fusuma: not running" in report
    assert "will not disable" in report
