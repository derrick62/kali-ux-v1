# Control Center

The GTK3 Control Center is the presentation layer for Kali UX. Feature metadata
lives in `core.registry`, user preferences live in the XDG configuration file,
and `ControlCenterModel` coordinates those sources with read-only platform
capability detection.

## Feature state vocabulary

The model reports three separate concepts:

- **Implementation maturity**: `integrated`, `foundation`, `prototype`, or `planned`.
- **Availability**: whether the current system satisfies the feature's declared
  requirements and whether the feature is implemented.
- **Enabled preference**: the user's saved preference. This does not start a
  daemon, take ownership of an input device, or modify desktop settings.

An unavailable feature can always be disabled. It cannot be enabled until its
requirements are satisfied. Planned features cannot be enabled.

## Configuration ownership

The Control Center must use `ControlCenterModel` for feature preferences. The
model persists changes through `core.config.save_config`, which writes a
same-directory temporary file with owner-only permissions and atomically
replaces the previous configuration. UI code must not write configuration JSON
itself.

## Safety boundary

Capability checks are read-only. Feature toggles change preferences only; they
do not start background listeners, elevate privileges, alter xfwm4 settings,
or change system services. Any future activation workflow must explain its
impact and request explicit user action.
