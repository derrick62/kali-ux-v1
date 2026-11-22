# ADR 0001 — Project scope and initial platform

- **Status:** Accepted
- **Date:** 2026-11-19

## Context
Kali UX is intended to bring selected desktop productivity interactions into a cohesive suite. Linux desktop environments and display protocols expose different capabilities.

## Decision
Start with Kali Linux + XFCE + xfwm4 + X11. Treat Wayland and other desktop environments as future compatibility work. Keep the window manager authoritative.

## Consequences
- Initial development and tests can target a concrete environment.
- Runtime capability checks and explicit unsupported states are required.
- No broad compatibility claims are made.
