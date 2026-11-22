"""Simple persistent GTK3 window overview used by the Task View gesture."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class TaskView:
    def __init__(self, Gtk, Gdk, Pango, activate_callback, preview_callback=None, GLib=None):
        self.Gtk, self.Gdk, self.Pango, self.GLib = Gtk, Gdk, Pango, GLib
        self.activate_callback = activate_callback
        self.preview_callback = preview_callback
        self.windows = []
        self.cards = []
        self.selected_index = 0
        self.preview_slots = []
        self.preview_index = 0
        self.preview_generation = 0
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("SwipeSwitch Task View")
        self.window.set_name("swipeswitch-task-view")
        self.window.set_decorated(False)
        self.window.get_style_context().add_class("task-view")
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_default_size(1024, 680)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("key-press-event", self._on_key)
        self.window.connect("delete-event", self._on_delete)
        self.window.connect("focus-out-event", self._on_focus_out)
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(
            b"""
            window.task-view {
                background-color: @theme_bg_color;
                color: @theme_fg_color;
            }
            window.task-view label { color: @theme_fg_color; }
            window.task-view label.muted { color: @insensitive_fg_color; }
            button.task-card {
                background-color: @theme_base_color;
                color: @theme_text_color;
                border: 1px solid @borders;
                border-radius: 12px;
                padding: 14px;
            }
            button.task-card:hover, button.task-card.selected {
                background-color: @theme_selected_bg_color;
                color: @theme_selected_fg_color;
                border-color: @theme_selected_bg_color;
            }
            label.task-title { color: @theme_text_color; }
            """
        )
        self.window.get_style_context().add_provider(
            self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.root.set_border_width(24)
        heading = Gtk.Label(label="Open windows")
        heading.set_halign(Gtk.Align.START)
        heading.get_style_context().add_class("heading")
        self.root.pack_start(heading, False, False, 0)
        self.grid = Gtk.FlowBox()
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grid.set_max_children_per_line(3)
        self.grid.set_min_children_per_line(1)
        self.grid.set_column_spacing(14)
        self.grid.set_row_spacing(14)
        self.grid.set_homogeneous(True)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.grid)
        self.root.pack_start(scroll, True, True, 0)
        footer = Gtk.Label(label="Select a window · Esc to close")
        footer.set_halign(Gtk.Align.END)
        footer.set_opacity(0.7)
        self.root.pack_start(footer, False, False, 0)
        self.window.add(self.root)
        self.window.hide()

    def show(self, windows):
        self.windows = list(windows)
        for child in self.grid.get_children():
            self.grid.remove(child)
        self.cards = []
        self.preview_slots = []
        self.preview_index = 0
        self.preview_generation += 1
        generation = self.preview_generation
        self.selected_index = 0
        for window in self.windows:
            button = self.Gtk.Button()
            button.get_style_context().add_class("task-card")
            content = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=10)
            icon = window.get_icon()
            image = self.Gtk.Image()
            image.set_size_request(300, 170)
            if icon is not None:
                image.set_from_pixbuf(icon)
                image.set_pixel_size(48)
            content.pack_start(image, True, True, 0)
            if self.preview_callback is not None:
                self.preview_slots.append((image, window))
            title = self.Gtk.Label(label=(window.get_name() or "Untitled window")[:90])
            title.set_line_wrap(True)
            title.set_max_width_chars(24)
            title.get_style_context().add_class("task-title")
            content.pack_start(title, False, False, 0)
            button.add(content)
            button.connect("clicked", self._on_select, window)
            self.cards.append(button)
            self.grid.add(button)
        self.window.show_all()
        self._center_on_pointer_monitor()
        self._select_card(0)
        self.window.present()
        if self.GLib is not None and self.preview_slots:
            self.GLib.idle_add(self._capture_next_preview, generation)

    def _center_on_pointer_monitor(self):
        try:
            display = self.Gdk.Display.get_default()
            monitor = None
            seat = display.get_default_seat() if display else None
            pointer = seat.get_pointer() if seat else None
            if pointer is not None:
                _screen, px, py = pointer.get_position()
                monitor = display.get_monitor_at_point(px, py)
            if monitor is None and display is not None:
                monitor = display.get_primary_monitor() or display.get_monitor(0)
            if monitor is None:
                return
            geometry = monitor.get_geometry()
            width = min(1200, max(520, geometry.width - 48))
            height = min(800, max(380, geometry.height - 48))
            self.window.set_default_size(width, height)
            self.window.move(
                geometry.x + (geometry.width - width) // 2,
                geometry.y + (geometry.height - height) // 2,
            )
        except Exception:
            log.debug("Could not position Task View on the pointer monitor", exc_info=True)

    def _on_select(self, _button, window):
        self.hide()
        self.activate_callback(window)

    def _capture_next_preview(self, generation):
        if (
            generation != self.preview_generation
            or self.preview_index >= len(self.preview_slots)
            or not self.window.get_visible()
        ):
            return False
        image, window = self.preview_slots[self.preview_index]
        self.preview_index += 1
        try:
            if not window.is_minimized():
                pixbuf = self.preview_callback(window)
                if pixbuf is not None:
                    image.set_from_pixbuf(pixbuf)
        except Exception:
            log.debug("Could not refresh Task View thumbnail", exc_info=True)
        return self.preview_index < len(self.preview_slots)

    def _select_card(self, index):
        if not self.cards:
            return
        self.selected_index = index % len(self.cards)
        for position, card in enumerate(self.cards):
            context = card.get_style_context()
            if position == self.selected_index:
                context.add_class("selected")
            else:
                context.remove_class("selected")
        self.cards[self.selected_index].grab_focus()

    def _on_key(self, _window, event):
        if event.keyval == self.Gdk.KEY_Escape:
            self.hide()
            return True
        if event.keyval in (self.Gdk.KEY_Right, self.Gdk.KEY_Down):
            self._select_card(self.selected_index + 1)
            return True
        if event.keyval in (self.Gdk.KEY_Left, self.Gdk.KEY_Up):
            self._select_card(self.selected_index - 1)
            return True
        if event.keyval in (self.Gdk.KEY_Return, self.Gdk.KEY_KP_Enter, self.Gdk.KEY_space):
            if self.cards:
                self.cards[self.selected_index].clicked()
            return True
        return False

    def _on_delete(self, *_args):
        self.hide()
        return True

    def _on_focus_out(self, *_args):
        # Clicking elsewhere dismisses the overview without activating a card.
        self.hide()
        return False

    def hide(self):
        self.preview_generation += 1
        self.window.hide()
