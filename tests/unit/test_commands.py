from kali_ux.platform import commands


def test_run_command_captures_exit_status(monkeypatch):
    class Completed:
        returncode = 7
        stdout = "out"
        stderr = "err"

    monkeypatch.setattr(commands.shutil, "which", lambda _name: "/usr/bin/example")
    monkeypatch.setattr(commands.subprocess, "run", lambda *a, **k: Completed())
    result = commands.run_command(["example", "--flag"])
    assert result.available
    assert result.returncode == 7
    assert (result.stdout, result.stderr) == ("out", "err")


def test_run_command_reports_missing_executable(monkeypatch):
    monkeypatch.setattr(commands.shutil, "which", lambda _name: None)
    result = commands.run_command(["not-installed"])
    assert not result.available
    assert "not-installed" in result.stderr


def test_start_command_detaches_graphical_process(monkeypatch):
    captured = {}
    monkeypatch.setattr(commands.shutil, "which", lambda _name: "/usr/bin/example")

    def fake_popen(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(commands.subprocess, "Popen", fake_popen)
    result = commands.start_command(["example", "--settings"])
    assert result.available and result.started
    assert captured["start_new_session"] is True
    assert captured["stdin"] is commands.subprocess.DEVNULL
    assert captured["stdout"] is commands.subprocess.DEVNULL
    assert captured["stderr"] is commands.subprocess.DEVNULL
