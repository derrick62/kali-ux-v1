# Kali UX — Feature inventory (0.3.0-alpha.6)

| Feature | Implemented behavior | Dependencies and known limits |
|---|---|---|
| SwipeSwitch | 3-finger horizontal MRU switching; 3-finger up Task View; 3-finger down Show Desktop; 4-finger horizontal workspace movement; cancellation, reversal, timeout and configurable unaccelerated deltas. Control Center Start/Stop supervises its child process and private log | GTK3, libwnck, X11, libinput-tools and readable touchpad device. The provider uses `libinput debug-events`; real device coexistence and permission behavior still need live validation |
| Gesture infrastructure | Single input listener service with normalized event subscribers, one-handler action routing and conflict inspection | Shared implementation, not a separately toggled feature; SwipeSwitch currently owns the active gesture subscription. No competing service is automatically stopped |
| Task View | Window grid, keyboard navigation, Escape dismissal, live-XID activation and icon fallback | Requires X11/GTK3/libwnck. Focus and keyboard behavior require manual XFCE testing |
| Window Peek | Aspect-preserving GDK foreign-window snapshots, lazy one-per-idle capture | Requires GdkX11; obscured/unmapped/minimized/protected windows may not yield full previews. Nothing is stored |
| Snap Assist | Eight half/quarter presets calculated against the active monitor work area | Uses shared X11 window manager adapter and `wmctrl`; `xfwm4` can constrain final geometry |
| Clipboard History | Opt-in clipboard-owner watcher, bounded in-memory text history, deduplication, search, copy-back and clear | Session-only; no persistence or reliable password-manager/sensitive-field detection |
| Quick Panel | Display, sound, network, power and keyboard settings launchers | Each external settings application is checked and unavailable buttons are disabled |
| Focus Tools | Timed notification do-not-disturb sessions; restores previous xfconf value or removes a property created by Kali UX | Requires `xfconf-query` and `xfce4-notifyd-config`. Abrupt power loss or process kill cannot guarantee restoration |
| Application Launcher | XDG desktop-entry scan, Hidden/NoDisplay/TryExec/OnlyShowIn/NotShowIn handling, search by name/comment/category, icon and launch via Gio | Desktop-entry localization and full launch UX are future refinements |
| Layout Memory | Named window geometry and workspace snapshots, PID/WM_CLASS/XID validation, restore and delete | Does not persist titles; window identity can still change between capture and restore; monitor topology changes are best-effort |
| Control Center | GTK3 pages separated into modules; feature preference, implementation maturity and capability state shown separately; theme-aware CSS | Enabling a preference does not start a service; disabling Window Switcher stops the SwipeSwitch child managed by the Control Center |
| Diagnostics | X11/GTK/tool capability checks and read-only process/autostart scan for known gesture tools | No automatic remediation and no collection of clipboard text or raw input |

## Feature-state vocabulary

- **Prototype:** implementation exists and automated/component tests cover its non-desktop logic, but it has not completed all target-desktop acceptance.
- **Available:** required platform capabilities were detected.
- **Unavailable:** one or more required capabilities are missing.
- **Enabled:** user preference is enabled. This does not imply that a background process is running.

No feature is labelled production-ready in this baseline.
