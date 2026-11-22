"""SwipeSwitch X11 application entry point."""

import argparse
import logging
import os
import signal

from kali_ux.features.gesture_control.service import GestureInputService
from kali_ux.features.window_peek.service import WindowPeek
from kali_ux.platform.gtk import load_gtk3

from .config import load_config
from .listener import detect_touchpad


def _imports():
    return load_gtk3()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="kali-ux-swipeswitch")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("swipeswitch")
    try:
        if not os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            raise RuntimeError(
                "SwipeSwitch currently requires an X11 session; Wayland is not supported."
            )
        cfg = load_config(args.config)
        from kali_ux.control_center.model import ControlCenterModel

        try:
            control_model = ControlCenterModel()
            peek_feature = control_model.get_feature("window_peek")
            overview_feature = control_model.get_feature("window_overview")
            cfg.thumbnails = (
                cfg.thumbnails and peek_feature["enabled"] and peek_feature["available"]
            )
            feature_preferences = {
                "window_overview": overview_feature["enabled"] and overview_feature["available"],
                "window_peek": peek_feature["enabled"] and peek_feature["available"],
            }
        except (OSError, ValueError):
            cfg.thumbnails = False
            feature_preferences = {"window_overview": False, "window_peek": False}
        device = detect_touchpad(cfg.touchpad_device)
        Gdk, GLib, Gtk, Pango, Wnck = _imports()
        if args.check:
            print(f"X11 DISPLAY: {os.environ['DISPLAY']}")
            print(f"Touchpad: {device}")
            print(f"Input readable: {'yes' if os.access(device, os.R_OK) else 'no'}")
            print(f"Config: {cfg.config_path}")
            print("GTK 3 / libwnck imports: OK")
            if not os.access(device, os.R_OK):
                print(
                    "Permission denied: review device access; Kali UX will not change permissions."
                )
                return 1
            return 0

        screen = Wnck.Screen.get_default()
        if screen is None:
            raise RuntimeError("Could not connect to the X11 window manager.")
        screen.force_update()
        from .controller import SwipeSwitchController
        from .overlay import SwitcherOverlay
        from .task_view import TaskView
        from .tracker import WindowTracker

        tracker = WindowTracker(screen, cfg)
        switcher = SwitcherOverlay(Gtk, Gdk, cfg, GLib=GLib)
        controller = SwipeSwitchController(
            screen, tracker, switcher, None, Gdk, cfg, feature_enabled=feature_preferences
        )
        peek = WindowPeek()
        task_view = TaskView(
            Gtk,
            Gdk,
            Pango,
            lambda window: controller.activate_xid(window.get_xid()),
            preview_callback=(
                lambda window: peek.capture_pixbuf(window, max_width=300, max_height=170)
            )
            if cfg.thumbnails
            else None,
            GLib=GLib,
        )
        controller.task_view = task_view

        input_service = GestureInputService(
            device, (3, 4), debug=args.debug, use_unaccelerated=cfg.use_unaccelerated
        )
        input_service.subscribe(lambda event: GLib.idle_add(controller.handle_event, event))
        input_service.start()
        GLib.timeout_add(250, lambda: (controller.check_timeout(), GLib.SOURCE_CONTINUE)[1])

        def reload_config(_signum, _frame):
            try:
                new_config = load_config(args.config)
                peek_feature = ControlCenterModel().get_feature("window_peek")
                new_config.thumbnails = (
                    new_config.thumbnails and peek_feature["enabled"] and peek_feature["available"]
                )
                controller.update_config(new_config)
                input_service.set_use_unaccelerated(new_config.use_unaccelerated)
                task_view.preview_callback = (
                    (lambda window: peek.capture_pixbuf(window, max_width=300, max_height=170))
                    if new_config.thumbnails
                    else None
                )
                log.info("Configuration reloaded")
            except Exception:
                log.exception("Config reload failed; retaining current configuration")

        def shutdown(*_args):
            input_service.stop()
            Gtk.main_quit()

        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, reload_config)
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        log.info("SwipeSwitch started; listening to %s (3- and 4-finger gestures)", device)
        Gtk.main()
        input_service.stop()
        return 0
    except Exception as exc:
        log.error("%s", exc)
        if args.debug:
            log.exception("Startup error")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
