# Kali UX — Architecture Specification

**Baseline:** 0.3.0-alpha.6 integrated feature prototype  
**Initial platform:** Kali Linux / XFCE / X11  
**Window manager:** `xfwm4` remains authoritative

## Architectural approach

Kali UX is a modular desktop enhancement suite implemented as a user-session Python application. It is not a set of unrelated utilities, a microservices system or a replacement window manager. Shared capabilities are implemented once and exposed through narrow interfaces; features own their own use cases and presentation.

The Control Center is the management surface. It does not own feature logic or directly implement every feature.

## Runtime layers

```text
GTK3 Control Center / overlays
             |
       UI page builders
             |
    Feature services/controllers
             |
   Shared core + action contracts
             |
Platform adapters (X11 / GTK / Gio / xfconf / libinput)
             |
       XFCE / xfwm4 / X11
```

### UI orchestration and pages

`ui/app.py` owns application startup, shared service instances, navigation, callbacks and shutdown. Page construction is separated under `ui/pages/` by responsibility. GTK widgets are created and mutated on the GTK main thread. Long-running or blocking operations must not block that thread; input callbacks are delivered through GLib.

### Feature modules

Features own user-visible behavior: SwipeSwitch, Task View, Snap Assist, Clipboard History, Quick Panel, Focus Tools, Application Launcher, Window Peek and Layout Memory. A feature must not reach into another feature's private implementation when a shared service or platform adapter exists.

### Shared core

- Configuration discovery, validation and atomic persistence.
- XDG paths and user-level data boundaries.
- Static feature registry and capability-aware preferences.
- Logging and read-only diagnostics.
- Explicit lifecycle and shutdown handling.

Feature preference, implementation maturity, runtime availability and actual process state are distinct concepts. Enabling a preference does not silently start a daemon or take ownership of an input device. SwipeSwitch starts only through an explicit command/button; disabling its feature stops only the child process managed by the Control Center.

## Shared platform adapters

### Window manager

`platform/window_manager.py` defines `X11WindowManager` and `WindowGeometry`. Snap Assist and Layout Memory use this shared adapter for `wmctrl` operations and window identity enumeration. The adapter sends requests; it does not claim to own window geometry. `xfwm4` remains authoritative and may constrain or reject a request.

`libwnck` remains the discovery and activation interface used by SwipeSwitch and Task View. Window activation resolves selected XIDs against the current live window list before attempting activation. `wmctrl` is a fallback/request tool, not a competing window manager.

### Gesture input and action routing

```text
Touchpad device
      |
libinput debug-events listener (explicit start)
      |
Normalized GestureEvent
      |
GestureInputService (one listener owner, event fan-out)
      |
SwipeSwitch GestureRecognizer
      |
GestureActionRouter (one handler per recognized action)
      |
SwipeSwitchController
      |
Window / workspace / desktop service + GTK overlay
```

The current provider uses the existing public SwipeSwitch listener implementation based on `libinput debug-events`. Libinput documents this as a debugging helper whose output may change and which usually requires direct access to `/dev/input/event*` (often root access). It is tested against fixtures, but remains the primary integration risk because it is not a dedicated application event API. Access to the selected device is checked before startup. Kali UX never elevates itself or changes group membership/device permissions automatically.

Other known gesture handlers are detected through process and autostart inspection. Detection is advisory only; no other service is stopped or rewritten. The current raw-event subscriber is SwipeSwitch. The action router prevents duplicate ownership within the integrated controller; additional feature gesture mappings should be added only through explicit registrations.

### Window previews

`features/window_switcher/engine/thumbs.py` uses GdkX11 foreign-window support and `Gdk.pixbuf_get_from_window` to obtain best-effort local snapshots. Previews are captured lazily, one per GLib idle tick. A failed capture falls back to the application's icon. Previews are not persisted. Obscured/off-screen portions may be absent, and minimized/protected windows may not be capturable.

### Clipboard

Clipboard History watches the X11 `CLIPBOARD` selection through GTK and stores bounded text entries in memory only. It does not persist clipboard contents. `PRIMARY` selection is not treated as the copy/paste clipboard. Sensitive-field detection is not claimed; users should pause capture before copying secrets.

### Desktop settings and application launch

Quick Panel delegates to existing XFCE tools. Focus Tools uses `xfconf-query` and tracks the prior value or whether Kali UX created the DND property. The Application Launcher reads XDG desktop-entry directories and launches through `gio`; it does not execute the desktop-file `Exec` string itself.

## Package map

```text
src/kali_ux/
  core/                       config, paths, feature registry
  platform/                   capabilities, commands, GTK, window_manager
  control_center/             preference/availability model
  diagnostics/                 read-only report and conflict information
  ui/
    app.py                     application orchestration and lifecycle
    pages/                     separated page builders
  features/
    gesture_control/            shared input service, action router, conflicts
    window_switcher/engine/     integrated SwipeSwitch engine
    window_peek/                X11 preview capability
    snap_assist/                preset geometry policy
    clipboard_history/          bounded in-memory clipboard model
    quick_panel/                XFCE settings action adapters
    focus_tools/                reversible timed DND helper
    launcher/                   XDG desktop-entry discovery/launch
    layout_memory/              named geometry/workspace snapshots
    window_overview/            Task View feature boundary
```

## Threading and lifecycle

- GTK operations run on the GTK main thread.
- Gesture input is read by one listener worker/subprocess.
- Normalized events cross to the GTK loop with `GLib.idle_add`.
- Listener shutdown is explicit on SIGINT/SIGTERM and normal GTK exit.
- SwipeSwitch started by the Control Center is managed by a feature-level process supervisor, polled through GLib, stopped on user request, and terminated during normal Control Center shutdown.
- Timed Focus Mode is restored on timeout or normal Control Center shutdown.
- No process is automatically installed as a daemon or autostart item.

## Configuration and filesystem

Follow XDG Base Directory conventions. Kali UX config and persistent data are stored in user-owned paths with owner-only permissions for files containing user-specific state. SwipeSwitch keeps its compatible TOML configuration under `$XDG_CONFIG_HOME/swipeswitch/`.

Clipboard payloads are not written to disk or logs. Layout snapshots omit titles and are only written after an explicit user action.

## Known architectural limits

- The gesture provider still relies on `libinput debug-events`; the correct long-term input API/ownership strategy remains open.
- The shared event service currently has SwipeSwitch as its only active consumer.
- Window operations are X11-specific; Wayland requires compositor-specific APIs.
- GTK3 is retained for XFCE compatibility; GTK4 migration is not part of this baseline.
- No Debian package, signed APT repository, systemd unit or autostart installer is included.
- Multi-monitor and live XFCE behavior require manual acceptance on the target machine.
