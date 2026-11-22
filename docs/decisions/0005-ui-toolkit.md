# ADR 0005 — GTK3 as the initial UI toolkit

- **Status:** Accepted for initial integration; long-term direction open
- **Date:** 2026-11-19

## Context
SwipeSwitch already uses GTK3/PyGObject, and the first target is XFCE.

## Decision
Use GTK3 for the initial integration and avoid an unnecessary migration during the audit. Re-evaluate GTK4 when there is a concrete benefit and migration plan.

## Consequences
- Reuse existing UI knowledge and components where appropriate.
- Keep domain logic independent of GTK.
- Do not assume every future module must use GTK3 indefinitely.
