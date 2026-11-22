"""Kali UX command-line interface."""

from __future__ import annotations

import argparse
import json

from kali_ux import __version__
from kali_ux.control_center.model import ControlCenterModel
from kali_ux.core.config import write_default_config
from kali_ux.diagnostics.report import build_report


def build_parser():
    p = argparse.ArgumentParser(prog="kali-ux", description="Kali UX desktop enhancement suite")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("status", help="Show platform and feature capability report")
    sub.add_parser("init", help="Create a private default configuration")
    sub.add_parser("features", help="List bundled features")
    swipe = sub.add_parser("swipeswitch", help="Start or check the SwipeSwitch X11/GTK3 interface")
    swipe.add_argument("--check", action="store_true", help="Check X11, GTK and touchpad access")
    swipe.add_argument("--debug", action="store_true", help="Enable diagnostic logging")
    swipe.add_argument("--config", help="Use an alternate SwipeSwitch TOML configuration")
    sub.add_parser("gui", help="Open the Kali UX GTK3 Control Center")
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if a.command == "init":
        print(write_default_config())
        return 0
    if a.command == "features":
        try:
            features = ControlCenterModel().rows()
        except (OSError, ValueError) as exc:
            print(f"Cannot load feature preferences: {exc}")
            return 1
        for feature in features:
            enabled = "enabled" if feature["enabled"] else "disabled"
            print(
                f"{feature['key']:20} {feature['implementation']:12} "
                f"{feature['state']:24} {enabled:8} {feature['title']}"
            )
        return 0
    if a.command == "swipeswitch":
        from kali_ux.features.window_switcher.engine.__main__ import main as run_switcher

        forwarded = []
        if a.check:
            forwarded.append("--check")
        if a.debug:
            forwarded.append("--debug")
        if a.config:
            forwarded.extend(("--config", a.config))
        return run_switcher(forwarded)
    if a.command == "gui":
        from kali_ux.ui.app import main as run_gui

        try:
            return run_gui()
        except (RuntimeError, ValueError, OSError) as exc:
            print(exc)
            return 1
    if a.command == "status" or a.command is None:
        try:
            print(json.dumps(build_report(), indent=2))
        except (OSError, ValueError) as exc:
            print(f"Cannot build diagnostics report: {exc}")
            return 1
        return 0
    return 2
