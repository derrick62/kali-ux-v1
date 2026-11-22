from kali_ux.features.window_switcher.process import SwipeSwitchProcess


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.terminated = False
        self.killed = False
        self.signals = []

    def send_signal(self, value):
        self.signals.append(value)

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def kill(self):
        self.killed = True
        self.returncode = -9

    def wait(self, timeout=None):
        return self.returncode


def test_swipeswitch_process_starts_with_private_log_and_can_be_stopped(tmp_path):
    calls = []
    process = FakeProcess()

    def popen(argv, **kwargs):
        calls.append((argv, kwargs))
        return process

    log_path = tmp_path / "logs" / "swipeswitch.log"
    manager = SwipeSwitchProcess(
        log_path=log_path, popen=popen, which=lambda _name: "/usr/bin/kali-ux-swipeswitch"
    )
    started, message = manager.start()
    assert started and "log is stored" in message
    assert manager.running
    assert manager.reload()
    assert process.signals
    assert log_path.stat().st_mode & 0o777 == 0o600
    assert calls[0][0] == ["/usr/bin/kali-ux-swipeswitch"]
    assert calls[0][1]["start_new_session"] is True
    assert manager.terminate()
    assert process.terminated
    assert manager.collect_exit_code() == 0
    assert not manager.has_process


def test_swipeswitch_process_reports_missing_executable():
    manager = SwipeSwitchProcess(which=lambda _name: None)
    started, message = manager.start()
    assert not started
    assert "Install Kali UX" in message


def test_swipeswitch_process_shutdown_kills_a_process_that_does_not_exit(tmp_path):
    class StubbornProcess(FakeProcess):
        def terminate(self):
            self.terminated = True

        def wait(self, timeout=None):
            from subprocess import TimeoutExpired

            raise TimeoutExpired("kali-ux-swipeswitch", timeout)

        def kill(self):
            self.killed = True
            self.returncode = -9

    process = StubbornProcess()
    manager = SwipeSwitchProcess(
        log_path=tmp_path / "swipeswitch.log",
        popen=lambda *_args, **_kwargs: process,
        which=lambda _name: "/usr/bin/kali-ux-swipeswitch",
    )
    assert manager.start()[0]
    assert manager.shutdown(timeout=0.01) == -9
    assert process.terminated and process.killed
    assert not manager.has_process
