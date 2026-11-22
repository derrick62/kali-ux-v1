"""Explicit GTK 3 / GDK 3 / libwnck 3 namespace loading."""

from __future__ import annotations


def load_gtk3():
    """Load the GTK3 stack without allowing PyGObject to select GTK4 namespaces."""
    try:
        import gi
    except ImportError as exc:
        raise RuntimeError(
            "Kali UX needs PyGObject and GTK3. Install python3-gi, "
            "gir1.2-gtk-3.0 and gir1.2-wnck-3.0 from apt."
        ) from exc

    try:
        # Gdk must be pinned explicitly: importing it unversioned can cause
        # PyGObject to load GDK4 before Gtk3 asks for GDK3.
        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        gi.require_version("Wnck", "3.0")
        gi.require_version("Pango", "1.0")
        from gi.repository import Gdk, GLib, Gtk, Pango, Wnck
    except (ValueError, gi.RepositoryError) as exc:
        raise RuntimeError(
            "Kali UX needs a consistent GTK3 stack. Install python3-gi, "
            "gir1.2-gtk-3.0 and gir1.2-wnck-3.0 from apt; do not mix GTK3 and GTK4."
        ) from exc

    return Gdk, GLib, Gtk, Pango, Wnck
