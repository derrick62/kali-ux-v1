# SwipeSwitch integration

The GTK3/libwnck SwipeSwitch engine is integrated under `engine/`. Run `kali-ux swipeswitch` or `kali-ux-swipeswitch` in an X11 session after installing the system GTK3/libwnck bindings and libinput tooling.

The implementation follows the current public `derrick62/swipeswitch` main-branch behavior for normalized libinput events, optional unaccelerated deltas, incremental four-finger workspace navigation, live-XID activation and Task View. Kali UX adds a single-owner `GestureInputService`, action routing and feature-preference gating.

The switcher overlay and Task View support lazy GdkX11 previews through `engine/thumbs.py`, with icon fallback when capture is unavailable. Overlay placement supports the primary or pointer monitor. Task View has keyboard navigation and resolves selections against the live window list.

**Important integration boundary:** the listener still reads `libinput debug-events`. This is a diagnostic command rather than a dedicated application event API, so target-version behavior, device permissions and coexistence with other gesture handlers must be validated on the actual Kali machine. Kali UX checks device readability and reports other handlers, but never changes permissions or disables them automatically.

The service is explicitly started; no autostart or privileged input helper is installed.
