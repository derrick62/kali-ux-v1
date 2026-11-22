import sys
from types import ModuleType


def test_gtk_loader_pins_all_gtk3_namespaces_before_import(monkeypatch):
    requested = []
    gi = ModuleType("gi")
    gi.require_version = lambda namespace, version: requested.append((namespace, version))
    gi.RepositoryError = type("RepositoryError", (Exception,), {})
    repository = ModuleType("gi.repository")
    for name in ("Gdk", "GLib", "Gtk", "Pango", "Wnck"):
        setattr(repository, name, object())
    gi.repository = repository
    monkeypatch.setitem(sys.modules, "gi", gi)
    monkeypatch.setitem(sys.modules, "gi.repository", repository)

    from kali_ux.platform.gtk import load_gtk3

    loaded = load_gtk3()
    assert len(loaded) == 5
    assert requested == [
        ("Gtk", "3.0"),
        ("Gdk", "3.0"),
        ("Wnck", "3.0"),
        ("Pango", "1.0"),
    ]
