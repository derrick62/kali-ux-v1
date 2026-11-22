# ADR 0003 — Platform integration through XFCE/X11 adapters

- **Status:** Accepted direction; API details open
- **Date:** 2026-11-19

## Context
Window placement, focus, stacking and workspaces are already managed by xfwm4. A second window manager would create conflicts.

## Decision
Treat xfwm4 as authoritative. Use established X11/EWMH interactions and evaluate libwnck for window/workspace discovery and operations. Verify each required operation on the target system.

## Consequences
- Kali UX requests actions; it does not own window placement.
- Requests can fail or be constrained by the window manager.
- Platform-specific code remains behind adapters.
