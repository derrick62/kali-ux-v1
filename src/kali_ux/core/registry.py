"""Static feature registry; intentionally not a third-party plugin loader."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    key: str
    title: str
    description: str
    status: str
    requires: tuple[str, ...] = ()


FEATURES = (
    Feature(
        "window_switcher",
        "SwipeSwitch",
        "Gesture-driven MRU window switching and desktop actions",
        "prototype",
        ("X11", "GTK3", "libwnck", "libinput", "input access"),
    ),
    Feature(
        "window_overview",
        "Task View",
        "Overview of open windows with selection and dismissal",
        "prototype",
        ("X11", "GTK3", "libwnck"),
    ),
    Feature(
        "snap_assist",
        "Snap Assist",
        "Native window placement presets and snap suggestions",
        "prototype",
        ("X11", "xfwm4", "wmctrl"),
    ),
    Feature(
        "clipboard_history",
        "Clipboard History",
        "Opt-in, bounded, session-only clipboard text history",
        "prototype",
        ("X11", "GTK clipboard"),
    ),
    Feature(
        "quick_panel", "Quick Panel", "Shortcuts to existing XFCE controls", "prototype", ("XFCE",)
    ),
    Feature(
        "focus_tools",
        "Focus Tools",
        "Optional do-not-disturb and focus session controls",
        "prototype",
        ("XFCE", "xfconf-query"),
    ),
    Feature(
        "launcher", "Application Launcher", "Desktop-entry search and launch", "prototype", ("gio",)
    ),
    Feature(
        "window_peek",
        "Window Peek",
        "Best-effort window preview capability",
        "prototype",
        ("X11", "GTK3", "libwnck", "GdkX11"),
    ),
    Feature(
        "layout_memory",
        "Layout Memory",
        "Save and restore best-effort window geometry",
        "prototype",
        ("X11", "wmctrl"),
    ),
)
