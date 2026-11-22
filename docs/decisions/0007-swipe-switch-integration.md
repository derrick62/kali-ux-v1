# ADR 0007 — SwipeSwitch integration is audit-first

- **Status:** Accepted
- **Date:** 2026-11-19

## Context
SwipeSwitch is an existing standalone repository with prior specifications and implementation work. Its recent scope expanded beyond the original live horizontal switcher.

## Decision
Audit the actual repository and current archive before deciding whether to embed, extract, adapt or keep it separately packaged. Preserve its standalone identity unless a reasoned decision changes that.

The current six-gesture product contract is maintained in `PRODUCT_SPECIFICATION.md`. Older documentation that excludes four-finger workspace navigation or three-finger up/down is superseded.

## Consequences
- No blind rewrite or copy.
- Run the existing test suite before changing code.
- Record Keep / Improve / Replace / Missing findings with evidence.
- Trace every agreed gesture to implementation and tests.
