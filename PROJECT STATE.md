# docs/PROJECT_STATE.md

# Kali UX — Project State and Source of Truth

> **This file is the control document.** Every development session begins by reading it and ends by updating it.
> If anything in this file conflicts with another document, this file is authoritative for *current position*;
> the product specification and architecture docs are authoritative for *intent*.
> Last updated: [date of this bundle's integration]

---

## 1. Project identity

| Field | Value |
|---|---|
| Product | Kali UX — modular desktop-experience suite for Kali Linux |
| Repository | `derrick62/kali-ux-v1` |
| Baseline version | `0.3.0-alpha.6` |
| Baseline state | Single "Initial commit" — archive and remote `main` are the same tree |
| Baseline verified on live desktop | **No.** Nothing has been run on the target Kali/XFCE/X11 machine |
| Recorded test report | 88 passed, 0 skipped (container report in `docs/VERIFICATION_REPORT.md`; not rerun in this process) |
| Initial platform contract | Kali Linux · XFCE · `xfwm4` · X11 · Python 3.10+ · GTK3/PyGObject |
| Distribution target | Debian package, later signed APT repository (not yet shipped) |

**Target architecture** is defined in the finished-structure blueprint (source: the "I would structure the finished Kali UX as a…" document). Alpha.6 is the *starting point*; the target is the *destination*. We evolve toward it deliberately, never by wholesale rewrite.

---

## 2. The product we are building (compressed, authoritative)

Kali UX is **one coordinated desktop layer**, not a dashboard of utilities. The Control Center is one interface to the product, not the product.

**Objectives:** better window/workspace/gesture interaction; coherent visual language across every surface; modular enable/disable; shared infrastructure instead of per-feature reinvention; reliability and safety; maintainability and extensibility; a proper installable/updateable/removable Linux product.

**What it is not:** a replacement for XFCE, `xfwm4`, the compositor, the panel, or the session manager. Not a general system-config tool. Not root-requiring. Not a competitor to other gesture daemons. Not a pile of scripts behind a dashboard.

**Ten user-facing features (the product surface):**
SwipeSwitch (window switcher) · Gesture Control · Window Overview / Task View · Window Peek · Snap Assist · Clipboard History · Quick Panel · Focus Tools · Application Launcher · Layout Memory.
Plus: the **Control Center** (management), and **Diagnostics** (read-only health).

---

## 3. Engineering philosophy (the decision rules)

These constrain every change. When a choice is unclear, these decide it.

1. **Integration, not replacement.** Kali UX requests; the desktop performs. `xfwm4` stays authoritative for focus, stacking, final geometry.
2. **Separation of concerns.** Listener ≠ recognizer ≠ controller ≠ platform adapter ≠ UI. No layer does another's job.
3. **Modular monolith.** One codebase, clear module boundaries, shared services. A separate process only for a real lifecycle/technical reason (the continuous input listener is the canonical case).
4. **Predictable interaction.** Every action has a beginning, response, and end. Gestures are cancellable; failed operations don't leave misleading UI.
5. **Visual restraint.** Animation communicates; it does not delay. Theme-aware, accessible contrast, reduced-motion support.
6. **User ownership and privacy.** No silent permission changes, daemon disabling, XFCE rewrites, or clipboard persistence without explicit consent. No telemetry.
7. **Engineering before cosmetics — but not instead of design.** Coherent feature groups, integrated continuously; no permanently unfinished prototypes.

**The data flow invariant (memorize this):**
`touchpad → platform input provider → shared gesture service (normalize + recognize) → gesture action router → feature (e.g. window switcher, MRU selection) → shared window service → platform backend → xfwm4`.
Each layer is unaware of the layers beneath it. The gesture service knows nothing of overlay visuals; the switcher knows nothing of how input arrives; neither overrides window management.

---

## 4. The architectural destination (target structure)

Per the finished-structure blueprint, the target is:

src/kali_ux/
core/ application, lifecycle, feature_manager, feature_registry,
config/ (manager, schema, defaults, migrations, validation),
events/ (bus, event, topics, subscriptions),
logging/ (setup, handlers, filters), paths, exceptions, signals, utilities
platform/ detection/ display/ windows/ input/ desktop/ processes/ + compatibility
services/ input/ gestures/ windows/ thumbnails/ clipboard/ applications/
notifications/ shortcuts/
features/ one directory per feature (service, controller, models, config, ui/, README)
control_center/ application, controller, navigation, feature_overview,
feature_details, settings_manager, status_manager, onboarding
ui/ app, window, navigation, dialogs/, components/, pages/, accessibility/
design/ tokens, colors, typography, spacing, icons, animations, themes, styles/
integrations/ xfce/, x11/, applications/
diagnostics/ service, report, health_check, feature_check, input_check,
desktop_check, dependency_check, export
resources/ icons/, images/, sounds/, ui/, schemas/, metadata/

text

**Alpha.6 starting point (what actually exists now):**
src/kali_ux/
core/ config.py, paths.py, registry.py
platform/ capabilities.py, commands.py, gtk.py, window_manager.py
features/ gesture_control/, window_switcher/ (engine/), window_overview/,
window_peek/, snap_assist/, clipboard_history/, quick_panel/,
focus_tools/, launcher/, layout_memory/
control_center/ model.py
diagnostics/ report.py
ui/ app.py (~788 lines), pages/ (home, features, windows, clipboard,
applications, productivity, settings)

text

**The gap, stated plainly:** alpha.6 has feature code and a `wmctrl` window adapter but **no shared window service interface**, **no feature lifecycle manager** (the five states are aspirational, not implemented), and **no `services/` layer** — features hold overlapping responsibilities that the target centralizes. `ui/app.py` owns too much orchestration. These are the first structural gaps to close.

---

## 5. The five-state model (make these honest)

Every feature is described along five independent axes. They are **not interchangeable** and must never be conflated in status reporting:

| State | Meaning |
|---|---|
| **Implemented** | Code exists for the feature |
| **Available** | The current system satisfies its platform requirements |
| **Enabled** | The user has enabled it in configuration |
| **Running** | Its background service/process is active |
| **Healthy** | Its service is operating correctly |

Alpha.6 handles Implemented/Available/Enabled partially (via `control_center/model.py`); Running/Healthy are handled ad hoc (SwipeSwitch process supervisor). **Unifying them is the job of the lifecycle contract we are about to build.**

---

## 6. Engineering rules (never abandon)

- No duplicated platform operations — features use shared adapters.
- No GTK in business logic — services testable without constructing widgets.
- No direct hardware access from UI pages — the input service owns devices.
- No hidden system changes — config, startup, permissions are explicit.
- No unbounded background processes — every long-running process has an owner, lifecycle, shutdown.
- No arbitrary shell — structured argument lists through `platform/commands.py`.
- No sensitive data in logs — clipboard contents, unnecessary window titles, raw user data.
- No false feature status — a prototype stays a prototype until acceptance criteria are met.
- No untested architecture changes — shared interfaces get tests and documented contracts.
- No silent scope changes — new ideas are recorded as decisions before changing scope.

---

## 7. Current development position

**Milestone 0 — Baseline verification and project control: ✅ effectively complete.**
Archive and remote `main` are the same tree (all files "Initial commit"). One agreed source baseline exists. The remaining Milestone 0 item — an accurate inventory of implemented / incomplete / planned — is produced incrementally by this tracker and the feature specs.

**Milestone 1 — Product definition and architectural foundation: 🔄 in progress.**
The destination architecture is agreed (finished-structure blueprint). The first two contracts are being implemented now:
- **Shared window-service interface** (behind which the existing `wmctrl` adapter sits, unchanged in behavior).
- **Feature-lifecycle contract** (the five states made real: `start` / `stop` / `status` / `recover`, with ownership of long-running services).

**Everything else (Milestones 2–10) is blocked on those contracts for the window and productivity tracks** and is not started.

### Milestone ledger

| # | Milestone | Status | Notes |
|---|---|---|---|
| 0 | Baseline verification | ✅ Done | Archive = remote; inventory ongoing via this doc |
| 1 | Product definition & architectural foundation | 🔄 In progress | Window-service + lifecycle contracts this round |
| 2 | Desktop & input infrastructure | ⬜ Not started | Gated on live input-provider decision (see risks) |
| 3 | Complete window navigation | ⬜ Not started | Blocked on window-service contract |
| 4 | Snap Assist & arrangement | ⬜ Not started | Blocked on window-service contract |
| 5 | Productivity features | ⬜ Not started | Blocked on lifecycle contract |
| 6 | Complete Control Center | ⬜ Not started | Depends on lifecycle |
| 7 | Visual refinement & polish | ⬜ Not started | — |
| 8 | Reliability, security, compatibility | ⬜ Not started | — |
| 9 | Debian packaging & release | ⬜ Not started | Deliberately deferred |
| 10 | Expansion & maintenance | ⬜ Not started | Post-1.0 |

### Current feature maturity (alpha.6 — honest assessment)

| Feature | Implemented | Remaining work before acceptance |
|---|---|---|
| SwipeSwitch | Integrated engine | Production input provider; live acceptance; interaction refinement |
| Gesture Control | Shared listener owner + router | Reliable provider strategy; additional consumers |
| Task View / Overview | GTK grid | Live behavior, focus handling, multi-monitor, polish |
| Window Peek | On-demand thumbnails | Compositor/window-state behavior |
| Snap Assist | 8 presets | Full snap experience, suggestions, robust geometry |
| Clipboard History | Session-only text | Privacy refinement, richer formats, complete UX |
| Quick Panel | XFCE settings launchers | More unified controls where supported |
| Focus Tools | Timed DND | Robust recovery, lifecycle validation |
| Launcher | XDG entry search/launch | Complete launcher experience |
| Layout Memory | Save/restore | Monitor topology, stale windows, reliability |
| Control Center | GTK3 dashboard | Deeper separation, complete settings, lifecycle |
| Diagnostics | Read-only checks | Service health, recovery guidance |

**No feature is production-ready.** Code and automated tests exist; live desktop acceptance does not.

---

## 8. The contract being implemented now (Milestone 1, first bundle)

**Deliverable:** Shared window-service interface + feature-lifecycle contract, with the existing `wmctrl` adapter preserved behind the interface and existing features wired to report honest state.

**In scope**
- A defined **window-service interface**: discovery, identity, activation, geometry request, workspace/monitor/work-area query, state query.
- A defined **lifecycle contract**: `start` / `stop` / `status` / `recover`; the five states made real; an explicit owner for long-running services; no GTK dependency in the contract itself.
- **Wiring:** `core/feature_registry.py` and `control_center/model.py` consume both, so existing features report honest Implemented/Available/Enabled/Running/Healthy.
- **Preservation:** the existing `wmctrl` adapter is retained as one backend implementation — SwipeSwitch, Snap Assist, Layout Memory keep working.
- **Tests** that pass without a GTK display.
- **Docs:** the feature-spec for the contract, the ADR recording the interface decisions, and this tracker updated.

**Out of scope (deliberately)**
- Any new user-visible feature.
- Replacing `wmctrl` or introducing libwnck/EWMH backends (a later decision, recorded in an ADR).
- Touching the gesture provider (separate Milestone 2 decision).
- Rewriting `ui/app.py` (incremental refactor, later).

**Acceptance criteria**
- Existing features continue to function unchanged (no regressions in the 88-test container report scope).
- Every feature's state is derivable from the contract, with Running/Healthy no longer conflated with Enabled.
- The contract is testable without a display server.
- The ADR and feature spec are committed alongside the code.
- **Your live acceptance:** confirm on your Kali machine that the refactor did not change observable behavior of existing features, and that state reporting matches reality.

---

## 9. The collaboration protocol

1. You name the feature/contract (or approve my roadmap recommendation).
2. I refer to `derrick62/kali-ux-v1` and produce a **bundle**: a directory tree mirroring the target `src/kali_ux/...` + `tests/...` + `docs/...`, **full file contents at full paths**, plus a short `BUNDLE_MANIFEST.md` listing every path and its purpose. Docs (feature spec + ADR) are included in the same round.
3. You integrate into your checkout and test (locally, and live where the feature requires it).
4. You give feedback.
5. If good, you push to the repo.
6. I confirm the pushed state and we proceed.

**Traceability is mandatory:** every bundle maps requirement → architecture layer → files → tests → acceptance criteria. Nothing is dropped in ad hoc.

---

## 10. Honesty ledger — what is and isn't verified

**Verified:** the baseline tree exists and matches the remote; the architecture and feature inventory are accurately described above; the container test report is recorded (not rerun here).

**Not verified — requires your machine:** touchpad input and device readability; real GTK rendering and overlay behavior; real `xfwm4` geometry constraints; multi-monitor work areas; clipboard-manager coexistence; Focus Tools restoration on abrupt termination; packaging install/upgrade/removal lifecycle; long-running stability.

**Never to be claimed without live acceptance:** "production-ready", "works on Kali", "handles multi-monitor", "packaging complete".

---

## 11. Biggest technical risks (standing list)

1. **Gesture input provider.** `libinput debug-events` is a diagnostic tool, not a production API; it may need direct device access and may conflict with other gesture daemons. A reliable provider must be proven on the target machine. *(Milestone 2 gate.)*
2. **Window backend.** `wmctrl` is useful but incomplete for a mature interaction system. A future ADR must decide libwnck vs EWMH vs additional bindings. *(Recorded, deferred.)*
3. **Control Center orchestration.** `ui/app.py` owns too much; incremental refactor, not rewrite.
4. **Feature lifecycle.** Being closed by the current contract bundle.
5. **Visual consistency.** Overlays and feature UIs still need unified design-system review.
6. **Packaging.** Debian/APT lifecycle unproven; deferred deliberately.

---

## 12. Session handover checkpoint (update every session)

- **Version/branch:** 0.3.0-alpha.6 baseline; development branch for contract work.
- **Files changed this session:** [populated on integration of the first bundle]
- **Decisions made:** [ADR links]
- **Tests executed / results:** [recorded on your machine]
- **Features completed/partial:** [none new; contract work]
- **Known issues/regressions:** [recorded on integration]
- **Next specific task:** [next bundle after this contract is accepted]
- **Live desktop testing still required:** [listed per bundle]

---