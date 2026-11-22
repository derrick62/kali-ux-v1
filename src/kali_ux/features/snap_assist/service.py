"""Snap presets expressed as work-area geometry requests to xfwm4."""

from __future__ import annotations

from kali_ux.platform.window_manager import X11WindowManager

PRESETS = {
    "left": (0, 0, 0.5, 1),
    "right": (0.5, 0, 0.5, 1),
    "top": (0, 0, 1, 0.5),
    "bottom": (0, 0.5, 1, 0.5),
    "top-left": (0, 0, 0.5, 0.5),
    "top-right": (0.5, 0, 0.5, 0.5),
    "bottom-left": (0, 0.5, 0.5, 0.5),
    "bottom-right": (0.5, 0.5, 0.5, 0.5),
}


class SnapService:
    def __init__(self, window_manager: X11WindowManager | None = None):
        self.window_manager = window_manager or X11WindowManager()

    @staticmethod
    def geometry_for_preset(
        preset: str,
        screen_width: int,
        screen_height: int,
        x: int = 0,
        y: int = 0,
    ) -> tuple[int, int, int, int] | None:
        if preset not in PRESETS or screen_width <= 0 or screen_height <= 0:
            return None
        fx, fy, fw, fh = PRESETS[preset]
        offset_x = round(fx * screen_width)
        offset_y = round(fy * screen_height)
        width = round(fw * screen_width)
        height = round(fh * screen_height)
        if fx + fw >= 1:
            width = screen_width - offset_x
        if fy + fh >= 1:
            height = screen_height - offset_y
        return x + offset_x, y + offset_y, max(1, width), max(1, height)

    def snap_active(
        self,
        preset: str,
        screen_width: int,
        screen_height: int,
        x: int = 0,
        y: int = 0,
    ) -> bool:
        geometry = self.geometry_for_preset(preset, screen_width, screen_height, x, y)
        if geometry is None:
            return False
        return self.window_manager.snap_active(*geometry)
