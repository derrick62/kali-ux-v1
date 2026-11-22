# ADR 0006 — Python and Debian packaging direction

- **Status:** Accepted direction; package split open
- **Date:** 2026-11-19

## Context
The target is Kali Linux, a Debian-based distribution, and native libraries such as GTK/PyGObject are best managed through distribution packages.

## Decision
Use `pyproject.toml` and a `src/` layout for the Python project. Keep dependencies minimal and use Debian packages for system libraries. Target `.deb` packaging before establishing an APT repository.

## Consequences
- No `sudo pip` installation.
- Runtime and development dependencies remain separate.
- Package lifecycle and user configuration preservation require explicit tests.
- Whether SwipeSwitch ships separately remains open.
