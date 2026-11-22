# Kali UX — Development Guide

## Development approach

The project now has an integrated implementation of the agreed feature set. The next work is not to add another broad feature catalogue; it is to validate and refine the system as a coherent desktop experience.

For each change:
- Identify the user-visible behavior and acceptance criteria.
- Trace the responsible feature, shared service and platform adapter.
- Keep GTK presentation separate from feature logic.
- Prefer the shared X11 window adapter for wmctrl operations.
- Preserve `xfwm4` as the window manager.
- Add automated tests for logic and failure cases.
- Run the full check script.
- Perform target-desktop testing for GTK, X11, input and window behavior.
- Update documentation, status and changelog.

## Prerequisites

- Python 3.10 or newer.
- GTK3/PyGObject/libwnck system bindings.
- X11 utilities such as `wmctrl`.
- `libinput-tools` for SwipeSwitch input.
- `pytest` and `ruff` for development.

Install GI bindings through APT and create the virtual environment with `--system-site-packages`. Do not use `sudo pip` or modify Kali's system Python.

## Setup

```bash
git clone https://github.com/derrick62/kali-ux.git
cd kali-ux
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## Useful commands

```bash
./scripts/check.sh
python -m kali_ux --version
kali-ux status
kali-ux features
kali-ux gui
kali-ux swipeswitch --check
kali-ux swipeswitch --debug
```

## Repository conventions

- Use the `src/` layout.
- Keep tests under `tests/`, mirroring package responsibilities.
- Keep GTK widgets in UI/page modules and service behavior in feature modules.
- Keep platform-specific behavior behind `platform/` adapters.
- Use dependency injection for command runners and desktop backends where it improves tests.
- Avoid circular imports, global mutable state and feature-to-feature private imports.
- Use argument arrays, bounded subprocess timeouts and explicit child-process shutdown.
- Keep logs and diagnostics privacy-safe.

## Git workflow

Use focused branches and commits. Do not force-push or replace public history as part of baseline corrections. Before committing, run tests/lint/format checks, inspect the diff, ensure no local paths/secrets/generated artifacts are included, and update docs/changelog.

## Desktop safety

- Test in a normal user XFCE/X11 session.
- Do not run GTK as root.
- Do not change device permissions or stop another gesture daemon automatically.
- Back up configuration before user-approved manual changes.
- Verify recovery behavior after Focus Mode and Show Desktop operations.
- Do not assume `libinput debug-events` is a stable long-term application API.

## Current next task

Run the alpha.6 build on the target Kali machine. First install dependencies, run `kali-ux swipeswitch --check`, inspect gesture conflicts, then validate gestures and overlays. Continue with multi-monitor snapping, Task View, clipboard ownership, Focus Mode restoration, launcher and layout restore. Record the OS/session details and any failures in the verification report before daily-use acceptance.
