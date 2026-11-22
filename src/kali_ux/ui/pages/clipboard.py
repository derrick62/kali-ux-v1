"""GTK3 page composition for the Kali UX Control Center."""


def clipboard(app):
    page = app._page("Clipboard", "clipboard")
    app._card(
        page,
        "Private clipboard history",
        "Recent text is held in memory only. Password-like content is not "
        "automatically detectable; pause capture before copying secrets. "
        "History is cleared when this application exits.",
    )
    bar = app.Gtk.Box(spacing=8)
    page.pack_start(bar, False, False, 0)
    app.capture_toggle = app.Gtk.CheckButton(label="Capture copied text during this session")
    app.capture_toggle.set_active(False)
    app._bind_feature_control("clipboard_history", app.capture_toggle)
    bar.pack_start(app.capture_toggle, False, False, 0)
    app._button(bar, "Clear history", app.clear_clipboard)
    app.clip_query = app.Gtk.Entry()
    app.clip_query.set_placeholder_text("Search clipboard history…")
    page.pack_start(app.clip_query, False, False, 0)
    app.clip_query.connect("changed", lambda *_: app.render_clipboard())
    app.clip_list = app.Gtk.ListBox()
    app.clip_scroll = app.Gtk.ScrolledWindow()
    app.clip_scroll.add(app.clip_list)
    page.pack_start(app.clip_scroll, True, True, 0)
    app.render_clipboard()
