"""GTK3 page composition for the Kali UX Control Center."""


def windows(app):
    page = app._page("Windows", "windows")
    app._card(
        page,
        "Window overview and snapping",
        "Task View uses libwnck to inspect windows. Snap presets request geometry "
        "changes through wmctrl; xfwm4 remains authoritative.",
    )
    row = app.Gtk.Box(spacing=8)
    page.pack_start(row, False, False, 0)
    app._bind_feature_control(
        "window_overview", app._button(row, "Open Task View", app.show_task_view)
    )
    app._bind_feature_control(
        "window_overview", app._button(row, "Refresh window list", app.refresh_windows)
    )
    app.window_list = app.Gtk.ListBox()
    app.window_list.set_selection_mode(app.Gtk.SelectionMode.NONE)
    app._bind_feature_control("window_overview", app.window_list)
    scroll = app.Gtk.ScrolledWindow()
    scroll.set_min_content_height(170)
    scroll.add(app.window_list)
    page.pack_start(scroll, True, True, 0)
    app.refresh_windows()
    app._card(
        page,
        "Snap Assist",
        "Choose a layout for the currently active window. Display work-area and "
        "multi-monitor calibration will be refined during live desktop testing.",
    )
    snapgrid = app.Gtk.Grid(column_spacing=8, row_spacing=8)
    page.pack_start(snapgrid, False, False, 0)
    presets = [
        "left",
        "right",
        "top",
        "bottom",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]
    for i, p in enumerate(presets):
        b = app.Gtk.Button(label=p.replace("-", " ").title())
        b.connect("clicked", lambda _b, preset=p: app.snap_active(preset))
        app._bind_feature_control("snap_assist", b)
        snapgrid.attach(b, i % 4, i // 4, 1, 1)
