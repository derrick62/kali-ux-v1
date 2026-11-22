"""GTK3 page composition for the Kali UX Control Center."""


def home(app):
    page = app._page("Overview", "overview")
    app._card(
        page,
        "Your desktop, brought together",
        "Use the tabs to switch windows, arrange your workspace, search applications, "
        "manage clipboard history and access common XFCE settings.",
    )
    grid = app.Gtk.Grid(column_spacing=12, row_spacing=12)
    page.pack_start(grid, False, False, 0)
    items = [
        ("Window switching", "Open the SwipeSwitch interface", app.start_swipeswitch),
        ("Task View", "See and select open windows", app.show_task_view),
        ("Snap Assist", "Arrange the active window", lambda: app.show_page("windows")),
        (
            "Application launcher",
            "Find and launch applications",
            lambda: app.show_page("applications"),
        ),
        (
            "Clipboard history",
            "Review recent copied text",
            lambda: app.show_page("clipboard"),
        ),
        ("Diagnostics", "Check desktop capabilities", app.show_diagnostics),
    ]
    for i, (name, desc, cb) in enumerate(items):
        card = app.Gtk.Button()
        content = app.Gtk.Box(orientation=app.Gtk.Orientation.VERTICAL, spacing=6)
        h = app.Gtk.Label()
        h.set_markup(f"<b>{name}</b>")
        h.set_halign(app.Gtk.Align.START)
        d = app.Gtk.Label(label=desc)
        d.set_line_wrap(True)
        d.set_halign(app.Gtk.Align.START)
        content.pack_start(h, False, False, 0)
        content.pack_start(d, False, False, 0)
        card.add(content)
        card.connect("clicked", lambda _b, f=cb: f())
        feature_key = {
            "Window switching": "window_switcher",
            "Task View": "window_overview",
            "Snap Assist": "snap_assist",
            "Application launcher": "launcher",
            "Clipboard history": "clipboard_history",
        }.get(name)
        if feature_key:
            app._bind_feature_control(feature_key, card)
        grid.attach(card, i % 2, i // 2, 1, 1)
