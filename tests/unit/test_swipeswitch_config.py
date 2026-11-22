import pytest

from kali_ux.features.window_switcher.engine.config import Config, _default_text, load_config


def test_default_swipeswitch_config_enables_on_demand_thumbnails():
    config = Config().validate()
    assert config.thumbnails is True
    assert "thumbnails = true" in _default_text()


def test_swipeswitch_config_rejects_non_boolean_flags():
    with pytest.raises(ValueError, match="thumbnails must be a boolean"):
        Config(thumbnails="false").validate()


def test_swipeswitch_config_reads_unaccelerated_preference(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("use_unaccelerated = true\nthumbnails = false\n", encoding="utf-8")
    config = load_config(path)
    assert config.use_unaccelerated is True
    assert config.thumbnails is False


def test_default_swipeswitch_config_is_created_with_private_permissions(tmp_path):
    path = tmp_path / "swipeswitch" / "config.toml"
    config = load_config(path)
    assert config.theme == "auto"
    assert config.monitor == "primary"
    assert path.stat().st_mode & 0o777 == 0o600
