# Debian packaging preparation

Debian packaging is intentionally deferred until the alpha feature boundaries and runtime dependencies are verified on the target Kali release. The future package should depend on distribution GTK3/PyGObject/libwnck packages, install only application-owned files, preserve user configuration on upgrade/removal, and not enable autostart or gesture input without an explicit opt-in.
