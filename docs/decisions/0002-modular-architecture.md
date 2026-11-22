# ADR 0002 — Modular monolith for the initial application

- **Status:** Accepted
- **Date:** 2026-11-19

## Context
The product contains multiple related desktop features, but early development does not justify distributed services or a complex plugin framework.

## Decision
Use one Python application with a small shared core, feature modules, GTK UI and platform adapters. Add process boundaries only when a concrete reliability, permission or lifecycle requirement justifies them.

## Consequences
- Easier development and distribution initially.
- Module interfaces and failure isolation still matter.
- Avoid premature event buses, dynamic plugin loading and service proliferation.
