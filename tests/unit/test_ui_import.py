def test_ui_module_can_be_imported_without_loading_gtk():
    # GTK is a system dependency and is intentionally loaded only when the UI starts.
    from kali_ux.ui.app import KaliUXWindow, _gtk

    assert KaliUXWindow is not None
    assert callable(_gtk)
