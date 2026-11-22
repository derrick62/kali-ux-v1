"""GTK3 productivity and desktop utility page."""

from kali_ux.features.quick_panel.actions import ACTIONS, action_available, open_action


def productivity(app):
    page = app._page("Productivity", "productivity")
    app._card(
        page,
        "Focus mode",
        "Temporarily request XFCE notification do-not-disturb. The previous "
        "value is restored when you disable it in this session.",
    )
    row = app.Gtk.Box(spacing=8)
    page.pack_start(row, False, False, 0)
    duration = app.Gtk.SpinButton.new_with_range(5, 240, 5)
    duration.set_value(25)
    duration.set_numeric(True)
    duration.set_tooltip_text("Focus session duration in minutes")
    app.focus_duration = duration
    row.pack_start(duration, False, False, 0)
    row.pack_start(app.Gtk.Label(label="minutes"), False, False, 0)
    app._bind_feature_control(
        "focus_tools", app._button(row, "Start focus session", app.start_focus_session)
    )
    app._bind_feature_control(
        "focus_tools", app._button(row, "Restore notifications", app.disable_focus)
    )
    app._card(
        page,
        "Quick Settings",
        "Open the existing XFCE settings applications rather than reimplementing system controls.",
    )
    grid = app.Gtk.Grid(column_spacing=8, row_spacing=8)
    page.pack_start(grid, False, False, 0)
    for i, key in enumerate(ACTIONS):
        b = app.Gtk.Button(label=key.title())
        available = action_available(key)
        b.set_sensitive(available)
        if not available:
            b.set_tooltip_text(f"The optional {ACTIONS[key][0]} application is not installed.")
        b.connect(
            "clicked",
            lambda _b, k=key: app.notify(
                "Launch requested."
                if open_action(k)
                else f"Could not start {k} settings; check optional packages."
            ),
        )
        app._bind_feature_control("quick_panel", b)
        grid.attach(b, i % 3, i // 3, 1, 1)
    app._card(
        page,
        "Layout memory",
        "Save current window geometry under a name, then request restoration "
        "later. This is best-effort and cannot guarantee exact monitor/workspace recovery.",
    )
    entry = app.Gtk.Entry()
    entry.set_placeholder_text("Layout name")
    page.pack_start(entry, False, False, 0)
    app.layout_name = entry
    row2 = app.Gtk.Box(spacing=8)
    page.pack_start(row2, False, False, 0)
    app._bind_feature_control(
        "layout_memory", app._button(row2, "Save current layout", app.capture_layout)
    )
    app._bind_feature_control(
        "layout_memory", app._button(row2, "Restore selected layout", app.restore_layout)
    )
    app._bind_feature_control(
        "layout_memory", app._button(row2, "Delete selected layout", app.delete_layout)
    )
    app.layout_combo = app.Gtk.ComboBoxText()
    app._bind_feature_control("layout_memory", app.layout_combo)
    app._bind_feature_control("layout_memory", app.layout_name)
    page.pack_start(app.layout_combo, False, False, 0)
    app.refresh_layouts()
