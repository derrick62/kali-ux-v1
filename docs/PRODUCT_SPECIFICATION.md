# Kali UX — Product Specification

**Document status:** Baseline v1.1  
**Date:** 2026-11-21  
**Authority:** Product scope and user-visible behaviour. Architecture explains how; implementation status explains what exists.

## 1. Vision

Kali UX aims to provide a coherent collection of small desktop interactions that make Kali Linux feel more polished and efficient for everyday use. It draws inspiration from useful Windows experiences without attempting to reproduce Windows wholesale or override Linux desktop conventions.

The suite should feel like one thoughtfully designed product rather than unrelated scripts. Its features should be useful individually and become more coherent through shared configuration, visual language, diagnostics and carefully coordinated platform integration.

## 2. Problem and opportunity

Many desktop conveniences are distributed across window-manager settings, panel plugins, shortcuts, external gesture tools and individual applications. This can make discovery and configuration fragmented. Kali UX explores whether a focused, modular suite can bring selected interactions together while continuing to rely on the desktop environment for the work it already performs well.

The opportunity is not to replace XFCE. It is to add carefully scoped interaction layers where a clear user benefit exists.

## 3. Initial user and environment

The initial user is a Kali Linux desktop user who wants more fluid window and workspace navigation, especially on a laptop with a touchpad.

The first supported development target is Kali Linux running XFCE, `xfwm4` and X11. The precise installed versions, hardware capabilities, compositor state and input configuration must be detected or documented during testing rather than assumed from the distribution name alone.

## 4. Product goals

- Make common desktop actions quicker and easier to discover.
- Preserve user control over features and system changes.
- Reuse native XFCE/X11 capabilities where practical.
- Provide consistent interaction and visual behaviour across suite features.
- Keep the system responsive, stable, auditable and maintainable.
- Make installation, configuration, diagnostics and removal predictable.

## 5. Non-goals for the initial release

- Replacing XFCE, `xfwm4`, the compositor, panel or session manager.
- Supporting every desktop environment or Wayland compositor at launch.
- Shipping a large collection of unrelated system-tweaking scripts.
- Requiring root for normal graphical operation.
- Silently rewriting the user's touchpad configuration or disabling existing gesture services.
- Collecting telemetry or transmitting user activity.
- Promising Windows feature parity.
- Building a general-purpose plugin marketplace or microservice platform.

## 6. Initial platform contract

| Concern | Initial decision |
|---|---|
| OS | Kali Linux |
| Desktop | XFCE |
| Window manager | `xfwm4` |
| Display protocol | X11 |
| Language | Python 3 |
| GUI | GTK 3 / PyGObject initially |
| Window/workspace access | X11/EWMH; evaluate libwnck |
| Runtime | User session, unprivileged |
| Configuration | XDG-compliant user configuration |
| Distribution | Debian package as the eventual primary native package |

GTK3 is a pragmatic starting point because the existing SwipeSwitch application uses it. This is not a permanent commitment to GTK3 for every future feature.

## 7. Feature scope

The suite's planned feature families are:

- Window navigation: SwipeSwitch and window overview.
- Window arrangement: Snap Assist and layout memory.
- Input coordination: shared gesture routing and shortcuts.
- Productivity: clipboard history and focus tools.
- Access: application launcher and quick panel.
- Administration: Control Center, configuration and diagnostics.

Detailed requirements and statuses are maintained in [FEATURES.md](FEATURES.md).

## 8. SwipeSwitch product requirements

SwipeSwitch is an existing project and is the first candidate for integration. The current agreed gesture contract is:

| Gesture | Required behaviour |
|---|---|
| Three fingers left | Next window |
| Three fingers right | Previous window |
| Three fingers down | Show Desktop |
| Three fingers up with a valid Show Desktop snapshot | Restore the previously visible windows |
| Three fingers up without a valid snapshot | Open Task View |
| Four fingers left | Next workspace |
| Four fingers right | Previous workspace |

The direction labels above are the agreed product mapping. Their implementation must be checked against actual event coordinate conventions and the user's touchpad before release.

### Window switcher behaviour

- Use most-recently-used ordering by default.
- Default scope is the current workspace plus sticky windows.
- Include eligible minimized windows in the switcher.
- Exclude desktop windows, panels, docks, splash windows, skip-taskbar windows and the switcher's own overlay.
- A continuous horizontal gesture may reveal an overlay, move selection and activate the selected window on gesture completion.
- A quick flick may select the next/previous window without requiring the full overlay, if the implementation supports it and testing validates the interaction.
- Restore/unminimize a selected minimized window before activation.
- Handle windows closing or changing workspace during an interaction.

### Show Desktop and restoration

Show Desktop must preserve a snapshot of the windows that were visible before the action. Windows already minimized before Show Desktop must remain minimized after restoration. Restoration should affect only windows that still exist and should not unexpectedly change windows opened after the snapshot. Repeated down gestures must not overwrite a valid snapshot. The snapshot must be invalidated or reconciled safely when state changes make restoration unreliable.

The implementation must document whether it uses minimization, EWMH desktop-showing state, or another mechanism. The correct mechanism is an implementation decision to validate against XFCE/xfwm4; the observable behaviour above is the requirement.

### Task View

Task View is a distinct overview, not simply the horizontal switcher enlarged. It should show eligible open windows, allow pointer selection, activate the selected window, and dismiss predictably (Escape and clicking outside are proposed baseline interactions). It must work with a single eligible window. Three-finger up opens Task View only when there is no valid restoration snapshot.

### Workspace navigation

Four-finger horizontal gestures navigate XFCE workspaces. Initial behaviour should respect workspace boundaries without wrapping unless later user testing establishes a different preference. Sticky windows remain available across workspaces according to normal desktop semantics.

### Gesture ownership and conflicts

The suite must have one clear ownership/arbitration policy for gestures it handles. Existing services such as `libinput-gestures` or Touchégg may already own gestures. The installer must detect potential conflicts and explain them. It must never silently edit or disable another service. A shared gesture dispatcher is an architectural direction for the suite, but the exact event source and permissions remain subject to a technical proof of concept.

## 9. Other feature requirements

### Snap Assist
Offer discoverable layouts and assist with arranging windows. Prefer native `xfwm4` behaviour and standards-compliant requests. Do not assume the window manager will accept every geometry request. Custom preview/assist UI must not fight the window manager.

### Clipboard History
Provide a bounded, searchable history with clear/pause/exclusion controls. Respect X11 `CLIPBOARD` and `PRIMARY` semantics. Do not log clipboard contents. Sensitive-content handling, persistence defaults and maximum retention must be explicit before implementation.

### Quick Panel
Provide a small, focused access surface for selected controls. Reuse XFCE settings and services where they already provide the required capability. Avoid becoming a duplicate settings manager.

### Focus Tools
Offer optional focus-oriented utilities with reversible settings and clear state. Do not change notifications, network access or application behaviour without explicit user configuration.

### Application Launcher
Improve application discovery and launching while respecting desktop entries, application IDs and existing application-menu conventions.

### Window Peek and Layout Memory
Preview windows and optionally remember arrangements. Window geometry and workspace restoration must be treated as best-effort because applications, monitors and desktop layouts can change.

### Control Center and Diagnostics
Provide one place to inspect feature state, adjust supported settings, see compatibility information and collect safe diagnostics. Diagnostics must redact sensitive data and never include raw clipboard contents or raw input streams by default.

## 10. Quality attributes

- **Reliability:** features fail safely and do not strand the desktop in a broken state.
- **Responsiveness:** overlays appear promptly and do not block the GTK main loop.
- **Resource discipline:** idle CPU and memory usage remain low; expensive work is bounded.
- **Compatibility:** supported versions and limitations are explicit.
- **Security:** least privilege, no unnecessary root execution, no network access unless a future feature explicitly requires it and documents why.
- **Privacy:** no telemetry by default; sensitive local data is minimized and user-controllable.
- **Accessibility:** keyboard operation, visible focus, readable contrast and reduced-motion options.
- **Maintainability:** clear module boundaries, tests, documentation and traceable decisions.

## 11. Success measures

Early success is not the number of features. It is a dependable foundation and one well-integrated, well-tested desktop workflow. Measures should include successful clean installation/removal, no persistent desktop regressions, predictable gesture ownership, reliable restoration, acceptable interaction latency and clear diagnostics. Numerical performance budgets should be established from measurement on the target hardware rather than invented in advance.

## 12. Release scope

The alpha.6 development scope is an integrated implementation pass across all agreed feature families: SwipeSwitch/window navigation, Task View, Snap Assist, Window Peek, Clipboard History, Quick Panel, Focus Tools, Application Launcher, Layout Memory, Control Center and diagnostics. This is an implementation-scope decision, not a claim that every module is production-ready. Each module remains a prototype until target Kali XFCE/X11 acceptance, privacy review, failure handling and packaging checks pass. The eventual stable-release scope may be narrowed based on that evidence, but the development baseline should contain the complete agreed feature set so the suite can be polished and tested as one coherent system.

## 13. Change control

Changes to this specification require:
- Updating its version/date.
- Recording the rationale in an ADR or change log.
- Identifying affected features, architecture and tests.
- Distinguishing a changed requirement from a change in implementation.
- Preserving the evidence behind decisions where useful.
