# Verification Report — Kali UX 0.3.0-alpha.6

**Source:** user-provided Kali UX archive, corrected and extended in the alpha.6 working tree  
**Verification environment:** Linux build container; no live Kali XFCE desktop or physical touchpad

## Automated verification

- Pytest: **88 passed, 0 skipped**.
- No tests were skipped. The tracker logic is unit-tested without importing GI; live libwnck behavior still requires the target desktop.
- Ruff lint: passed.
- Ruff format check: passed.
- Python bytecode compilation: passed.
- CLI version and status smoke tests: passed.
- Window-manager adapter, layout identity, gesture parser, action routing, conflict detection, launcher metadata, Focus Mode lifecycle, Window Peek capture logic, UI callback contracts and SwipeSwitch process supervision have automated unit coverage.

## Build verification

- Wheel: `kali_ux-0.3.0a6-py3-none-any.whl` (67,559 bytes).
- SHA-256: `07fbe30f7383b0abc6d71ff8365ea948ec78ebadba45c59d9348643f7129b174`.
- Installed into an isolated target directory with `pip --no-deps --target`; the installed CLI reported `kali-ux 0.3.0a6` and the installed `status` command returned valid JSON with 9 feature entries.

## Not verified in this environment

- GTK Control Center launch and visual rendering on XFCE.
- Actual libwnck integration with the user's window manager.
- Physical touchpad input and event permissions.
- Gesture coexistence with Touchégg/libinput-gestures/Fusuma/Gebaar.
- Multi-monitor, fractional scaling, panel work areas and fullscreen windows.
- Window capture behavior with obscured/protected/minimized windows.
- Focus Mode behavior against the target XFCE notification-daemon version.
- Clean Debian package install/upgrade/removal.

A passing unit suite does not constitute desktop acceptance. These items must be tested on the target Kali machine before calling this a fully verified daily-use release.
