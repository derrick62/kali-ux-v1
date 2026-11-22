# ADR 0004 — Central gesture ownership and arbitration

- **Status:** Accepted architectural requirement; implementation open
- **Date:** 2026-11-19

## Context
SwipeSwitch and future features may use the same touchpad gestures. Existing tools may already listen for or execute gestures.

## Decision
The suite needs one explicit ownership/arbitration policy for gestures it handles. The production input source and permission model must be selected only after a target-machine proof of concept. Do not silently disable or edit other gesture tools.

## Consequences
- Input acquisition, normalization, recognition, routing and action are separate responsibilities.
- Existing tools must be detected and conflicts explained.
- `libinput debug-events` is a diagnostic aid, not automatically the production API.
