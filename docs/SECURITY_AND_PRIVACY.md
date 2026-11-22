# Kali UX — Security and Privacy

## Principles

Kali UX is a local desktop utility. It requires no network access, telemetry or privileged background process. It runs as the logged-in user and leaves the desktop's own window manager in control.

## Execution and permissions

- Do not use setuid binaries or run GTK interfaces as root.
- SwipeSwitch checks read access to the selected touchpad event device before starting.
- Kali UX does not add users to the `input` group, change device ACLs, or alter permissions automatically.
- Gesture conflict inspection is read-only. It never stops or reconfigures Touchégg, libinput-gestures, Fusuma, Gebaar or other services.
- External commands are passed as argument arrays, not interpolated shell strings.
- Listener shutdown is explicit and child processes are terminated during normal shutdown.
- The Control Center supervises only the SwipeSwitch process it starts; it does not stop an independently launched terminal instance.
- SwipeSwitch logs are stored under user data with owner-only permissions and contain diagnostics, not clipboard contents or window titles.

The current listener uses `libinput debug-events`. Libinput documents this as a debugging helper whose output may change and which usually requires direct access to input event devices, often root access. Kali UX never elevates itself. The provider therefore only works where the normal user already has suitable access and remains an integration risk until replaced or formally validated. Its permissions and coexistence must be tested on the target machine before daily-use release.

## Input data

The gesture service consumes normalized swipe events only. It does not capture keyboard content. Raw event streams are not logged by default; debug logging is explicit. Diagnostics report known provider names and autostart entry paths but do not record raw input.

## Clipboard data

Clipboard History is opt-in and session-only. Entries are bounded by item count and byte size, deduplicated, searchable and clearable. Clipboard contents are not written to disk, logs or diagnostics. There is no reliable automatic detection of password fields or sensitive applications; users should pause capture before copying secrets. The current backend watches GTK's `CLIPBOARD` selection, not `PRIMARY` selection.

Persistent clipboard history is intentionally not included. Any future persistence requires a separate consent, retention, exclusion and deletion design.

## Window metadata and previews

Layout Memory stores XID, PID, WM_CLASS, desktop and geometry. It deliberately omits window titles because titles can contain private information. Files are stored with owner-only permissions. Restore verifies the saved identity against the current window list before requesting changes.

Window previews are captured locally on demand from X11 foreign windows. They are not stored. Obscured/off-screen content may be absent; minimized, protected or inaccessible windows fall back to icons.

## Focus Mode

Focus Mode changes the XFCE notification daemon's do-not-disturb property for a timed session and restores the previous value on timeout or normal Control Center shutdown. If Kali UX created the property because it did not exist, it removes that property on restore. Abrupt process termination, power loss or session failure can interrupt cleanup; verify the notification state after an abnormal exit.

## Diagnostics and network

Diagnostics are read-only and exclude clipboard payloads, raw input and window titles. No network access is required. Future network features must document purpose, destinations, data types, consent and failure behavior before implementation.

## Safe system changes

No autostart entry, systemd user service, privileged helper, APT repository or system-wide configuration change is installed by this alpha. User configuration and layout data are not automatically deleted during uninstall.
