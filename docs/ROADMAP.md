# Kali UX — Development Roadmap

**Current baseline:** 0.3.0-alpha.6  
**Product direction:** a cohesive desktop experience for Kali XFCE/X11, not a Control Center full of unrelated utilities.

## Product principles

- Integrate with XFCE and `xfwm4`; do not replace the window manager.
- Share platform services and keep feature responsibilities separate.
- Make gestures, shortcuts and overlays predictable, cancellable and keyboard-accessible.
- Respect user configuration, XDG paths, privacy and system ownership.
- Implement the agreed feature set as a coherent system, then polish the interactions together.
- Never call a feature production-ready until its target-desktop acceptance criteria pass.

## Phase A — Product and architecture foundation

**Status: established.** Product scope, initial platform, design principles, module boundaries, privacy rules, testing strategy and architecture decisions are documented.

## Phase B — Integrated feature implementation

**Status: broad implementation present in alpha.6; live integration remains open.**

The initial suite now contains working code paths for:

- SwipeSwitch and Task View.
- Gesture input ownership, action routing and conflict reporting.
- Window Peek previews.
- Snap Assist.
- Clipboard History.
- Quick Panel.
- Focus Tools.
- Application Launcher.
- Layout Memory.
- Control Center and diagnostics.

The goal of this phase was to give every agreed module a real service boundary and a usable interface rather than leaving placeholder folders or mock-only screens. The alpha.6 implementation is the first integrated feature pass, not a claim of production acceptance.

## Phase C — Target-desktop integration and stabilization

This is the next critical phase. Validate the entire system on Kali XFCE/X11:

- Confirm `libinput debug-events` device access, event stream, cancellation and coexistence with existing gesture handlers.
- Test three- and four-finger gestures on the physical touchpad, including reversals, quick sequences and timeouts.
- Validate overlay monitor placement, focus, keyboard dismissal, previews, minimized windows and fullscreen behavior.
- Validate `xfwm4` snapping, panels/work areas, window constraints and multi-monitor arrangements.
- Validate Focus Mode property creation/restoration and behavior across logout/restart.
- Validate clipboard owner changes, copy-back, pause/clear and interactions with a system clipboard manager.
- Validate launcher desktop-entry behavior and missing application states.
- Validate layout restore with windows moved, closed, restarted or moved between workspaces.
- Exercise feature enable/disable, Control Center shutdown and session logout.

Exit criteria: no stuck overlays or orphaned listener; no unintended changes to input permissions or other services; safe fallbacks for unsupported windows; clear user-facing errors; all critical desktop workflows pass manual acceptance.

## Phase D — Visual and interaction polish

Polish the integrated experience rather than each module in isolation:

- Align spacing, typography, icons, surface hierarchy, borders, shadows and motion.
- Improve monitor-aware sizing and density for small/large displays.
- Add reduced-motion behavior and verify keyboard/focus paths.
- Refine snapping suggestions, Task View card behavior and Quick Panel affordances.
- Review GTK theme integration and light/dark appearance on Kali themes.
- Profile responsiveness, thumbnail capture and resource use with many windows.

## Phase E — Engineering hardening

- Add X11 integration tests in a controlled XFCE session.
- Test malformed configuration, interrupted commands, process/device disconnect and partial failures.
- Review input listener supervision and decide whether a dedicated supported input API is preferable to `libinput debug-events`.
- Review clipboard privacy policy and optional persistence only if there is a justified use case.
- Review logging and diagnostic redaction.
- Establish a support matrix and stable feature lifecycle contract.

## Phase F — Packaging and public release

- Complete Debian packaging metadata.
- Test clean install, upgrade, reinstall, removal and interrupted package operations.
- Preserve user configuration and avoid enabling autostart or input ownership without explicit opt-in.
- Publish source and verified artifacts with checksums and release notes.
- Consider a signed APT repository after package lifecycle tests are stable.

## Phase G — Compatibility expansion

Investigate other X11 desktops and Wayland through separate platform adapters. Wayland is not an extension of the current X11 implementation; it requires compositor-specific window and input APIs.

## Definition of done

A feature is complete only when its specification, implementation, automated tests, target-desktop tests, failure handling, documentation and packaging impact have been reviewed. Alpha.6 has a broad implementation, but Phase C acceptance is still outstanding.
