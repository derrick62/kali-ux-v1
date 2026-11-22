> **Historical preliminary audit:** this report predates the alpha.2 remediation. See `docs/swipeswitch/AUDIT.md` for the follow-up source review and current test result.

# SwipeSwitch — Preliminary Audit Report

**Audit date:** 2026-11-19
**Source inspected:** `swipeswitch-v0.2.0-core-preview.zip` from the project's prior conversation Library
**Source version:** 0.2.0 core preview
**Audit status:** Preliminary source inspection; live Kali/XFCE verification not performed.

> This report describes the inspected archive only. It does not claim that the archive is identical to the current GitHub repository or the user's current working tree.

## 1. Executive assessment

The 0.2.0 archive is a meaningful functional preview rather than only the original horizontal switcher. It contains code for all six agreed gesture behaviours: three-finger left/right window switching, three-finger down Show Desktop, three-finger up restoration or Task View depending on snapshot state, and four-finger left/right workspace navigation.

The architecture has begun separating gesture recognition, desktop actions, window tracking and GTK presentation. This is a sound direction. However, the preview is not release-ready. Its own README labels desktop acceptance testing outstanding, and this audit reproduced automated-test issues in the available environment.

The most important structural concern is that `gestures.py` is the recognizer used by the live application while `state.py` contains a second, older gesture state machine whose tests are still present. This creates two competing representations of gesture behaviour and is likely a source of confusion and stale tests.

## 2. Source inventory

The archive contains:

- `listener.py` — touchpad discovery, `libinput debug-events` subprocess and event parsing.
- `gestures.py` — gesture lifecycle classification and action generation.
- `controller.py` — routes recognized actions to switcher, Task View, desktop and workspace services.
- `state.py` — older GTK-independent window-switcher state machine.
- `tracker.py` — libwnck window filtering and MRU tracking.
- `activator.py` — window activation with `wmctrl` fallback.
- `desktop.py` — Show Desktop snapshot and restoration.
- `workspaces.py` — workspace navigation.
- `overlay.py` — GTK3 horizontal switcher.
- `task_view.py` — GTK3 window overview.
- `thumbs.py` — placeholder returning no thumbnail.
- `config.py` — TOML configuration.
- `__main__.py` — startup, CLI, GTK/libwnck setup and shutdown.
- `install.sh`, `uninstall.sh`, desktop/autostart and systemd templates.
- Unit tests for parser, gestures, state and tracker.

## 3. Requirement traceability

| Requirement | Source location | Preliminary status |
|---|---|---|
| Three-finger left/right switch | `gestures.py`, `controller.py`, `overlay.py`, `tracker.py` | Implemented in source; not live-verified |
| Three-finger down Show Desktop | `gestures.py`, `controller.py`, `desktop.py` | Implemented in source; not live-verified |
| Three-finger up restore when snapshot exists | `controller.py`, `desktop.py` | Implemented in source; restoration edge cases need tests |
| Three-finger up Task View without snapshot | `controller.py`, `task_view.py` | Implemented in source; single-window path appears supported |
| Four-finger left/right workspace navigation | `gestures.py`, `controller.py`, `workspaces.py` | Implemented in source; not live-verified |
| MRU and current-workspace/sticky filtering | `tracker.py` | Implemented in source; GTK/libwnck tests blocked here |
| Task View selection and Escape dismissal | `task_view.py` | Implemented in source; focus/dismissal needs live validation |
| Thumbnails | `thumbs.py` | Not implemented; placeholder only |
| Multi-monitor-aware overlay | `overlay.py` | Primary monitor only |
| Shared suite-wide gesture router | `controller.py` is app-local | Partial precursor; not a reusable Kali UX service |
| Configuration and startup | `config.py`, `__main__.py`, scripts | Implemented in preview; hardening required |

## 4. Automated test execution

The archive was extracted and tested in the current inspection runtime.

### Full test collection

Command:

```bash
python -m pytest -q
```

Result: collection stopped because `tests/test_tracker.py` imports `swipeswitch.tracker`, which imports `gi.repository.Wnck` at module import time. The current inspection runtime does not have PyGObject (`gi`) installed:

```text
ModuleNotFoundError: No module named 'gi'
```

This is an environment/dependency limitation, not proof that tracker tests fail on Kali. It does reveal that a test of the tracker currently requires GTK/libwnck bindings even though its test cases use fake window objects.

### GTK-independent subset

Command:

```bash
python -m pytest -q tests/test_parser.py tests/test_gestures.py tests/test_state.py
```

Result: **19 passed, 3 failed**.

Failures:

- `test_horizontal_reversal_changes_selection_direction` expects one rightward step after a -50 then +100 delta with a 40-pixel step. The recognizer uses cumulative signed displacement and emits two rightward corrections after having already emitted one leftward step. That may be correct for net cursor-like selection, but the test expectation and intended UX semantics need to be reconciled. Do not change the algorithm or test without deciding what reversal should feel like.
- `test_live_scrub_and_release` uses the legacy `GestureStateMachine` in `state.py`. With the current default `show_threshold_px=35`, a -30 update should not show the overlay, but the test expects it to. The expectation appears stale or the test setup is incomplete.
- `test_timeout_resets` also uses the legacy state machine. Because the -30 update does not cross the 35-pixel threshold, the overlay was never visible, so expecting `hide_overlay=True` is inconsistent with the configured threshold.

The live application imports and uses `GestureRecognizer` from `gestures.py`; it does not use `GestureStateMachine` from `state.py`. This reinforces the need to consolidate the duplicate state logic and align tests with the live execution path.

## 5. Component findings

### Listener and parser — Improve

Positive:
- Parser accepts an optional sequence number in swipe update headers.
- Device detection looks for `pointer` plus `gesture` capabilities and prefers a device whose name contains `touchpad`.
- The subprocess is restricted to one selected device.
- The listener filters configured finger counts, redirects unused stderr and has a restart/backoff path.
- Worker-thread callbacks are marshalled to the GLib main context by the application entry point.

Risks and follow-up:
- Production behaviour depends on parsing the human-readable output of `libinput debug-events`. The libinput documentation presents this as a diagnostic tool. Validate stability across the target Kali/libinput versions and compare with a more appropriate event API before treating it as a durable production contract.
- Device selection can be ambiguous when multiple gesture-capable pointer devices exist. A warning is not the same as user-confirmed selection.
- Reading `/dev/input/eventX` may require broad `input` group membership. The README acknowledges the security trade-off, but the eventual permission design should be revisited rather than assuming group membership is always the right answer.
- The listener currently treats permission errors by logging and exiting the listener loop. Surface this state to diagnostics/UI so the application cannot appear healthy while gestures are inactive.
- Capture real event fixtures from the target device. The existing fixture is described as illustrative, not as a verified capture.
- Exercise child process shutdown, EOF, repeated restart, device unplug/replug and a blocked `readline()` during shutdown.

### Gesture recognizer — Improve

Positive:
- Recognition is separate from GTK and desktop operations.
- It distinguishes three- and four-finger gestures.
- It classifies horizontal/vertical intent using a threshold and dominance ratio.
- It routes vertical three-finger gestures to Show Desktop or Task View and horizontal four-finger gestures to workspace navigation.
- Cancellation and timeout paths avoid committing a switch.

Risks and follow-up:
- Reversal semantics are unresolved because the test and cumulative-displacement implementation disagree.
- Confirm whether the first threshold-crossing update should immediately move selection and whether that movement is perceptually consistent.
- Define what happens when the finger count changes mid-gesture and whether the input stream emits a clean END for the original gesture.
- Add tests for multiple update chunks, diagonal-to-axis dominance, near-threshold movement, cancellation after a visible overlay and timeouts for all gesture classes.
- Make the product mapping and coordinate sign convention explicit in docs and validate it on hardware.

### Controller and duplicate state — Improve / restructure

`controller.py` is the live action coordinator and is a reasonable first separation from `__main__.py`. However, `state.py` remains a second, older state machine with tests that do not match the live recognizer. Choose one source of truth. Prefer keeping pure recognition in `gestures.py` and removing or deliberately reworking the unused state machine after confirming no other imports depend on it.

The controller directly coordinates multiple services and UI objects. This is acceptable for the current small preview, but integration into Kali UX should occur behind a documented feature interface rather than importing private classes across projects.

### Window tracker — Keep, then improve

Positive:
- Uses libwnck and tracks MRU ordering separately from stacking order.
- Reads the newly active window from the screen in the active-window-changed callback.
- Filters window type, workspace, skip-tasklist and SwipeSwitch's own windows.
- Includes minimized windows and sticky windows.

Risks and follow-up:
- `gi.repository.Wnck` is imported at module import time, making otherwise fake-based unit tests require PyGObject. Consider moving the dependency to the platform adapter boundary or using a small protocol/interface.
- Test window close, workspace move, sticky state, active-window transitions, skip-tasklist, dialogs and duplicate XIDs.
- Confirm whether window titles beginning with `swipeswitch` are a robust way to exclude both overlays; a stronger internal identifier/property may be preferable.
- Verify the semantics of Wnck workspace `None` on the target version.

### Show Desktop and restoration — Improve; manual validation essential

Positive:
- Captures XIDs for currently visible eligible windows.
- Does not overwrite an existing snapshot on repeated down gestures.
- Skips windows already minimized.
- Restores only windows that still exist.
- Clears the snapshot after restoration.

Risks and follow-up:
- The implementation minimizes eligible windows individually rather than using the window manager's native show-desktop state. Validate whether this matches XFCE expectations, panel behaviour and user-visible semantics.
- Define what should happen if a user manually changes window state, opens new windows or switches workspace while the snapshot is active.
- Verify focus restoration when the previously active window closes or changes workspace.
- Ensure partial minimize failures do not leave a misleading snapshot that cannot be restored accurately.
- Add fake-window tests for all restoration cases before relying on live testing.

### Task View — Improve; manual validation essential

Positive:
- Separate GTK window from the horizontal switcher.
- Displays icons and titles in a clickable grid.
- Supports Escape and attempts click-outside dismissal.
- Controller appears to permit a one-window overview, satisfying the single-window requirement in source.

Risks and follow-up:
- `focus-out-event` hides the overview. Verify that pointer interaction with a card is not pre-empted by focus loss and that clicking outside behaves as intended.
- Add keyboard navigation between cards; currently Escape is the only explicit keyboard behaviour in the inspected code.
- Test focus restoration after dismissal and activation.
- Test one window, many windows, minimized windows, sticky windows, long titles and fullscreen applications.

### Switcher overlay — Improve

Positive:
- Pre-created GTK3 overlay, undecorated and configured to avoid accepting focus.
- Includes dark/light CSS and a non-composited opaque fallback.
- Centers on the primary monitor.

Risks and follow-up:
- Cards are packed into a horizontal box without an evident scroll container; many windows may overflow the available width.
- The `auto` theme setting currently falls back to dark in the inspected code.
- The overlay is primary-monitor-only.
- No thumbnails are implemented; `thumbs.py` is a stub.
- Verify stacking above fullscreen windows, compositor off, multiple displays and scaling.

### Workspace manager — Keep, verify

Positive:
- Uses libwnck workspaces.
- Non-wrapping navigation is the default.
- Implements the agreed left=next/right=previous mapping.

Follow-up:
- Verify mapping against XFCE workspace ordering and the actual touchpad coordinate convention.
- Test boundaries, one workspace, dynamic workspace changes and rapid gestures.
- Review timestamp handling and activation failures.

### Configuration and entry point — Improve

Positive:
- TOML configuration, XDG config home support and restrictive config-file mode.
- `--debug`, `--config` and `--check` options.
- SIGHUP reload path.
- Runtime dependencies are intended to come from the distribution.

Risks and follow-up:
- `--check` currently detects a touchpad and imports GTK/libwnck before it can report success; diagnostic checks should be broken into independent capability checks.
- Configuration validation is basic; validate types and cross-field constraints explicitly.
- `theme="auto"` is not implemented as theme detection.
- Several fields appear to be unused or only partially implemented (`flick_min_px`, `invert_direction`, `use_unaccelerated`, `thumbnails`, `thumb_budget_ms`).
- Consider the runtime requirement for TOML parsing: Python 3.11 includes `tomllib`, while the project declares Python 3.10+ and currently requires `tomli` fallback without declaring it.
- Review signal handling and shutdown when the listener is blocked or GTK is exiting.

### Packaging scripts — Improve before public release

Positive:
- User-level application files and launcher.
- User configuration is preserved by uninstall.
- Desktop autostart is installed in the user's config directory.
- No systemd service is enabled by default.

Risks and follow-up:
- Installer performs `apt-get update` and installs system dependencies with sudo; explain this clearly and make the privileged portion as small as possible.
- Installer overwrites the existing autostart `.desktop` file without backup or conflict handling.
- It creates a user launcher and copies source directly rather than installing a versioned Debian package.
- `systemd` service template is present but unused; avoid confusing users about which startup mechanism is active.
- Uninstaller removes the application and autostart file without confirmation; ensure it does not remove unrelated user edits.
- Test paths containing spaces, missing PATH entries and interrupted installation.
- Do not add automatic edits to `libinput-gestures` or other tools.

## 6. Preliminary classification

| Component | Classification | Reason |
|---|---|---|
| `gestures.py` | Keep / Improve | Good pure boundary; reversal and lifecycle semantics need clarification |
| `controller.py` | Keep / Improve | Useful coordinator; integration interface needed |
| `listener.py` | Improve | Good parser/device separation; production event source and permissions unresolved |
| `tracker.py` | Keep / Improve | Suitable libwnck basis; import coupling and edge cases |
| `activator.py` | Keep / Improve | Simple activation boundary; verify timestamp and fallback behaviour |
| `desktop.py` | Improve | Snapshot approach is right; partial failures and external state changes |
| `workspaces.py` | Keep / Verify | Clear service; validate direction and boundaries on XFCE |
| `task_view.py` | Improve | Functional starting UI; focus, keyboard and scaling |
| `overlay.py` | Improve | Useful base; overflow, monitor and theme behaviour |
| `state.py` | Replace or remove after dependency check | Duplicate/unused state machine with stale tests |
| `thumbs.py` | Missing | Stub only |
| `config.py` | Improve | Basic schema; unused settings and Python 3.10 TOML fallback |
| `__main__.py` | Improve | Startup responsibilities and `--check` coupling |
| installer/uninstaller | Improve | Prototype user-level install; backup/rollback and package work |

## 7. Recommended next engineering sequence

1. Confirm whether this archive is the same source as the user's current working tree and remote repository.
2. Run the tests on the actual Kali/XFCE development machine with PyGObject/libwnck installed.
3. Resolve the three pure-test failures deliberately; do not simply weaken assertions.
4. Remove or consolidate the duplicate `state.py` path and its stale tests.
5. Add deterministic tests for desktop snapshot/restoration and controller routing.
6. Add tests for Task View one-window, focus and dismissal behaviour.
7. Capture real touchpad event fixtures and verify parser behaviour on the target libinput version.
8. Conduct live manual testing of all six gestures, workspace boundaries, fullscreen overlays and cancellation.
9. Only then define the Kali UX integration adapter and decide whether SwipeSwitch remains standalone.

## 8. Remote repository limitation

The supplied GitHub URL, `https://github.com/derrick62/swipeswitch`, returned a 404 when opened during this audit attempt. This may mean the repository is private, moved, renamed or the URL is not currently accessible. The archive inspected above is available from the prior conversation and is sufficient for this preliminary source audit, but it cannot establish the current remote HEAD or whether later commits exist.

## 9. Audit conclusion

The 0.2.0 preview has a promising modular direction and source-level implementations for the agreed core gestures. It is not yet verified on the target desktop. The immediate priority is to consolidate the recognizer/state-machine path, repair or correct the failing tests, make GTK/libwnck test dependencies explicit, and validate the six behaviours on real XFCE/X11 hardware. Do not begin the larger feature expansion until these foundations are stable.
