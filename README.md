# Kali UX

**Kali UX** is a modular desktop-experience suite for Kali Linux. The initial target is XFCE on X11. It combines window navigation, snapping, productivity utilities and desktop controls while leaving `xfwm4` authoritative for window management.

> **Implementation status:** 0.3.0-alpha.6 integrated feature prototype. The feature modules and Control Center are implemented and automated-tested, but this archive has not been run on the user's live Kali desktop. Touchpad input, GTK rendering, real XFCE behavior, multi-monitor geometry and package lifecycle still require target-machine acceptance. See `docs/IMPLEMENTATION_STATUS.md` and `docs/VERIFICATION_REPORT.md`.

## Included features

| Feature | What works in this baseline | Runtime boundary |
|---|---|---|
| SwipeSwitch | Three-finger MRU switching, Task View, Show Desktop/restore, four-finger workspace navigation, configurable unaccelerated deltas, cancellation and timeout handling | X11, GTK3, libwnck, libinput tools and readable touchpad device; input listener remains an explicitly started `libinput debug-events` provider |
| Shared Gesture Infrastructure | One input-service owner, normalized event fan-out, action routing and read-only conflict detection | Other gesture daemons are reported, never disabled or reconfigured automatically; service starts only with SwipeSwitch |
| Task View / Window Overview | GTK3 window grid, keyboard selection, live-XID activation and icon fallback | Uses libwnck; optional previews require GdkX11 and the Window Peek feature enabled |
| Window Peek | On-demand local X11 snapshots, aspect-preserving scaling and lazy capture | Obscured, minimized, protected or destroyed windows fall back to application icons; previews are not persisted |
| Snap Assist | Eight half/quarter-screen presets using monitor work-area geometry | Requests geometry through the shared `wmctrl` adapter; `xfwm4` remains in control |
| Clipboard History | Opt-in GTK clipboard monitoring, bounded session history, deduplication, search, copy-back and clear | Memory-only; no persistence, sensitive-app detection or automatic secret classification |
| Quick Panel | Opens display, sound, network, power and keyboard settings applications | Missing optional applications are disabled with an explanation |
| Focus Tools | Timed do-not-disturb sessions with restoration on timeout or normal application exit | Requires `xfconf-query` and `xfce4-notifyd-config`; abrupt session/process termination still needs manual validation |
| Application Launcher | XDG desktop-entry discovery, metadata/category search, icons, keyboard activation, refresh and `gio launch` | Respects desktop-entry visibility and `TryExec` constraints; no Wayland-specific backend |
| Layout Memory | Named geometry/workspace snapshots, identity checks, restore and delete | Stores no window titles; restore is best-effort and skips stale/reused XIDs |
| Control Center | Theme-aware GTK3 dashboard with page builders separated from application orchestration | Feature preferences are distinct from runtime availability and do not silently start daemons |
| Diagnostics | Platform capability report and gesture-provider process/autostart scan | Read-only; does not change system settings or input permissions |

## Platform contract

- Initial support target: Kali Linux, XFCE, X11.
- `xfwm4` remains the window manager and owns focus, stacking and final geometry decisions.
- X11 window operations are isolated behind `platform/window_manager.py` and use `wmctrl` requests.
- GTK UI work stays on the GTK main thread; gesture input is read by one explicit listener and delivered through GLib.
- No automatic changes to XFCE settings, input permissions, other gesture services or system files.
- No GUI process should run as root.
- Wayland and other desktop environments are not supported by this baseline.

## Install and run

Install GTK/PyGObject/libwnck from Kali packages, then install the Python project in a user-owned virtual environment. Use `--system-site-packages` so the venv can see distribution-provided GI bindings. Do not use `sudo pip`.

See [`docs/INSTALL.md`](docs/INSTALL.md) for exact dependencies and commands.

```bash
kali-ux init
kali-ux gui
```

Enable the desired feature modules in the Control Center. Clipboard monitoring remains separately opt-in. Start SwipeSwitch explicitly when you want gestures. The Control Center's Gestures page provides a managed Start/Stop button; a process started there is stopped when the Control Center closes. Its log is stored under `$XDG_DATA_HOME/kali-ux/logs/swipeswitch.log`:

```bash
kali-ux swipeswitch --check
kali-ux swipeswitch
```

The check command verifies the X11/GTK environment and touchpad device readability. The listener does not modify device permissions. Important: `libinput debug-events` is a debugging helper, not a stable production API, and often requires direct input-device access. SwipeSwitch only works when your normal user already has that access; Kali UX will not elevate itself or change permissions. Do not run the GUI as root.

## Configuration and data

- Kali UX config: `$XDG_CONFIG_HOME/kali-ux/config.json` (default `~/.config/kali-ux/config.json`)
- Kali UX data: `$XDG_DATA_HOME/kali-ux` (default `~/.local/share/kali-ux`)
- Cache: `$XDG_CACHE_HOME/kali-ux` (default `~/.cache/kali-ux`)
- SwipeSwitch config: `$XDG_CONFIG_HOME/swipeswitch/config.toml` (default `~/.config/swipeswitch/config.toml`)

Clipboard contents remain in memory only. Layout snapshots are written only after an explicit capture request, with owner-only file permissions, and omit window titles.

## Project map

```text
src/kali_ux/
  core/                  configuration, paths and feature registry
  platform/              capability, command, GTK and shared window adapters
  features/               independently bounded feature services
  control_center/         feature preference and availability model
  diagnostics/            read-only health and conflict reporting
  ui/                     application orchestration and separated page builders
    pages/

tests/                    unit and component tests
docs/                     product, architecture, research and operational guides
packaging/                desktop-entry template and packaging notes
scripts/                  developer verification helpers
```

## Development and verification

```bash
python -m pip install -e '.[dev]'
./scripts/check.sh
```

The current build-container report is **88 passed, 0 skipped**. Automated checks do not replace manual acceptance on Kali XFCE/X11. See `docs/TESTING.md` for the target desktop matrix.

The package is still an alpha source/wheel release. A Debian package, signed APT repository, autostart entry and systemd user unit are intentionally not shipped until their lifecycle and user-consent behavior can be tested on the target release.
