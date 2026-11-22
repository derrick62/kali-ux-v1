"""GTK3 page composition for the Kali UX Control Center."""


def features(app):
    page = app._page("Features", "features")
    app._card(
        page,
        "Feature management",
        "Enable only features that are implemented and whose requirements are "
        "available on this desktop. Enabling a feature changes its preference; "
        "it does not start background services or alter system settings.",
    )
    app.feature_rows = app.Gtk.Box(orientation=app.Gtk.Orientation.VERTICAL, spacing=8)
    page.pack_start(app.feature_rows, True, True, 0)
    app.render_features()
