# Changelog

All notable project changes are recorded here. This file begins with the foundation scaffold; it does not imply that the planned features are implemented.

## [0.1.0] - 2026-11-19

### Added
- Initial Kali UX product and engineering foundation.
- Product specification, roadmap, architecture, feature inventory and design principles.
- Testing, development, research, security/privacy and packaging guidance.
- Initial Python package, CLI version command and smoke test.
- Architecture Decision Records for project scope, modular architecture, platform baseline, gesture arbitration, UI toolkit and packaging direction.

### Status
- No desktop enhancement feature is claimed as complete by this scaffold.
- SwipeSwitch integration remains subject to the dedicated audit.

## 0.3.0-alpha.1 — Interactive prototype

- Added GTK3 Control Center with Overview, Windows, Clipboard, Applications, Productivity and Settings pages.
- Added user-triggered window activation, Task View, eight snap presets, session-only clipboard capture/search/copy/clear, application search/launch, XFCE settings shortcuts, focus-mode controls and named layout snapshots.
- Added `kali-ux gui` / `kali-ux-gui` launch commands and a desktop-entry template.
- Preserved the original SwipeSwitch documentation under `docs/swipeswitch/`.
- Added installation and prototype-operation guides.
- Explicitly retained the known SwipeSwitch acceptance failures and platform validation requirements.


## 0.3.0-alpha.2 — Engineering remediation

- Consolidated live gesture events into `events.py` and removed the unused legacy state machine.
- Corrected reversal semantics and added cancellation for finger-count changes and interrupted gesture begins.
- Added detached process launching for graphical applications so Control Center actions do not block or time out their child apps.
- Hardened focus-mode restoration and layout snapshot validation, privacy and atomic writes.
- Improved active-monitor work-area selection for Snap Assist.
- Reformatted the Python codebase, resolved Ruff lint findings and expanded service/gesture tests.
- Updated implementation, verification and development documentation to match the current source.


## 0.3.0-alpha.3 — Baseline review corrections

- Centralized GTK namespace loading and explicitly pinned GDK 3 alongside GTK 3, libwnck 3 and Pango 1.0 to prevent accidental GTK4/GDK4 selection.
- Removed the unused legacy gesture state machine and its stale expected-failure tests; the live recognizer is the only gesture lifecycle implementation.
- Added a regression test for the GTK namespace selection order.
- Corrected release documentation and verification counts to match the source and actual test run.
- Updated package metadata to use the SPDX `MIT` license identifier and a current setuptools build requirement.
- Kept desktop integration limitations explicit; no live touchpad, compositor, multi-monitor or Debian package lifecycle acceptance is claimed.


## 0.3.0-alpha.4 — Control Center foundation

- Connected the GTK Control Center to `ControlCenterModel` for feature preference management.
- Added capability-aware feature availability, separating implementation maturity, availability and enabled preference.
- Prevented enabling planned or unavailable features while always allowing users to disable a saved preference.
- Added atomic, owner-only configuration writes and strict boolean validation for feature enabled settings.
- Replaced notebook tabs with GTK stack/sidebar navigation and added Features, Appearance, Gestures, Privacy, Diagnostics and About sections.
- Gated feature controls using saved preferences and runtime availability; toggles do not start services or change system settings.
- Added model/configuration regression tests and updated the development roadmap to put Control Center before SwipeSwitch integration.

## 0.3.0-alpha.6 — Integrated feature realignment

- Reorganized Control Center page composition into focused `ui/pages/` modules and replaced the hardcoded dark dashboard palette with GTK theme-aware styling.
- Added a shared `X11WindowManager` adapter used by Snap Assist and Layout Memory; layout restore now checks XID, PID and WM_CLASS before applying geometry and restores workspace when possible.
- Added a single-owner `GestureInputService`, event fan-out, a single-handler `GestureActionRouter`, read-only detection of competing gesture processes/autostart entries and an explicit device-readability check.
- Added a supervised SwipeSwitch process lifecycle to the Control Center, including Start/Stop, graceful termination, normal-exit cleanup, runtime preference reload and a private user-data log.
- Aligned the integrated SwipeSwitch listener with the current public implementation: optional unaccelerated libinput deltas, live-XID activation, incremental four-finger workspace navigation, short-flick handling and config reload updates.
- Added lazy X11 window thumbnails to the switcher overlay and Task View, monitor-under-pointer placement, horizontal scrolling, keyboard Task View selection and icon fallback.
- Added timed Focus Mode with restoration of the previous xfconf value or removal of a property created by Kali UX; normal application shutdown attempts cleanup.
- Improved the launcher with XDG data-directory handling, desktop-entry visibility/TryExec filters, icon/comment/category metadata, keyboard activation and refresh.
- Added Quick Panel availability checks, Layout Memory snapshot deletion and identity-aware restore.
- Expanded tests for gesture lifecycle/provider behavior, launcher metadata, window previews, shared window-manager requests and layout identity.
- Updated architecture, feature inventory, implementation status, installation, testing, security/privacy, roadmap and verification documentation.
- Automated verification: 88 passed, 0 skipped; Ruff lint and formatting checks passed in the build container.

### Remaining acceptance

The libinput diagnostic listener, real touchpad permissions/coexistence, GTK/XFCE rendering, window-manager geometry, multi-monitor behavior and package lifecycle still require tests on the target Kali desktop. No `.deb`, APT repository, autostart or systemd unit is included.
