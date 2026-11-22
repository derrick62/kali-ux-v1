from kali_ux.core.config import load_config
from kali_ux.features.launcher.service import ApplicationLauncher


def test_default_config_is_isolated_copy():
    a = load_config()
    b = load_config()
    a["features"]["launcher"]["enabled"] = True
    assert b["features"]["launcher"]["enabled"] is False


def test_launcher_search_is_safe_for_empty_query():
    launcher = ApplicationLauncher()
    assert isinstance(launcher.search(""), list)


def test_partial_feature_config_keeps_other_defaults(tmp_path):
    import json

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"version": 1, "features": {"launcher": {"enabled": True}}}))
    config = load_config(config_file)
    assert config["features"]["launcher"]["enabled"] is True
    assert config["features"]["snap_assist"]["enabled"] is False


def test_invalid_config_section_is_rejected(tmp_path):
    import json

    import pytest

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"version": 1, "features": []}))
    with pytest.raises(ValueError, match="features"):
        load_config(config_file)


def test_relative_xdg_override_is_ignored(monkeypatch):
    from pathlib import Path

    from kali_ux.core.paths import _xdg

    monkeypatch.setenv("KALI_UX_TEST_CONFIG_HOME", "relative/path")
    assert _xdg("KALI_UX_TEST_CONFIG_HOME", ".config") == Path.home() / ".config"


def test_clipboard_limits_are_validated(tmp_path):
    import json

    import pytest

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"version": 1, "clipboard": {"max_items": 0}}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="clipboard.max_items"):
        load_config(config_file)


def test_clipboard_limits_can_be_configured(tmp_path):
    import json

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"version": 1, "clipboard": {"max_items": 12, "max_item_bytes": 2048}}),
        encoding="utf-8",
    )
    config = load_config(config_file)
    assert config["clipboard"]["max_items"] == 12
    assert config["clipboard"]["max_item_bytes"] == 2048


def test_feature_enabled_setting_must_be_boolean(tmp_path):
    import json

    import pytest

    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"version": 1, "features": {"launcher": {"enabled": "yes"}}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="features.launcher.enabled"):
        load_config(config_file)


def test_config_rejects_unsupported_persistent_clipboard_setting(tmp_path):
    import json

    import pytest

    from kali_ux.core.config import load_config

    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1, "clipboard": {"persist": True}}), encoding="utf-8")
    with pytest.raises(ValueError, match="persistent clipboard history is not supported"):
        load_config(path)
