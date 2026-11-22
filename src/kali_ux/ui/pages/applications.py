"""GTK3 page composition for the Kali UX Control Center."""


def launcher(app):
    page = app._page("Applications", "applications")
    app._card(
        page,
        "Application launcher",
        "Search installed XDG desktop entries. Applications are launched through "
        "the desktop environment, without shell evaluation.",
    )
    app._bind_feature_control(
        "launcher", app._button(page, "Refresh application list", app.refresh_apps)
    )
    app.app_search = app.Gtk.SearchEntry()
    app.app_search.set_placeholder_text("Search applications…")
    app._bind_feature_control("launcher", app.app_search)
    page.pack_start(app.app_search, False, False, 0)
    app.app_list = app.Gtk.ListBox()
    app.app_list.connect("row-activated", app._launch_app_row)
    app._app_row_entries = {}
    scroll = app.Gtk.ScrolledWindow()
    scroll.add(app.app_list)
    app._bind_feature_control("launcher", app.app_list)
    page.pack_start(scroll, True, True, 0)
    app.app_search.connect("search-changed", lambda *_: app.render_apps())
    app.app_search.connect("activate", app._launch_first_app)
    app.render_apps()
