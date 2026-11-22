# Kali UX baseline realignment report

**Reviewed source:** user-provided `kali-ux(4).zip`  
**Reference implementation:** current public `derrick62/swipeswitch` `main` branch  
**Updated baseline:** 0.3.0-alpha.6  
**Review date:** 21 November 2026

## Executive assessment

The project remains aligned with the intended product: a cohesive desktop enhancement suite for Kali XFCE/X11, not a Control Center full of unrelated utilities. The existing modular Python package, GTK3 UI, feature registry, XDG configuration and standalone SwipeSwitch documentation were retained.

The alpha.6 pass completes a broad feature implementation and corrects several architectural gaps. It is still an engineering prototype because live input, GTK and XFCE behavior have not been tested on the target machine.

## Main corrections

- Separated Control Center page construction into `ui/pages/` modules and made the dashboard follow the active GTK theme.
- Added a shared `X11WindowManager` adapter for Snap Assist and Layout Memory.
- Strengthened Layout Memory with PID/WM_CLASS/XID identity checks, workspace restore and deletion; snapshots omit titles.
- Added a single-owner `GestureInputService`, event fan-out, action router, conflict inspection and explicit device-readability checks.
- Aligned the integrated SwipeSwitch parser/recognizer/controller with the current public implementation: optional unaccelerated deltas, incremental four-finger workspace movement, short-flick handling, live-XID activation and runtime configuration updates.
- Added lazy GdkX11 previews to the switcher overlay and Task View, monitor-under-pointer placement, horizontal scrolling and keyboard Task View navigation.
- Added timed Focus Mode with normal-exit restoration and cleanup of a property created by Kali UX.
- Improved XDG launcher discovery and metadata, Quick Panel missing-application behavior and Layout Memory lifecycle.
- Expanded tests and reconciled current documentation.

## Preserved architecture

- `xfwm4` remains authoritative.
- The app remains a modular Python/GTK3 user-session application, not microservices.
- User configuration/data remain under XDG paths.
- Clipboard history remains opt-in and memory-only.
- No automatic input permission changes, competing gesture-service shutdown, root GUI, autostart or systemd service is introduced.

## Verification

- Pytest: 88 passed, 0 skipped.
- Ruff lint and formatting: passed.
- Python compilation and CLI smoke tests: passed.
- The skipped test requires system PyGObject/libwnck bindings.
- No physical touchpad, live GTK, multi-monitor, xfwm4 or Debian package lifecycle test was possible in the build container.

See `docs/VERIFICATION_REPORT.md` for exact results and `docs/IMPLEMENTATION_STATUS.md` for the implemented/unverified boundary.

## Next step

Use alpha.6 as the integrated source baseline for target-machine acceptance. Do not expand the feature catalogue further until the gesture provider, window backend, Task View and feature lifecycles have passed real Kali XFCE/X11 testing. Then polish the entire experience as one coherent system.
