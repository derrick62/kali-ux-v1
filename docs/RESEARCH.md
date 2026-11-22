# Kali UX — Research Notes and Technical Constraints

**Date:** 2026-11-19
**Purpose:** Record the evidence behind the initial platform and engineering choices. This is not a substitute for testing the actual target laptop.

## 1. Kali desktop and display-server context

Kali documentation distinguishes display-server choices by desktop environment. Its Wayland page states that Xfce uses X11, while Kali GNOME and KDE have different defaults. Therefore, “Kali Linux” alone is not a sufficient compatibility declaration. Kali UX explicitly targets XFCE/X11 first and should inspect `$XDG_SESSION_TYPE` at runtime.

Source: Kali Linux, [Wayland](https://www.kali.org/docs/general-use/wayland/).

Kali's XFCE documentation describes XFCE-specific configuration and compositor considerations. Compositing state can affect translucency and screenshot/thumbnail expectations; the UI must have a usable opaque fallback.

Source: Kali Linux, [Kali Linux Xfce FAQ](https://www.kali.org/docs/general-use/xfce-faq/).

## 2. Window management

The Extended Window Manager Hints (EWMH) specification standardizes interactions among X11 window managers, compositors and desktop utilities on top of ICCCM. This supports the decision to request supported operations from the window manager rather than implement a competing window manager.

Source: freedesktop.org, [EWMH specification](https://specifications.freedesktop.org/wm/latest-single/).

EWMH does not guarantee that every requested operation is supported or accepted identically by every window manager. Validate each operation against `xfwm4`, and treat `libwnck` as a candidate API rather than a blanket guarantee.

## 3. Gesture input

The libinput documentation describes `libinput debug-events` as a tool that prints events from devices and helps diagnose device behaviour. That makes it useful for collecting actual event fixtures and understanding the touchpad. It does not by itself establish that parsing its human-readable command output is the best long-term production interface.

Source: libinput, [Helper tools — libinput debug-events](https://wayland.freedesktop.org/libinput/doc/latest/tools.html).

The project must experimentally determine:
- Which event source is available on the target system.
- Whether the event format is stable enough for the intended use.
- How device selection and permissions work.
- Whether the stream can be restricted to the touchpad.
- How cancellation, finger-count changes and reconnects are represented.
- How the application coexists with other gesture tools.

No user/group permission change should be prescribed until the selected acquisition mechanism is understood.

## 4. XDG filesystem and autostart conventions

The XDG Base Directory Specification provides standard locations for user configuration, data, cache and runtime files. Kali UX should honor the environment variables rather than hard-code home-directory paths.

Source: [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/).

The Desktop Application Autostart Specification defines how desktop sessions start applications from `.desktop` files in autostart directories. This is a reasonable initial option for a session-oriented graphical utility, subject to testing in XFCE.

Source: [Desktop Application Autostart Specification](https://specifications.freedesktop.org/autostart/latest/).

The Desktop Entry Specification defines application launch/menu metadata. Use valid desktop entries rather than ad-hoc startup scripts where possible.

Source: [Desktop Entry Specification](https://xdg.pages.freedesktop.org/xdg-specs/desktop-entry/latest-single/).

## 5. GTK and UI direction

GTK3 is selected initially because the existing SwipeSwitch project is built with GTK3/PyGObject. This minimizes migration work during the first audit and integration. It is not yet a decision that all future UI must use GTK3 forever.

Open questions:
- Whether the Control Center should share GTK3 or migrate later.
- Whether GTK4 offers a meaningful benefit for planned features.
- How to maintain theme integration and accessibility across Kali XFCE themes.

## 6. Existing SwipeSwitch research/context

An earlier SwipeSwitch specification described a Python/GTK3 application using libwnck, an input listener, state machine, tracker, overlay and activator. It included MRU ordering, current-workspace filtering, minimized-window handling, and a Windows 11-inspired dark translucent overlay.

Subsequent work expanded the agreed gesture contract to include four-finger workspace navigation, three-finger Show Desktop/restoration and three-finger Task View. The older v2.1 document explicitly excluded these actions; that exclusion is obsolete and must not be carried forward.

The supplied 0.3.0-alpha.2 archive was subsequently inspected. The six agreed gesture routes are represented in the live recognizer and controller, and automated tests now cover the gesture lifecycle. The event source is still `libinput debug-events`; no conclusion about production suitability or real touchpad behaviour is claimed until the target-machine proof of concept is complete.

## 7. Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Gesture ownership conflict | Two services can react to one gesture | Detect conflicts; ask before changing another service |
| Input permissions too broad | Touchpad feature could gain unnecessary access | Choose least-privilege mechanism; document exact access |
| Window manager differences | Requests may be ignored or behave differently | Keep xfwm4 authoritative; test each operation |
| Thumbnail cost | Capture can delay UI or use memory | Icons first; asynchronous bounded capture |
| State snapshot becomes stale | Restore can change unrelated window state | Reconcile snapshot with live window events |
| GTK thread misuse | UI hangs or crashes | Main-thread UI updates and worker dispatch |
| Feature sprawl | Suite becomes hard to maintain | Release a vertical slice; prioritize user value |
| Clipboard sensitivity | History can retain secrets | Explicit retention, exclusions, pause and clear policy |
| Compositor variability | Transparency and capture differ | Opaque fallback and compositor-on/off tests |

## 8. Open research questions

- What exact Kali release, XFCE, xfwm4, GTK and libwnck versions are on the target machine?
- What event lines does the target touchpad produce for all six gestures?
- Which gesture utility is currently installed and active?
- What is the least-privilege production input mechanism?
- Which EWMH/wnck operations reliably implement Show Desktop and restoration on xfwm4?
- Can Task View and switcher overlays reliably appear above fullscreen windows without stealing focus?
- What thumbnail API is available and performant?
- Which native xfwm4 snapping behaviours should Snap Assist complement?
- What packaging dependencies are available in Kali's repositories?

## 9. Reference list

- Kali Linux, Wayland: https://www.kali.org/docs/general-use/wayland/
- Kali Linux, Xfce FAQ: https://www.kali.org/docs/general-use/xfce-faq/
- libinput tools: https://wayland.freedesktop.org/libinput/doc/latest/tools.html
- EWMH: https://specifications.freedesktop.org/wm/latest-single/
- XDG Base Directory: https://specifications.freedesktop.org/basedir/latest/
- Desktop Autostart: https://specifications.freedesktop.org/autostart/latest/
- Desktop Entry: https://xdg.pages.freedesktop.org/xdg-specs/desktop-entry/latest-single/
