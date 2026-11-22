"""Pre-created GTK3 switcher overlay."""

import logging
import time

from gi.repository import Pango

from .thumbs import capture_thumbnail

log = logging.getLogger(__name__)

DARK_CSS = """
window#swipeswitch-overlay {
    background-color: rgba(12, 15, 22, 0.88);
}
.frame {
    background-color: rgba(28, 33, 45, 0.96);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 14px;
}
.card {
    background-color: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px;
    min-width: 188px;
    min-height: 150px;
}
.card.selected {
    background-color: rgba(55,112,220,0.24);
    border: 2px solid #6ea8ff;
}
.title { color: #f3f5f8; font-size: 12px; }
.preview-area { background-color: rgba(4, 7, 12, 0.72); border-radius: 8px; }
.icon { color: #dce6f5; font-size: 28px; }
"""
LIGHT_CSS = """
window#swipeswitch-overlay { background-color: rgba(25,30,40,0.55); }
.frame {
    background-color: rgba(245,247,250,0.98);
    border: 1px solid #d6dce5;
    border-radius: 16px;
    padding: 14px;
}
.card {
    background-color: #fff;
    border: 1px solid #dce2ea;
    border-radius: 12px;
    padding: 12px;
    min-width: 188px;
    min-height: 150px;
}
.card.selected { background-color: #e5efff; border: 2px solid #2878e8; }
.title { color: #18202c; font-size: 12px; }
.preview-area { background-color: rgba(25, 36, 52, 0.10); border-radius: 8px; }
.icon { color: #315b91; font-size: 28px; }
"""


class SwitcherOverlay:
    def __init__(self, Gtk, Gdk, config, GLib=None):
        self.Gtk, self.Gdk, self.config, self.GLib = Gtk, Gdk, config, GLib
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_name("swipeswitch-overlay")
        self.window.set_title("swipeswitch-overlay")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_accept_focus(False)
        self.window.set_focus_on_map(False)
        self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.window.set_app_paintable(True)
        self.window.connect("draw", self._draw_fallback)
        self.css = Gtk.CssProvider()
        self.screen = Gdk.Screen.get_default()
        self._apply_css()
        self.outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.outer.set_halign(Gtk.Align.CENTER)
        self.outer.set_valign(Gtk.Align.CENTER)
        self.frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.frame.get_style_context().add_class("frame")
        self.scroller = Gtk.ScrolledWindow()
        self.scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.scroller.set_shadow_type(Gtk.ShadowType.NONE)
        self.scroller.add(self.frame)
        self.outer.pack_start(self.scroller, True, True, 0)
        self.window.add(self.outer)
        self.cards, self.windows, self.selected = [], [], 0
        self.preview_slots = []
        self.preview_index = 0
        self.preview_generation = 0
        self.window.hide()

    def _apply_css(self):
        theme = self.config.theme
        if theme == "auto":
            settings = self.Gtk.Settings.get_default()
            theme_name = ""
            prefer_dark = False
            if settings is not None:
                try:
                    theme_name = str(settings.get_property("gtk-theme-name") or "")
                    prefer_dark = bool(settings.get_property("gtk-application-prefer-dark-theme"))
                except Exception:
                    pass
            theme = "dark" if prefer_dark or "dark" in theme_name.casefold() else "light"
        css = LIGHT_CSS if theme == "light" else DARK_CSS
        try:
            self.css.load_from_data(css.encode())
            self.Gtk.StyleContext.add_provider_for_screen(
                self.screen, self.css, self.Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception:
            log.exception("Could not apply overlay CSS")

    def update_config(self, config):
        self.config = config
        self._apply_css()

    def _draw_fallback(self, widget, cr):
        try:
            if not self.Gdk.Screen.get_default().is_composited():
                cr.set_source_rgb(0.055, 0.065, 0.09)
                cr.paint()
        except Exception:
            pass
        return False

    def show(self, windows, selected_index=0):
        self.windows, self.selected = list(windows), selected_index
        self._rebuild()
        self.window.show_all()
        self.window.present()
        self.window.set_keep_above(True)
        self._center_on_primary()
        if self.GLib is not None and self.preview_slots:
            generation = self.preview_generation
            self.GLib.idle_add(self._capture_next_preview, generation)

    def _center_on_primary(self):
        try:
            display = self.Gdk.Display.get_default()
            monitor = None
            if display is not None and self.config.monitor == "pointer":
                seat = display.get_default_seat()
                pointer = seat.get_pointer() if seat else None
                if pointer is not None:
                    _screen, px, py = pointer.get_position()
                    monitor = display.get_monitor_at_point(px, py)
            if monitor is None and display is not None:
                monitor = display.get_primary_monitor() or display.get_monitor(0)
            if monitor is None:
                raise RuntimeError("No display monitor is available")
            geo = monitor.get_geometry()
            width = min(900, max(420, geo.width - 48))
            height = min(260, max(190, geo.height - 48))
            self.window.set_default_size(width, height)
            self.window.move(geo.x + (geo.width - width) // 2, geo.y + (geo.height - height) // 2)
        except Exception:
            self.window.set_position(self.Gtk.WindowPosition.CENTER)

    def _rebuild(self):
        for child in self.frame.get_children():
            self.frame.remove(child)
        self.cards = []
        self.preview_slots = []
        self.preview_index = 0
        self.preview_generation += 1
        for index, window in enumerate(self.windows):
            card = self.Gtk.Box(orientation=self.Gtk.Orientation.VERTICAL, spacing=8)
            card.set_halign(self.Gtk.Align.CENTER)
            context = card.get_style_context()
            context.add_class("card")
            if index == self.selected:
                context.add_class("selected")

            preview = self.Gtk.Image()
            preview.set_size_request(180, 100)
            preview.get_style_context().add_class("preview-area")
            icon = window.get_icon()
            if icon is not None:
                preview.set_from_pixbuf(icon)
                preview.set_pixel_size(48)
            card.pack_start(preview, True, True, 0)
            if self.config.thumbnails:
                self.preview_slots.append((preview, window))

            title = self.Gtk.Label(label=(window.get_name() or "Untitled window")[:54])
            title.set_ellipsize(Pango.EllipsizeMode.END)
            title.set_max_width_chars(26)
            title.get_style_context().add_class("title")
            card.pack_start(title, False, False, 0)
            self.frame.pack_start(card, False, False, 0)
            self.cards.append(card)
        self.frame.show_all()

    def _capture_next_preview(self, generation):
        if generation != self.preview_generation or not self.window.get_visible():
            return False
        deadline = time.monotonic() + max(1, self.config.thumb_budget_ms) / 1000.0
        start_index = self.preview_index
        while self.preview_index < len(self.preview_slots):
            image, window = self.preview_slots[self.preview_index]
            self.preview_index += 1
            try:
                if not window.is_minimized():
                    pixbuf = capture_thumbnail(window, self.Gdk, max_width=180, max_height=100)
                    if pixbuf is not None:
                        image.set_from_pixbuf(pixbuf)
            except Exception:
                log.debug("Window thumbnail capture failed", exc_info=True)
            if self.preview_index > start_index and time.monotonic() >= deadline:
                break
        return self.preview_index < len(self.preview_slots)

    def update_selection(self, selected_index):
        if not self.cards:
            return
        selected_index %= len(self.cards)
        if selected_index == self.selected:
            return
        self.cards[self.selected].get_style_context().remove_class("selected")
        self.selected = selected_index
        self.cards[self.selected].get_style_context().add_class("selected")
        self._scroll_selected_into_view()

    def _scroll_selected_into_view(self):
        if not self.cards or not self.scroller.get_realized():
            return
        card = self.cards[self.selected]
        allocation = card.get_allocation()
        adjustment = self.scroller.get_hadjustment()
        current = adjustment.get_value()
        page_size = adjustment.get_page_size()
        if allocation.x < current:
            adjustment.set_value(allocation.x)
        elif allocation.x + allocation.width > current + page_size:
            adjustment.set_value(allocation.x + allocation.width - page_size)

    def hide(self):
        self.preview_generation += 1
        self.window.hide()
