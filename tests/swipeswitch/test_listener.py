def test_listener_stops_on_explicit_device_permission_error(monkeypatch):
    import io

    from kali_ux.features.window_switcher.engine import listener as listener_module

    class FailedProcess:
        stdout = io.StringIO("libinput error: Permission denied opening /dev/input/event9\n")

        def poll(self):
            return 1

        def terminate(self):
            pass

        def wait(self, timeout=None):
            return 1

    monkeypatch.setattr(
        listener_module.subprocess, "Popen", lambda *_args, **_kwargs: FailedProcess()
    )
    listener = listener_module.LibinputListener("/dev/input/event9", (3, 4), lambda _event: None)
    listener.start()
    listener._thread.join(timeout=1)
    assert not listener.running
    assert "Permission denied" in listener._fatal_error
