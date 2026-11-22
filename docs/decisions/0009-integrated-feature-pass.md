# ADR 0009 — Integrated feature implementation pass

**Status:** Accepted for alpha.6  
**Date:** 2026-11-21

## Context

The project had a growing feature catalogue but inconsistent service boundaries and UI composition. The product direction is a cohesive desktop experience rather than a dashboard containing unrelated utilities. The user requested an integrated pass across all agreed feature modules before the next polish phase.

## Decision

Implement or complete the feature service paths in one integrated alpha pass while retaining explicit module boundaries. Separate Control Center page builders, centralize X11 window operations, establish one gesture input owner and action router, and complete the planned service behavior for Window Peek, launcher metadata, Focus Mode sessions and Layout Memory identity checks.

All features remain labelled `prototype` until target Kali XFCE/X11 acceptance passes. Feature preferences do not silently start background services or modify system settings.

## Consequences

- The suite has a broad, coherent implementation to test and polish.
- Automated tests cover more feature logic and shared adapters.
- The alpha is not a claim of live desktop acceptance; physical input, GTK rendering, multi-monitor behavior and packaging remain external validation tasks.
