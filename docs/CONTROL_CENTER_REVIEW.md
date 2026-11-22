> **Historical review:** This document describes the alpha.4 Control Center foundation. It is retained as design history; the current implementation and status are documented in `docs/IMPLEMENTATION_STATUS.md`, `docs/ARCHITECTURE.md` and `docs/REVIEW_REPORT.md` for alpha.6.

# Control Center foundation review — 0.3.0-alpha.4

## Scope

This increment establishes the management contract between the GTK3 interface,
feature registry, user configuration and read-only platform capability checks.
It does not attempt to finish every feature page or claim live desktop acceptance.

## Architecture

- `core.registry` remains the static catalogue of bundled features. It is not a
  third-party plugin loader.
- `platform.capabilities.detect()` reports the current session and available
  executables/GTK introspection namespaces. It does not change the desktop.
- `control_center.model.ControlCenterModel` combines registry metadata,
  capability results and user preferences into feature rows. It is the UI-facing
  owner of feature preference updates.
- `core.config.save_config()` writes settings to a same-directory temporary
  file, applies mode `0600`, flushes the file and atomically replaces the target.
- `ui.app.KaliUXWindow` presents those rows through a GTK `Stack` and
  `StackSidebar`. Feature-specific controls are sensitive only when the feature
  is both enabled and available.
- `diagnostics.report.build_report()` exposes platform capabilities and feature
  state without collecting clipboard contents, window titles or other user data.

## State model

The interface deliberately separates:

- **Implementation maturity**: `integrated`, `foundation`, `prototype`, `planned`.
- **Availability**: whether the implementation exists and its declared runtime
  requirements are detected.
- **Enabled preference**: the user's saved setting.

An enabled preference is not a claim that a service is running. Enabling a
feature does not launch a process, start a daemon, change input permissions,
modify `xfwm4`, or alter system settings. Planned and unavailable features cannot
be enabled; an already-enabled feature can always be disabled.

## Known limitations

- The GTK interface has not been launched in a live desktop session in the build
  environment. Validate the sidebar, scrolling, focus, keyboard navigation,
  scaling and display sizing on the target Kali XFCE/X11 machine.
- Some capabilities are intentionally conservative. A detected executable
  means the dependency is present, not that its service is running or correctly
  configured.
- Gesture-provider detection only reports known provider executables. It does
  not claim exclusive input ownership or prove that a provider is active.
- Appearance currently documents the built-in dark styling; a theme editor is
  not implemented.
- The UI remains concentrated in `ui/app.py`. Page/component extraction is a
  follow-up after the current model and navigation behaviour are accepted.

## Verification

The alpha.4 build-container suite reports 46 passed and one skipped. The skipped
libwnck tracker test requires the target system's PyGObject/libwnck integration.
Python bytecode compilation and wheel construction succeeded. Ruff was not
available in the build environment. These checks do not replace live desktop
acceptance.
