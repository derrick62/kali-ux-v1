"""GTK3 settings, privacy and diagnostics pages."""

import shutil


def appearance(app):
    page = app._page("Appearance", "appearance")
    app._card(
        page,
        "Visual preferences",
        "The Control Center follows the active GTK desktop theme. Task View uses a "
        "focused dark overlay for visual separation, while the dashboard remains theme-aware.",
    )
    app._card(
        page, "Current interface", "GTK3 · Active desktop theme · Keyboard-accessible controls"
    )


def gestures(app):
    page = app._page("Gestures", "gestures")
    app._card(
        page,
        "Gesture provider",
        "Gesture input is not started automatically. SwipeSwitch uses one shared "
        "libinput listener after checking device readability; known competing handlers "
        "are reported without being changed.",
    )
    providers = [
        name for name in ("touchegg", "libinput-gestures", "fusuma", "gebaar") if shutil.which(name)
    ]
    app._card(
        page,
        "Detected providers",
        ", ".join(providers) if providers else "No supported external gesture provider detected.",
    )
    app._card(
        page,
        "Current status",
        "Gesture input is owned by one explicitly started service. Other handlers are "
        "only reported; Kali UX never disables or reconfigures them automatically.",
    )
    app._button(page, "Scan for gesture conflicts", app.show_gesture_conflicts)
    app.swipeswitch_button = app._button(page, "Start SwipeSwitch", app.toggle_swipeswitch)
    app._bind_feature_control("window_switcher", app.swipeswitch_button)


def privacy(app):
    page = app._page("Privacy", "privacy")
    app._card(
        page,
        "Clipboard history",
        "Clipboard capture is opt-in and held in memory only. Window previews are "
        "captured locally on demand and are not persisted. Neither payloads nor titles "
        "are written to diagnostic logs.",
    )
    app._button(page, "Open clipboard controls", lambda: app.show_page("clipboard"))
    app._card(
        page,
        "Data collection",
        "Kali UX does not collect telemetry. Clipboard persistence and automatic "
        "sensitive-field detection are intentionally not implemented.",
    )


def diagnostics_page(app):
    page = app._page("Diagnostics", "diagnostics")
    app._card(
        page,
        "Desktop health",
        "Review detected platform capabilities, feature requirements and known "
        "integration limitations. Diagnostics are read-only.",
    )
    app._button(page, "View diagnostic report", app.show_diagnostics)
    app._button(page, "Refresh detected capabilities", app.refresh_diagnostics)


def about(app):
    page = app._page("About", "about")
    app._card(
        page,
        "Kali UX",
        "A modular desktop-experience enhancement suite for Kali Linux. "
        "The initial target is XFCE on X11, with xfwm4 remaining the authoritative window manager.",
    )
    app._button(page, "Show implementation status", app.show_status)
    app._button(page, "Open configuration folder", app.open_config_folder)
