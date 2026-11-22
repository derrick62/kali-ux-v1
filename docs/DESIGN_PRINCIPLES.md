# Kali UX — Design Principles

## 1. Product character

Kali UX should feel considered, responsive and calm. Windows Fluent Design is a reference for interaction quality and visual restraint, not a template to copy literally. The result must feel native enough to coexist with Kali's XFCE desktop and its light/dark themes.

## 2. Interaction principles

### Clarity before cleverness
Every gesture, shortcut and control needs a discoverable purpose. Avoid hidden interactions that cannot be learned or configured.

### Predictability
The same action should produce the same result in the same state. Context-sensitive behaviour must be explained and visually communicated. SwipeSwitch's three-finger-up behaviour is intentionally state-dependent: restore when a valid Show Desktop snapshot exists; otherwise open Task View.

### Responsiveness
Show immediate feedback for accepted input. Keep expensive operations—such as thumbnail capture—off the UI thread and make them optional where possible.

### Reversibility
Settings and desktop changes should be easy to undo. Dismiss overlays with Escape where appropriate. Provide safe recovery if an interaction is interrupted.

### Respect native behaviour
Use XFCE settings and window-manager capabilities when they already solve the problem. Avoid duplicating or fighting the panel, compositor, session manager or window manager.

### Consistency without uniformity
Shared spacing, typography, selection, motion and keyboard conventions should make modules feel related. Different tasks may still need different layouts.

## 3. Visual language

Establish design tokens after evaluating the actual Kali XFCE themes:
- Semantic surface/background/foreground colors.
- Accent and status colors.
- Typography scale and weights.
- Spacing scale.
- Corner radii.
- Borders and elevation.
- Focus and selection states.
- Icon style and sizing.
- Overlay dimming and opacity fallbacks.

Do not hardcode a single dark palette as the only supported appearance. Support theme-aware styling where feasible and preserve readable contrast if compositing/transparency is unavailable.

## 4. Motion

Motion should explain state transitions, not decorate every action. Keep it short, interruptible and optional. Respect reduced-motion preferences. Never make animation a prerequisite for selecting a window or dismissing an overlay.

## 5. Accessibility

- Keyboard navigation for interactive overlays.
- Visible focus indicator.
- Escape dismissal where safe.
- Readable text at normal desktop scaling.
- Contrast that remains usable across themes.
- No color-only communication of selection/status.
- Reduced-motion behaviour.
- Sensible behaviour at different display scales.

## 6. Window switcher and Task View

The horizontal switcher optimizes rapid sequential selection. Task View optimizes scanning and choosing among all eligible windows. They should not be visually or behaviourally conflated. Titles must remain legible; icons should appear immediately; thumbnails are progressive enhancement and must not delay the core interaction.

## 7. Error and empty states

Explain why a feature is unavailable (unsupported session, missing dependency, no eligible windows, conflicting gesture service) and offer a safe next step. Avoid vague error messages and silent failure.

## 8. Design validation

Validate interfaces on the actual XFCE desktop with:
- Kali dark and light themes.
- Compositor enabled and disabled.
- Different window counts.
- Keyboard-only interaction.
- Different scaling and monitor arrangements.
- Fullscreen and maximized windows.
- Reduced-motion settings where available.

Do not claim accessibility conformance without a defined audit and evidence.
