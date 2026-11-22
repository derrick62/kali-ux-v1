# ADR 0008 — Shared X11 window-management adapter

**Status:** Accepted for the XFCE/X11 baseline  
**Date:** 2026-11-21

## Context

Snap Assist and Layout Memory both issued `wmctrl` commands independently. That duplicated command construction and made it harder to apply common validation and window identity rules.

## Decision

Introduce `platform/window_manager.py` with `WindowGeometry` and `X11WindowManager`. Snap Assist delegates active-window geometry requests to it. Layout Memory uses it to enumerate windows, validate XID/PID/WM_CLASS identity, move a window to its saved workspace and restore geometry.

`xfwm4` remains authoritative. The adapter sends requests and reports whether the command was accepted; it does not maintain a competing window-manager state model.

## Consequences

- Window-management commands have one shared testable boundary.
- Layout restore can skip stale/reused XIDs rather than blindly applying geometry.
- The implementation remains X11-specific and must be replaced or extended for other backends.
