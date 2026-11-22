"""Interactive GTK3 dashboard for the Kali UX prototype.

All desktop mutations are explicit user actions. The UI does not elevate privileges,
change xfwm4 configuration, or start an input listener automatically.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from kali_ux.control_center.model import ControlCenterModel
from kali_ux.core.paths import CONFIG_HOME
from kali_ux.diagnostics.report import build_report
from kali_ux.features.clipboard_history.service import ClipboardHistory
from kali_ux.features.focus_tools.service import FocusMode
from kali_ux.features.launcher.service import ApplicationLauncher
from kali_ux.features.layout_memory.service import LayoutMemory
from kali_ux.features.snap_assist.service import SnapService
from kali_ux.features.window_peek.service import WindowPeek
from kali_ux.features.window_switcher.engine.activator import activate_window
from kali_ux.features.window_switcher.engine.config import load_config as load_swipeswitch_config
from kali_ux.features.window_switcher.engine.task_view import TaskView
from kali_ux.features.window_switcher.process import SwipeSwitchProcess
from kali_ux.platform.commands import start_command
from kali_ux.platform.gtk import load_gtk3
from kali_ux.ui.pages.applications import launcher as build_launcher_page
from kali_ux.ui.pages.clipboard import clipboard as build_clipboard_page
from kali_ux.ui.pages.features import features as build_features_page
from kali_ux.ui.pages.home import home as build_home_page
from kali_ux.ui.pages.productivity import productivity as build_productivity_page
from kali_ux.ui.pages.settings import (
    about as build_about_page,
)
from kali_ux.ui.pages.settings import (
    appearance as build_appearance_page,
)
from kali_ux.ui.pages.settings import (
    diagnostics_page as build_diagnostics_page,
)
from kali_ux.ui.pages.settings import (
    gestures as build_gestures_page,
)
from kali_ux.ui.pages.settings import (
    privacy as build_privacy_page,
)
from kali_ux.ui.pages.windows import windows as build_windows_page


def _gtk():
    return load_gtk3()


class KaliUXWindow:
    def __init__(self, Gtk, Gdk, GLib, Pango, Wnck):
        self.Gtk, self.Gdk, self.GLib, self.Pango, self.Wnck = Gtk, Gdk, GLib, Pango, Wnck
        self.model = ControlCenterModel()
        self.config = self.model.config
        self._feature_controls = {}
        clipboard_config = self.config.get("clipboard", {})
        self.clipboard = ClipboardHistory(
            max_items=clipboard_config.get("max_items", 50),
            max_item_bytes=clipboard_config.get("max_item_bytes", 65536),
        )
        self.focus = FocusMode()
        self._focus_timer_id = None
        self.swipeswitch_process = SwipeSwitchProcess()
        self._swipeswitch_poll_id = None
        self._swipeswitch_stop_deadline = None
        self._swipeswitch_stop_requested = False
        self.swipeswitch_button = None
        self.layouts = LayoutMemory()
        self.launcher = ApplicationLauncher()
        self.snap = SnapService()
        self.window = Gtk.Window(title="Kali UX · Desktop Control Center")
        self.window.set_default_size(1000, 720)
        self.window.set_border_width(18)
        self.window.connect("destroy", self._on_destroy)
        self._style()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.window.add(root)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        title = Gtk.Label()
        title.set_markup(
            '<span size="xx-large" weight="bold">Kali UX</span>  '
            '<span alpha="65%">Desktop Control Center</span>'
        )
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, True, True, 0)
        status = Gtk.Button(label="System status")
        status.connect("clicked", self.show_diagnostics)
        header.pack_end(status, False, False, 0)
        root.pack_start(header, False, False, 0)
        subtitle = Gtk.Label(
            label="A unified set of thoughtful desktop interactions for XFCE on X11."
        )
        subtitle.set_halign(Gtk.Align.START)
        subtitle.get_style_context().add_class("muted")
        root.pack_start(subtitle, False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        root.pack_start(content, True, True, 0)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(120)
        self.sidebar = Gtk.StackSidebar()
        self.sidebar.set_stack(self.stack)
        self.sidebar.set_size_request(190, -1)
        self.sidebar.get_style_context().add_class("navigation-sidebar")
        content.pack_start(self.sidebar, False, False, 0)
        content.pack_start(self.stack, True, True, 0)

        build_home_page(self)
        build_features_page(self)
        build_windows_page(self)
        build_clipboard_page(self)
        build_launcher_page(self)
        build_productivity_page(self)
        build_appearance_page(self)
        build_gestures_page(self)
        build_privacy_page(self)
        build_diagnostics_page(self)
        build_about_page(self)
        self._apply_feature_preferences()
        footer = Gtk.Label(
            label=(
                "Prototype · X11 / XFCE · Window manager remains xfwm4 · "
                "No background listeners started automatically"
            )
        )
        footer.get_style_context().add_class("muted")
        footer.set_halign(Gtk.Align.START)
        root.pack_start(footer, False, False, 0)
        self.window.show_all()
        self.clipboard_backend = self.Gtk.Clipboard.get(self.Gdk.SELECTION_CLIPBOARD)
        self.clipboard_backend.connect("owner-change", self._clipboard_changed)

    def _style(self):
        css = self.Gtk.CssProvider()
        css.load_from_data(b"""
            window { background-color: @theme_bg_color; color: @theme_fg_color; }
            stack { background-color: transparent; }
            .navigation-sidebar {
                background-color: shade(@theme_bg_color, 0.96);
                border: 1px solid alpha(@theme_fg_color, 0.12);
                border-radius: 10px;
                padding: 8px;
            }
            .navigation-sidebar list { background-color: transparent; }
            .navigation-sidebar row { border-radius: 7px; padding: 5px; }
            button { padding: 8px 12px; border-radius: 8px; }
            entry, textview, treeview {
                background-color: @theme_base_color;
                color: @theme_text_color;
            }
            .panel {
                background-color: @theme_base_color;
                color: @theme_text_color;
                border: 1px solid alpha(@theme_fg_color, 0.14);
                border-radius: 12px;
                padding: 16px;
            }
            .muted { color: alpha(@theme_fg_color, 0.72); }
            .metric { font-size: 24px; font-weight: bold; }
        """)
        self.Gtk.StyleContext.add_provider_for_screen(
            self.Gdk.Screen.get_default(), css, self.Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _page(self, name, key=None):
        page = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=12)
        page.set_border_width(16)
        page.set_homogeneous(False)
        self.stack.add_titled(page, key or name.lower().replace(" ", "-"), name)
        return page

    def show_page(self, key):
        self.stack.set_visible_child_name(key)

    def _button(self, parent, label, callback, *args):
        button = self.Gtk.Button(label=label)
        button.connect("clicked", lambda *_: callback(*args))
        parent.pack_start(button, False, False, 0)
        return button

    def _bind_feature_control(self, key, widget):
        base_sensitive = bool(widget.get_sensitive())
        self._feature_controls.setdefault(key, []).append((widget, base_sensitive))
        feature = self.model.get_feature(key)
        widget.set_sensitive(base_sensitive and bool(feature["enabled"] and feature["available"]))
        return widget

    def _apply_feature_preferences(self):
        for key, widgets in self._feature_controls.items():
            feature = self.model.get_feature(key)
            active = bool(feature["enabled"] and feature["available"])
            for widget, base_sensitive in widgets:
                widget.set_sensitive(base_sensitive and active)

    def _card(self, parent, title, description):
        box = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=7)
        box.get_style_context().add_class("panel")
        heading = self.Gtk.Label()
        heading.set_markup(f"<b>{title}</b>")
        heading.set_halign(self.Gtk.Align.START)
        body = self.Gtk.Label(label=description)
        body.set_line_wrap(True)
        body.set_halign(self.Gtk.Align.START)
        body.get_style_context().add_class("muted")
        box.pack_start(heading, False, False, 0)
        box.pack_start(body, False, False, 0)
        parent.pack_start(box, False, False, 0)
        return box

    def render_features(self):
        if not hasattr(self, "feature_rows"):
            return
        for child in self.feature_rows.get_children():
            self.feature_rows.remove(child)
        for feature in self.model.rows():
            card = self.Gtk.Box(orientation=self.Gtk.Orientation.HORIZONTAL, spacing=12)
            card.get_style_context().add_class("panel")
            details = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=4)
            title = self.Gtk.Label(label=feature["title"])
            title.set_halign(self.Gtk.Align.START)
            title.set_markup(f"<b>{feature['title']}</b>")
            description = self.Gtk.Label(label=feature["description"])
            description.set_line_wrap(True)
            description.set_halign(self.Gtk.Align.START)
            description.get_style_context().add_class("muted")
            status_text = (
                f"Implementation: {feature['implementation'].title()} · "
                f"Availability: {feature['state']}"
            )
            if feature["missing_requirements"]:
                status_text += " · Missing: " + ", ".join(feature["missing_requirements"])
            status = self.Gtk.Label(label=status_text)
            status.set_halign(self.Gtk.Align.START)
            status.get_style_context().add_class("muted")
            details.pack_start(title, False, False, 0)
            details.pack_start(description, False, False, 0)
            details.pack_start(status, False, False, 0)
            toggle = self.Gtk.Switch()
            toggle.set_active(feature["enabled"])
            toggle.set_sensitive(feature["can_enable"])
            toggle.set_valign(self.Gtk.Align.CENTER)
            toggle.connect(
                "notify::active",
                lambda widget, _pspec, key=feature["key"]: self.set_feature_enabled(
                    key, widget.get_active(), widget
                ),
            )
            card.pack_start(details, True, True, 0)
            card.pack_end(toggle, False, False, 0)
            self.feature_rows.pack_start(card, False, False, 0)
        self.feature_rows.show_all()

    def set_feature_enabled(self, key, enabled, widget):
        try:
            self.model.set_enabled(key, enabled)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            current = self.model.get_feature(key)["enabled"]
            widget.set_active(current)
            self.notify(str(exc))
            return
        self.config = self.model.config
        if not enabled and key == "clipboard_history":
            if hasattr(self, "capture_toggle"):
                self.capture_toggle.set_active(False)
            self.clipboard.clear()
            if hasattr(self, "clip_list"):
                self.render_clipboard()
        if not enabled and key == "focus_tools" and self.focus.active:
            self._cancel_focus_timer()
            if not self.focus.disable():
                self.notify("Focus Mode could not restore the previous notification setting.")
        if not enabled and key == "window_switcher":
            self.stop_swipeswitch()
        elif key in {"window_overview", "window_peek"} and self.swipeswitch_process.running:
            if not self.swipeswitch_process.reload():
                self.notify("SwipeSwitch could not reload the updated feature preferences.")
        self.render_features()
        self._apply_feature_preferences()
        self.notify("Feature preference saved. No background service was started.")

    def refresh_diagnostics(self):
        try:
            self.model.refresh_capabilities()
            self.render_features()
            self._apply_feature_preferences()
        except (OSError, ValueError) as exc:
            self.notify(f"Capability refresh failed: {exc}")
            return
        self.notify("Platform capability checks refreshed.")

    def _screen(self):
        """Return the active window monitor's usable work area when possible."""
        display = self.Gdk.Display.get_default()
        x = y = 0
        wnck_screen = self.Wnck.Screen.get_default()
        active = wnck_screen.get_active_window() if wnck_screen else None
        if active is not None:
            wx, wy, ww, wh = active.get_geometry()
            x, y = wx + max(0, ww // 2), wy + max(0, wh // 2)
        monitor = display.get_monitor_at_point(x, y) if display else None
        if monitor:
            rect = (
                monitor.get_workarea()
                if hasattr(monitor, "get_workarea")
                else monitor.get_geometry()
            )
            return rect.x, rect.y, rect.width, rect.height
        screen = self.Gdk.Screen.get_default()
        if screen is None:
            return 0, 0, 0, 0
        if screen.get_n_monitors() > 0:
            rect = screen.get_monitor_workarea(0)
            return rect.x, rect.y, rect.width, rect.height
        return 0, 0, screen.get_width(), screen.get_height()

    def snap_active(self, preset):
        x, y, w, h = self._screen()
        ok = self.snap.snap_active(preset, w, h, x, y)
        self.notify(
            "Snap request sent."
            if ok
            else "Snap failed. Check that wmctrl is installed and an active X11 window exists."
        )

    def _window_objects(self):
        screen = self.Wnck.Screen.get_default()
        if not screen:
            return []
        screen.force_update()
        return [
            w
            for w in screen.get_windows()
            if not w.is_skip_tasklist()
            and w.get_window_type() in (self.Wnck.WindowType.NORMAL, self.Wnck.WindowType.DIALOG)
        ]

    def refresh_windows(self):
        for child in self.window_list.get_children():
            self.window_list.remove(child)
        for win in self._window_objects():
            row = self.Gtk.ListBoxRow()
            box = self.Gtk.Box(spacing=10)
            box.set_border_width(6)
            label = self.Gtk.Label(label=win.get_name() or "Untitled")
            label.set_halign(self.Gtk.Align.START)
            activate = self.Gtk.Button(label="Activate")
            activate.connect(
                "clicked",
                lambda _b, w=win: (self._activate_live_window(w), self.window.present()),
            )
            box.pack_start(label, True, True, 0)
            box.pack_end(activate, False, False, 0)
            row.add(box)
            self.window_list.add(row)
        self.window_list.show_all()

    def _activate_live_window(self, selected):
        xid = int(selected.get_xid())
        screen = self.Wnck.Screen.get_default()
        if screen is None:
            return False
        screen.force_update()
        live = next(
            (window for window in (screen.get_windows() or []) if int(window.get_xid()) == xid),
            None,
        )
        if live is None:
            self.notify("That window has already closed.")
            return False
        return activate_window(live, self.Gdk)

    def _clipboard_changed(self, clipboard, _event):
        if not hasattr(self, "capture_toggle") or not self.capture_toggle.get_active():
            return
        feature = self.model.get_feature("clipboard_history")
        if not feature["enabled"] or not feature["available"]:
            return
        clipboard.request_text(self._on_clipboard_text, None)

    def _on_clipboard_text(self, _clipboard, text, _user_data=None):
        if not text or not hasattr(self, "capture_toggle"):
            return
        if not self.capture_toggle.get_active():
            return
        if self.clipboard.add(text):
            self.render_clipboard()

    def render_clipboard(self):
        if not hasattr(self, "clip_list"):
            return
        for child in self.clip_list.get_children():
            self.clip_list.remove(child)
        query = self.clip_query.get_text() if hasattr(self, "clip_query") else ""
        clips = self.clipboard.search(query)
        if not clips:
            empty = self.Gtk.Label(label="No clipboard entries yet.")
            empty.set_halign(self.Gtk.Align.START)
            empty.get_style_context().add_class("muted")
            row = self.Gtk.ListBoxRow()
            row.add(empty)
            self.clip_list.add(row)
        for clip in clips:
            row = self.Gtk.ListBoxRow()
            content = self.Gtk.Box(orientation=self.Gtk.Orientation.HORIZONTAL, spacing=10)
            content.set_border_width(8)
            details = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=3)
            preview = clip.text.replace("\n", " ").replace("\r", " ")[:220]
            label = self.Gtk.Label(label=preview)
            label.set_halign(self.Gtk.Align.START)
            label.set_xalign(0)
            label.set_line_wrap(True)
            label.set_max_width_chars(72)
            details.pack_start(label, False, False, 0)
            timestamp = datetime.fromtimestamp(clip.captured_at).strftime("%H:%M:%S")
            time_label = self.Gtk.Label(label=timestamp)
            time_label.set_halign(self.Gtk.Align.START)
            time_label.get_style_context().add_class("muted")
            details.pack_start(time_label, False, False, 0)
            copy_button = self.Gtk.Button(label="Copy")
            copy_button.connect(
                "clicked", lambda _button, value=clip.text: self.copy_clipboard(value)
            )
            content.pack_start(details, True, True, 0)
            content.pack_end(copy_button, False, False, 0)
            row.add(content)
            self.clip_list.add(row)
        self.clip_list.show_all()

    def clear_clipboard(self):
        self.clipboard.clear()
        self.render_clipboard()
        self.notify("Clipboard history cleared.")

    def copy_clipboard(self, text):
        self.clipboard_backend.set_text(text, -1)
        self.notify("Clipboard entry copied.")

    def refresh_apps(self):
        count = self.launcher.refresh()
        self.render_apps()
        self.notify(f"Application list refreshed: {count} application(s) found.")

    def render_apps(self):
        if not hasattr(self, "app_list"):
            return
        for child in self.app_list.get_children():
            self.app_list.remove(child)
        self._app_row_entries = {}
        query = self.app_search.get_text() if hasattr(self, "app_search") else ""
        matches = self.launcher.search(query)[:80]
        if not matches:
            empty = self.Gtk.Label(label="No matching applications found.")
            empty.set_halign(self.Gtk.Align.START)
            empty.get_style_context().add_class("muted")
            row = self.Gtk.ListBoxRow()
            row.add(empty)
            self.app_list.add(row)
        for entry in matches:
            row = self.Gtk.ListBoxRow()
            self._app_row_entries[row] = entry
            content = self.Gtk.Box(spacing=10)
            content.set_border_width(6)
            if entry.icon:
                icon_path = Path(entry.icon).expanduser()
                if icon_path.is_absolute() and icon_path.is_file():
                    image = self.Gtk.Image.new_from_file(str(icon_path))
                else:
                    image = self.Gtk.Image.new_from_icon_name(entry.icon, self.Gtk.IconSize.DIALOG)
                content.pack_start(image, False, False, 0)
            labels = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=2)
            name = self.Gtk.Label(label=entry.name)
            name.set_halign(self.Gtk.Align.START)
            name.set_xalign(0)
            labels.pack_start(name, False, False, 0)
            if entry.description:
                description = self.Gtk.Label(label=entry.description)
                description.set_halign(self.Gtk.Align.START)
                description.set_xalign(0)
                description.set_ellipsize(self.Pango.EllipsizeMode.END)
                description.get_style_context().add_class("muted")
                labels.pack_start(description, False, False, 0)
            launch = self.Gtk.Button(label="Launch")
            launch.connect("clicked", lambda _button, item=entry: self.launch_app(item))
            content.pack_start(labels, True, True, 0)
            content.pack_end(launch, False, False, 0)
            row.add(content)
            self.app_list.add(row)
        self.app_list.show_all()

    def _launch_first_app(self, *_args):
        matches = self.launcher.search(self.app_search.get_text())
        if matches:
            self.launch_app(matches[0])

    def show_task_view(self):
        try:
            if not hasattr(self, "window_peek"):
                self.window_peek = WindowPeek()
            swipeswitch_config = load_swipeswitch_config()
            peek_feature = self.model.get_feature("window_peek")
            thumbnails_enabled = (
                swipeswitch_config.thumbnails
                and peek_feature["enabled"]
                and peek_feature["available"]
            )
            if not hasattr(self, "task_view"):
                self.task_view = TaskView(
                    self.Gtk,
                    self.Gdk,
                    self.Pango,
                    self._activate_live_window,
                    preview_callback=(
                        lambda window: self.window_peek.capture_pixbuf(
                            window, max_width=300, max_height=170
                        )
                    )
                    if thumbnails_enabled
                    else None,
                    GLib=self.GLib,
                )
            else:
                self.task_view.preview_callback = (
                    (
                        lambda window: self.window_peek.capture_pixbuf(
                            window, max_width=300, max_height=170
                        )
                    )
                    if thumbnails_enabled
                    else None
                )
            self.task_view.show(self._window_objects())
        except Exception as exc:
            self.notify(f"Task View unavailable: {exc}")

    def show_gesture_conflicts(self):
        from kali_ux.features.gesture_control.conflicts import (
            format_conflict_report,
            inspect_gesture_providers,
        )

        self._dialog(
            "Gesture service conflicts", format_conflict_report(inspect_gesture_providers())
        )

    def _launch_app_row(self, _listbox, row):
        entry = self._app_row_entries.get(row)
        if entry is not None:
            self.launch_app(entry)

    def launch_app(self, entry):
        if not self.launcher.launch(entry):
            self.notify(
                f"Could not start {entry.name}. Check that gio is installed and "
                "the desktop entry is valid."
            )
        else:
            self.notify(f"Launch requested: {entry.name}")

    def _on_destroy(self, *_args):
        self._cancel_focus_timer()
        self._stop_swipeswitch_on_exit()
        if self.focus.active and not self.focus.disable():
            import logging

            logging.getLogger(__name__).error(
                "Kali UX closed while focus mode could not restore the previous XFCE setting"
            )
        self.Gtk.main_quit()

    def _cancel_focus_timer(self):
        if self._focus_timer_id is not None:
            self.GLib.source_remove(self._focus_timer_id)
            self._focus_timer_id = None

    def start_focus_session(self):
        self._cancel_focus_timer()
        if self.focus.active and not self.focus.disable():
            self.notify(
                "Could not restore the previous notification setting before restarting focus mode."
            )
            return
        if not self.focus.enable():
            self.notify(
                "Could not enable focus mode; XFCE notification settings may be unavailable."
            )
            return
        minutes = self.focus_duration.get_value_as_int()
        self._focus_timer_id = self.GLib.timeout_add_seconds(
            minutes * 60, self._finish_focus_session
        )
        self.notify(f"Focus mode enabled for {minutes} minutes.")

    def _finish_focus_session(self):
        self._focus_timer_id = None
        restored = self.focus.disable()
        if self.window.get_visible():
            self.notify(
                "Focus session complete. Notifications restored."
                if restored
                else (
                    "Focus session ended, but XFCE could not restore the previous "
                    "notification setting."
                )
            )
        return self.GLib.SOURCE_REMOVE

    def enable_focus(self):
        self.notify(
            "Focus mode enabled."
            if self.focus.enable()
            else "Could not enable focus mode; XFCE notification property may be unavailable."
        )

    def disable_focus(self):
        self._cancel_focus_timer()
        self.notify(
            "Previous notification setting restored."
            if self.focus.disable()
            else "No saved focus-mode state to restore."
        )

    def capture_layout(self):
        name = self.layout_name.get_text().strip()
        ok = self.layouts.capture(name)
        self.refresh_layouts(name if ok else None)
        self.notify(
            "Layout saved." if ok else "Could not save layout; check wmctrl and the layout name."
        )

    def refresh_layouts(self, preferred=None):
        selected = preferred or self.layout_combo.get_active_text()
        names = self.layouts.names()
        self.layout_combo.remove_all()
        for name in names:
            self.layout_combo.append_text(name)
        if selected in names:
            self.layout_combo.set_active(names.index(selected))
        elif names:
            self.layout_combo.set_active(0)

    def restore_layout(self):
        name = self.layout_combo.get_active_text()
        count = self.layouts.restore(name) if name else 0
        self.notify(f"Requested geometry restoration for {count} matching window(s).")

    def delete_layout(self):
        name = self.layout_combo.get_active_text()
        deleted = self.layouts.delete(name) if name else False
        self.refresh_layouts()
        self.notify("Layout deleted." if deleted else "Select a saved layout to delete.")

    def open_config_folder(self):
        try:
            CONFIG_HOME.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.notify(f"Could not create the configuration folder: {exc}")
            return
        result = start_command(["xdg-open", str(CONFIG_HOME)])
        if not result.started:
            self.notify(
                "Could not open the configuration folder; check that xdg-open is installed."
            )

    def start_swipeswitch(self):
        started, message = self.swipeswitch_process.start()
        if not started:
            self.notify(message)
            return
        self._swipeswitch_stop_requested = False
        self._swipeswitch_stop_deadline = None
        self._set_swipeswitch_button(True)
        if self._swipeswitch_poll_id is None:
            self._swipeswitch_poll_id = self.GLib.timeout_add(300, self._poll_swipeswitch)
        self.notify(message)

    def toggle_swipeswitch(self):
        if self.swipeswitch_process.running:
            self.stop_swipeswitch()
        else:
            self.start_swipeswitch()

    def stop_swipeswitch(self):
        process = self.swipeswitch_process
        if not process.running:
            process.collect_exit_code()
            self._set_swipeswitch_button(False)
            return
        if self._swipeswitch_stop_deadline is None:
            self._swipeswitch_stop_requested = True
            self._swipeswitch_stop_deadline = time.monotonic() + 2.0
            process.terminate()
            self.notify("Stopping SwipeSwitch…")
        if self._swipeswitch_poll_id is None:
            self._swipeswitch_poll_id = self.GLib.timeout_add(200, self._poll_swipeswitch)

    def _poll_swipeswitch(self):
        process = self.swipeswitch_process
        if not process.has_process:
            self._swipeswitch_poll_id = None
            return self.GLib.SOURCE_REMOVE
        returncode = process.collect_exit_code()
        if returncode is None and process.has_process:
            if process.running:
                if (
                    self._swipeswitch_stop_deadline is not None
                    and time.monotonic() >= self._swipeswitch_stop_deadline
                ):
                    process.kill()
                    self._swipeswitch_stop_deadline = time.monotonic() + 1.0
                return True
            returncode = process.collect_exit_code()
            if returncode is None and process.has_process:
                return True
        self._swipeswitch_stop_deadline = None
        self._set_swipeswitch_button(False)
        self._swipeswitch_poll_id = None
        if self._swipeswitch_stop_requested:
            self.notify("SwipeSwitch stopped.")
        elif returncode != 0:
            self.notify(f"SwipeSwitch exited with status {returncode}. Review the SwipeSwitch log.")
        self._swipeswitch_stop_requested = False
        return self.GLib.SOURCE_REMOVE

    def _set_swipeswitch_button(self, running):
        if self.swipeswitch_button is not None:
            self.swipeswitch_button.set_label(
                "Stop SwipeSwitch" if running else "Start SwipeSwitch"
            )

    def _stop_swipeswitch_on_exit(self):
        self.swipeswitch_process.shutdown(timeout=1.5)
        if self._swipeswitch_poll_id is not None:
            self.GLib.source_remove(self._swipeswitch_poll_id)
            self._swipeswitch_poll_id = None
        self._set_swipeswitch_button(False)

    def show_diagnostics(self, *_):
        try:
            report = build_report()
        except (OSError, ValueError) as exc:
            self.notify(f"Diagnostics unavailable: {exc}")
            return
        self._dialog("System diagnostics", json.dumps(report, indent=2))

    def show_status(self):
        self.show_diagnostics()

    def _dialog(self, title, content):
        dialog = self.Gtk.Dialog(
            title=title, transient_for=self.window, flags=self.Gtk.DialogFlags.MODAL
        )
        dialog.add_button("Close", self.Gtk.ResponseType.CLOSE)
        view = self.Gtk.TextView()
        view.set_editable(False)
        view.set_monospace(True)
        view.get_buffer().set_text(content)
        scroll = self.Gtk.ScrolledWindow()
        scroll.set_size_request(760, 480)
        scroll.add(view)
        dialog.get_content_area().pack_start(scroll, True, True, 8)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def notify(self, message):
        dialog = self.Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=self.Gtk.MessageType.INFO,
            buttons=self.Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()


def main():
    Gdk, GLib, Gtk, Pango, Wnck = _gtk()
    _window = KaliUXWindow(Gtk, Gdk, GLib, Pango, Wnck)
    Gtk.main()
    return 0
