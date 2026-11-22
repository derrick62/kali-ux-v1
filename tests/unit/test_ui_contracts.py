from kali_ux.ui.app import KaliUXWindow
from kali_ux.ui.pages import applications, clipboard, productivity, settings, windows


def test_control_center_implements_every_callback_used_by_page_builders():
    required = {
        "refresh_apps",
        "render_apps",
        "_launch_first_app",
        "_launch_app_row",
        "launch_app",
        "_clipboard_changed",
        "_on_clipboard_text",
        "render_clipboard",
        "clear_clipboard",
        "copy_clipboard",
        "start_focus_session",
        "disable_focus",
        "capture_layout",
        "restore_layout",
        "delete_layout",
        "show_task_view",
        "refresh_windows",
        "snap_active",
        "show_gesture_conflicts",
        "show_diagnostics",
        "refresh_diagnostics",
        "show_status",
        "open_config_folder",
        "start_swipeswitch",
        "toggle_swipeswitch",
        "stop_swipeswitch",
    }
    assert all(callable(getattr(KaliUXWindow, name, None)) for name in required)
    assert all(
        callable(getattr(module, name, None))
        for module, name in (
            (applications, "launcher"),
            (clipboard, "clipboard"),
            (productivity, "productivity"),
            (settings, "gestures"),
            (windows, "windows"),
        )
    )
