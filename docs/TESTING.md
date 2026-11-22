# Kali UX — Testing Strategy

## 1. Purpose

Desktop software crosses several boundaries: Python logic, GTK, X11, window-manager behaviour, input devices, session lifecycle and packaging. A passing unit test is necessary but cannot prove that an overlay behaves correctly on a real XFCE session.

Testing is layered so that failures can be localized and claims remain honest.

## 2. Test levels

### Unit tests
Test pure logic without a desktop session:
- Gesture parsing and normalization.
- Gesture state machine and direction classification.
- Arbitration and ownership rules.
- MRU ordering and window filtering using fakes.
- Show Desktop snapshot creation/reconciliation.
- Configuration parsing, validation and defaults.
- Layout calculation and feature state transitions.

### Component tests
Test a component with controlled dependencies:
- Window tracker with fake window events.
- Gesture router with fake feature handlers.
- Clipboard policy with a fake backend.
- GTK-independent overlay view models.

### Integration tests
Run in a controlled X11/XFCE environment:
- EWMH window enumeration and activation.
- Workspace navigation and boundaries.
- Minimize/restore operations.
- Desktop visibility state.
- GTK overlay stacking, focus and dismissal.
- Input subprocess lifecycle and permissions.
- Configuration and startup integration.

### Manual desktop tests
Required for real user interaction:
- Physical touchpad gesture direction and feel.
- Gesture cancellation and rapid repetition.
- Overlay behaviour above fullscreen windows.
- Compositor on/off.
- Multi-monitor and scaling.
- XFCE panel coexistence.
- Login, logout, suspend/resume and device reconnect.
- Interaction with existing gesture services.

### Packaging tests
- Clean install.
- Upgrade from prior version.
- Reinstall.
- Removal.
- Interrupted install/upgrade.
- Missing dependencies.
- Preservation of user configuration.
- No root-owned user files and no privileged GUI process.

## 3. SwipeSwitch test matrix

### Gesture input
- BEGIN / UPDATE / END normal lifecycle.
- END cancelled.
- Missing or optional sequence identifiers.
- Unexpected whitespace and event-line variations.
- Unsupported finger counts.
- Finger-count changes during gesture.
- Diagonal motion and direction threshold.
- Very short, slow and fast gestures.
- No END event / timeout.
- Input process exits, device disconnects and reconnects.

Capture real event output from the target touchpad and preserve sanitized fixtures. Do not fabricate fixtures from assumptions about the command's output.

### Window switching
- 0, 1, 2, 3 and 10+ eligible windows.
- MRU ordering.
- Sticky and current-workspace windows.
- Minimized window selected.
- Window closes during gesture.
- Workspace changes mid-gesture.
- Excluded panel/dock/desktop/overlay windows.
- Activation failure and focus-stealing constraints.

### Show Desktop and restoration
- Several visible windows.
- One visible window.
- A mix of visible and already minimized windows.
- Repeated down gesture does not replace snapshot.
- A window closes while desktop is shown.
- A new window opens while desktop is shown.
- A window changes workspace.
- Restoration after partial external state change.
- No valid snapshot: three-finger up opens Task View.
- Valid snapshot: three-finger up restores the previous visible set.
- Only one eligible window: Task View still opens and works.

### Workspace navigation
- Zero/one/multiple workspaces where environment permits.
- First and last workspace boundaries.
- Correct left/right mapping.
- Sticky windows.
- Rapid repeated navigation.
- Interaction with workspace changes from keyboard or panel.

### Regression and stress
- At least 50 consecutive gesture cycles without a stuck overlay as an initial smoke criterion.
- Repeated open/dismiss and rapid direction reversal.
- Listener termination and restart.
- GTK shutdown while worker is active.
- Long-running idle session and memory observation.

## 4. Test tooling

Use `pytest` for Python tests. Use `ruff` for linting. Add type checking only when it provides value and can be configured consistently. Desktop integration tests should be explicitly marked and skipped with a clear reason when the required X11/XFCE environment is unavailable.

## 5. Test evidence

For each milestone record:
- Commit or source revision tested.
- OS, desktop, window manager and session type.
- Python and relevant library versions.
- Commands run.
- Pass/fail counts.
- Manual scenarios completed.
- Known failures and limitations.
- Whether the result is unit-tested, integration-tested or manually verified.

## 6. Definition of done

A feature is done only when:
- Requirements and acceptance criteria exist.
- Relevant automated tests pass.
- Desktop integration and manual tests pass where needed.
- No known high-severity regression remains.
- Error handling and recovery are tested.
- Documentation and changelog are updated.
- Installation/removal impact is understood.
- The implementation status is accurately labelled.

## 7. Alpha.6 integrated feature acceptance

The automated suite now covers the following non-desktop behavior:

- Shared `X11WindowManager` parsing, geometry requests and unmaximize failure handling.
- Layout capture privacy, workspace/geometry restoration, stale/reused XID rejection and snapshot deletion.
- Gesture input event fan-out, listener lifecycle, input permission refusal and unaccelerated-delta selection.
- Four-finger incremental workspace steps, short flick fallback and reversal.
- Read-only gesture provider conflict reporting.
- XDG desktop-entry metadata, category search and hidden-entry filtering.
- Window Peek scaling and minimized-window fallback through a mocked GdkX11 surface.
- Focus Mode restoration and cleanup of a property created by Kali UX.

The target Kali machine must still verify these behaviors against real GTK/X11/xfwm4/libwnck/libinput components. In particular, automated fakes do not prove that `wmctrl` geometry is accepted by xfwm4, that GdkX11 can capture every application, or that libinput events coexist with other services.

## 8. Manual acceptance checklist

- [ ] `kali-ux swipeswitch --check` reports X11, GTK/libwnck and readable touchpad access.
- [ ] Existing gesture handlers are identified; no service is disabled automatically.
- [ ] Three-finger left/right opens, moves and commits the MRU switcher in the expected physical direction.
- [ ] Three-finger up opens Task View; keyboard arrows/Enter/Escape work.
- [ ] Three-finger down minimizes eligible windows; repeating does not overwrite the snapshot; the next up restores only the original visible set.
- [ ] Four-finger horizontal gestures navigate workspaces incrementally, reverse correctly and respect boundaries.
- [ ] Cancelling, changing finger count or pausing mid-gesture never leaves an overlay stuck.
- [ ] Window Peek previews work where capture is available and gracefully fall back to icons.
- [ ] Snap presets respect panel work areas and the monitor containing the active window.
- [ ] Layout Memory skips closed/reused windows and restores matching windows/workspaces.
- [ ] Clipboard capture is off until explicitly enabled; pause/clear work and contents do not persist after exit.
- [ ] Focus Mode restores the prior DND value on timeout and normal app close.
- [ ] Launcher search, icons, Enter activation and Gio launch work with Kali desktop entries.
- [ ] Missing Quick Panel applications are visibly unavailable, not silently failing.
- [ ] Control Center Start/Stop supervises SwipeSwitch, sends graceful termination, and stops its managed child on normal Control Center exit.
- [ ] Runtime Window Overview/Window Peek preference changes reload the running SwipeSwitch process.
- [ ] Feature toggles and Control Center shutdown do not leave child processes or altered system settings.
