from kali_ux.cli import main


def test_main_reports_platform_status(capsys):
    assert main(["status"]) == 0
    assert "platform" in capsys.readouterr().out


def test_features_command(capsys):
    assert main(["features"]) == 0
    assert "SwipeSwitch" in capsys.readouterr().out


def test_swipeswitch_subcommand_accepts_check_and_config_options():
    from kali_ux.cli import build_parser

    args = build_parser().parse_args(
        ["swipeswitch", "--check", "--debug", "--config", "/tmp/swipeswitch.toml"]
    )
    assert args.command == "swipeswitch"
    assert args.check is True
    assert args.debug is True
    assert args.config == "/tmp/swipeswitch.toml"
