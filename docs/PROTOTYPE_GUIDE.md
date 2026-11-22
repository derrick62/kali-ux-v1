# Kali UX integrated feature guide — 0.3.0-alpha.6

This baseline contains a broad integrated implementation of the agreed feature set. All feature modules are still labelled prototypes because live XFCE/X11 acceptance has not been completed.

## Control Center

Launch with `kali-ux gui`. The Control Center separates application orchestration from page builders under `src/kali_ux/ui/pages/`. Its Features page distinguishes implementation maturity, runtime availability and the user's enabled preference. Enabling a preference does not silently start a service or change system settings.

The dashboard follows the active GTK theme. Task View and the SwipeSwitch overlay use a deliberately dark, focused presentation.

## Window navigation

SwipeSwitch runs explicitly with `kali-ux swipeswitch` or the managed Start/Stop control on the Gestures page. A Control Center-managed instance is supervised and stopped when the Control Center exits. It supports three-finger horizontal MRU switching, three-finger up for Task View (or restoration after Show Desktop), three-finger down for Show Desktop, and four-finger horizontal workspace navigation. Gesture cancellation, reversal and inactivity timeout are handled by the recognizer.

The overlay uses lazy X11 previews when Window Peek is enabled and configured. Task View supports keyboard selection and Escape dismissal. A preview failure falls back to the application icon. Activation resolves the selected XID against live windows before acting.

## Snap Assist and Layout Memory

Snap Assist provides left/right/top/bottom and four quarter-screen presets. Geometry is calculated from the active monitor work area and sent through the shared X11 window-manager adapter. `xfwm4` remains authoritative.

Layout Memory saves named geometry/workspace snapshots only after an explicit capture. It stores no window titles, checks XID/PID/WM_CLASS before restore, and supports restore and delete. Monitor topology changes and unusual windows remain best-effort.

## Productivity

- **Clipboard:** turn capture on explicitly. History is bounded and session-only; search, copy-back and clear are available. Pause before copying secrets.
- **Quick Panel:** launches existing XFCE settings tools. Missing optional applications are disabled.
- **Focus Tools:** choose a duration and start a timed notification do-not-disturb session. It restores on timeout or normal Control Center exit.
- **Application Launcher:** search by app name, comment or category; icons and launch are based on XDG desktop entries and Gio. Press Enter to launch the first match or activate a selected row.

## Gesture conflict management

Open Gestures → Scan for gesture conflicts. The report checks known processes and desktop autostart entries. It is advisory only; no other gesture handler is stopped or reconfigured.

Before starting SwipeSwitch, run `kali-ux swipeswitch --check`. If device access is denied, review the local input permissions rather than running the GUI as root or allowing Kali UX to modify them.

## Known limits

- The listener still uses `libinput debug-events` and requires live input-provider validation.
- Only XFCE/X11 is targeted; Wayland is not supported.
- Clipboard persistence and sensitive-app detection are not included.
- Quick Panel delegates to existing applications; it is not a custom system-settings shell.
- Window previews may be incomplete for obscured/off-screen windows.
- No `.deb`, APT repository, autostart entry or systemd user service is shipped.
- Multi-monitor, scaling, fullscreen, focus and session lifecycle behavior require manual acceptance on Kali.
