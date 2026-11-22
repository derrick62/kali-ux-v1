# Changelog

All notable project changes are documented here.

## [0.1.0-audit] — 2026-11-18

### Changed
- Made the libinput parser accept swipe update events with an optional sequence number.
- Updated automatic touchpad detection for `pointer gesture` capability reports.
- Allowed the listener to filter multiple finger counts.
- Redirected unused libinput child stderr and strengthened listener shutdown.
- Applied threshold-crossing movement to the first visible switcher selection.
- Corrected the installed launcher to invoke the package as a module.
- Added the master product/architecture document, roadmap, audit and testing strategy.

### Verification
- Static source inspection completed. Automated and live desktop tests remain pending.


## 0.2.0 — Core feature preview

- Added a unified three-/four-finger gesture recognizer and central controller.
- Added four-finger virtual workspace navigation.
- Added Show Desktop snapshots and restoration of previously visible windows.
- Added a persistent, clickable Task View overview.
- Connected three-finger horizontal switching to the shared gesture pipeline.
- Added focused gesture-recognition unit tests.
- Updated project documentation and configuration for the core preview.
- Not yet verified on the target Kali/XFCE laptop.
