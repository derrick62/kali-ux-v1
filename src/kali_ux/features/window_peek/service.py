"""Best-effort X11 window thumbnail capability used by Task View."""

from __future__ import annotations

import logging

from kali_ux.features.window_switcher.engine.thumbs import capture_thumbnail

log = logging.getLogger(__name__)


class WindowPeek:
    def capture_pixbuf(self, window, *, max_width: int = 420, max_height: int = 236):
        """Capture a scaled snapshot without persisting it."""
        try:
            import gi

            gi.require_version("Gdk", "3.0")
            from gi.repository import Gdk

            return capture_thumbnail(window, Gdk, max_width=max_width, max_height=max_height)
        except Exception as exc:
            log.debug("Window thumbnail unavailable: %s", exc)
            return None

    def capability(self) -> tuple[bool, str]:
        try:
            import gi

            gi.require_version("Gdk", "3.0")
            gi.require_version("GdkX11", "3.0")
            from gi.repository import Gdk, GdkX11  # noqa: F401

            if Gdk.Display.get_default() is None:
                return False, "No active GDK display is available."
            return True, (
                "On-demand X11 thumbnails are available; obscured, minimized or protected "
                "windows may use application icons."
            )
        except Exception:
            return False, "GTK3 GdkX11 bindings are unavailable."
