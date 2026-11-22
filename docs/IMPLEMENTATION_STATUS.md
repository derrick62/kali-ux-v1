# Implementation status — integrated feature prototype

**Release:** 0.3.0-alpha.6  
**Target:** Kali Linux / XFCE / X11  
**Verification environment:** Linux build container; not a live Kali desktop

## What is implemented

- GTK3 Control Center with separated page builders, theme-aware styling, feature preferences, runtime capability reporting and explicit shutdown handling. SwipeSwitch launched from the Control Center is supervised, has Start/Stop state and writes a private user-data log.
- SwipeSwitch integrated engine based on the current public SwipeSwitch implementation: normalized libinput event parsing, optional unaccelerated deltas, three-finger window switching and vertical actions, incremental four-finger workspace navigation, cancellation, reversal, timeout, MRU window tracking, Show Desktop snapshot/restore and Task View.
- Shared `GestureInputService` owns one input listener and fans out normalized events. `GestureActionRouter` maps recognized actions to one controller handler. Gesture conflict inspection is read-only. This is shared infrastructure, not a separately toggled feature.
- Task View includes keyboard selection, live-XID activation, lazy previews and icon fallback.
- Window Peek uses GdkX11 foreign-window capture on demand; it does not store screenshots.
- Shared `X11WindowManager` adapter backs Snap Assist and Layout Memory.
- Snap Assist exposes eight geometry presets using the active monitor work area supplied by the GTK layer.
- Clipboard History is opt-in, bounded, deduplicated, searchable, copyable and session-only.
- Quick Panel launches existing XFCE settings applications and disables missing optional actions.
- Focus Tools supports timed DND sessions, restoring the previous value or removing a property it created on normal completion/shutdown.
- Application Launcher scans XDG desktop-entry paths, handles visibility/TryExec filters, searches metadata/categories, refreshes and launches with Gio.
- Layout Memory stores named window geometry/workspace snapshots, omits titles, validates XID/PID/WM_CLASS identity, restores geometry and deletes snapshots.
- Diagnostics reports platform capabilities and known gesture processes/autostart entries without modifying the system.

## Runtime requirements and limitations

| Capability | Required components | Limitation |
|---|---|---|
| SwipeSwitch | X11, GTK3, libwnck, libinput-tools, readable touchpad event device | `libinput debug-events` remains a diagnostic-command provider; target-device ownership/coexistence must be validated |
| Task View | X11, GTK3, libwnck | Live focus/dismissal behavior requires manual testing |
| Window Peek | GdkX11 GTK typelib and X11 | Obscured/minimized/protected windows may fall back to icons |
| Snap Assist / Layout Memory | X11 and wmctrl | Window-manager constraints and monitor/workspace changes are best-effort |
| Clipboard History | GTK clipboard | Memory-only; no sensitive-app classification or persistence |
| Quick Panel | XFCE and individual settings applications | Optional apps may be absent |
| Focus Tools | xfconf-query and `xfce4-notifyd-config` | Abrupt process kill/power loss cannot guarantee restore |
| Launcher | Gio and XDG desktop entries | Some desktop-entry features/localization remain unimplemented |

## Feature maturity

All registry entries are labelled **prototype**. That is intentional. Code and automated tests exist, but the features have not completed live XFCE/X11 acceptance. The Control Center reports implementation maturity, availability and user preference separately. An enabled preference does not imply a service is running.

## Verification

The current build-container verification records:

- **88 passed, 0 skipped** in pytest.
- The Wnck tracker logic is unit-tested without importing GI; live libwnck behavior still requires the target desktop.
- Ruff lint: passed.
- Ruff formatting check: passed.
- Python compilation: passed.
- CLI version/status smoke tests: passed.
- Wheel build and isolated installation: passed; artifact hash is recorded in `docs/VERIFICATION_REPORT.md`.

## Not claimed complete

No live touchpad gesture test, real XFCE overlay test, multi-monitor acceptance, accessibility review, clean Debian install/upgrade/removal test or Wayland support has been completed in this environment. No `.deb` or APT repository is shipped.
