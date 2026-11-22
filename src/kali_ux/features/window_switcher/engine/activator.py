"""Window activation, with wmctrl fallback."""

import logging

from kali_ux.platform.window_manager import X11WindowManager

log = logging.getLogger(__name__)


def activate_window(window, Gdk, logger=None):
    logger = logger or log
    try:
        if window.is_minimized():
            window.unminimize(Gdk.CURRENT_TIME)
        window.activate(Gdk.CURRENT_TIME)
        return True
    except Exception as exc:
        logger.warning("Wnck activation failed: %s", exc)
        try:
            if X11WindowManager().activate(hex(int(window.get_xid()))):
                return True
        except Exception as fallback_exc:
            logger.error("wmctrl fallback failed: %s", fallback_exc)
        return False
