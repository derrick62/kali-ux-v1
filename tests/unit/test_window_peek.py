import sys
from types import ModuleType, SimpleNamespace

from kali_ux.features.window_peek.service import WindowPeek


class FakePixbuf:
    def __init__(self, width=1000, height=500):
        self.width = width
        self.height = height

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def scale_simple(self, width, height, interpolation):
        return (width, height, interpolation)


class FakeWindow:
    def is_minimized(self):
        return False

    def get_xid(self):
        return 123


def install_fake_gi(monkeypatch, *, minimized=False, pixbuf=None):
    gi = ModuleType("gi")
    gi.require_version = lambda *_args: None
    repository = ModuleType("gi.repository")
    native = SimpleNamespace(get_width=lambda: 1000, get_height=lambda: 500)
    display = object()
    gdk = SimpleNamespace(
        Display=SimpleNamespace(get_default=lambda: display),
        pixbuf_get_from_window=lambda *_args: pixbuf or FakePixbuf(),
    )
    gdkx11 = SimpleNamespace(
        X11Window=SimpleNamespace(
            foreign_new_for_display=lambda _display, xid: native if xid == 123 else None
        )
    )
    gdkpixbuf = SimpleNamespace(InterpType=SimpleNamespace(BILINEAR=7))
    repository.Gdk = gdk
    repository.GdkX11 = gdkx11
    repository.GdkPixbuf = gdkpixbuf
    gi.repository = repository
    monkeypatch.setitem(sys.modules, "gi", gi)
    monkeypatch.setitem(sys.modules, "gi.repository", repository)

    window = FakeWindow()
    window.is_minimized = lambda: minimized
    return window


def test_window_peek_captures_and_scales_x11_thumbnail(monkeypatch):
    window = install_fake_gi(monkeypatch)
    result = WindowPeek().capture_pixbuf(window)
    assert result == (420, 210, 7)


def test_window_peek_skips_minimized_windows(monkeypatch):
    window = install_fake_gi(monkeypatch, minimized=True)
    assert WindowPeek().capture_pixbuf(window) is None
