> **Historical note:** The audit below records the alpha.3 cleanup and is retained as implementation history. The current integrated source is alpha.6; see `src/kali_ux/features/window_switcher/README.md`, `docs/IMPLEMENTATION_STATUS.md` and `docs/VERIFICATION_REPORT.md` for current behavior and remaining acceptance work.

# SwipeSwitch — Technical Audit and Core Preview Status

**Audit basis:** initial source archive and integrated core-preview source, inspected 18 November 2026.
**Execution status:** static inspection only; the application and test suite were not executed as part of this audit.

## Keep

- `state.py`: pure state-machine logic is a useful testable boundary.
- `tracker.py`: libwnck-based window discovery and MRU tracking are a suitable starting point.
- `activator.py`: focused activation helper with a fallback is worth retaining.
- `overlay.py`: GTK overlay provides a functional starting presentation.
- `config.py`: TOML configuration is appropriate, although its schema is still prototype-level.
- Existing tests: preserve and expand them.

## Improve

- `listener.py`: support the observed optional sequence number in update events; detect `pointer gesture` devices; accept one or multiple finger counts at the listener boundary; avoid an unread stderr pipe; make process shutdown more deterministic. The application now configures both three- and four-finger input streams.
- `state.py`: apply the movement that first crosses the overlay threshold to selection.
- `tracker.py`: strengthen eligibility checks and handling of windows that disappear or change state.
- `activator.py`: verify activation outcomes and preserve safe fallback behaviour.
- `overlay.py`: evolve into distinct switcher and Task View presentation components.
- `config.py`: migrate to feature-specific configuration sections with clear validation and migration behaviour.
- Installer: launch the package as a module rather than executing `__main__.py` directly.

## Restructure

`__main__.py` currently owns startup, callbacks, feature coordination, config reload and shutdown. Feature coordination has moved into `controller.py`, with dedicated gesture, desktop, workspace and Task View modules. Further separation and error recovery remain candidates for refinement.

## Missing

- Asynchronous thumbnail capture.
- Structured logging/diagnostics and broader integration tests.
- Complete project documentation and release workflow.

## Corrections included in this audit update

- Parser accepts swipe update lines with and without an optional sequence number.
- Automatic device detection recognises `pointer gesture` capability and prefers a device whose name includes `touchpad`.
- Listener accepts one or multiple finger counts, redirects unused child stderr, and has more deterministic process shutdown.
- Initial threshold-crossing movement contributes to the selected index.
- Installer launcher invokes `python3 -m swipeswitch` with the installed package on `PYTHONPATH`.
- Regression tests were added for the event format variations and threshold-crossing selection.

## Core-preview implementation update

The 0.2.0 core preview adds `gestures.py`, `controller.py`, `workspaces.py`, `desktop.py` and `task_view.py`. MRU tracking now reads the newly active Wnck window rather than treating the signal argument (the previously active window) as the new one. The application now routes three-finger horizontal gestures to the switcher, three-finger vertical gestures to Task View or Show Desktop/restoration, and four-finger horizontal gestures to workspace navigation. A timeout path cancels unfinished gestures rather than committing them.

## Outstanding verification

No automated test result is claimed. Run the documented test suite in the target development environment, then perform a live X11/Kali/XFCE check. Verify device auto-detection against the actual `libinput list-devices` output and verify permissions without running SwipeSwitch as root.


## Follow-up source remediation — 19 November 2026

The integrated Kali UX archive was reviewed and modified after the preliminary audit. This is a source-level engineering pass, not live desktop verification.

- Removed the unused `GestureStateMachine` implementation and its stale tests; moved the shared immutable `GestureEvent` contract into `events.py`.
- Fixed the reversal acceptance expectation to reflect cumulative movement: reversing from one leftward step to one net rightward step crosses two step boundaries.
- Added immediate switcher cancellation when finger count changes or a new BEGIN interrupts an active sequence.
- Added tests for reversal, interrupted begins, finger-count changes and timeout cancellation.
- Fixed blocking GUI process launches, focus-mode state recovery, snap request sequencing and layout snapshot privacy/atomicity.
- Current automated result after the alpha.3 cleanup: 41 passed, 1 skipped, 0 expected failures. Ruff was unavailable in the review container, so lint and formatting are not claimed here.

The remaining skipped tracker test and all GTK/libwnck/input/xfwm4 behaviour still require a real Kali XFCE/X11 session. `libinput debug-events` remains a proof-of-concept input source, not a production-approved provider.


## Alpha.3 startup correction

GTK namespace loading is now shared through `kali_ux.platform.gtk.load_gtk3()`. It explicitly requests GTK 3, GDK 3, libwnck 3 and Pango 1.0 before importing namespaces, preventing the unversioned GDK import from selecting GDK 4 in a GTK3 process.
