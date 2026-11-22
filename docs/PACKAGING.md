# Kali UX — Packaging and Distribution

## Direction

The target distribution is Kali Linux, so Debian packaging and APT are the natural native distribution path. Begin with reproducible local package builds and documented dependencies. Consider a signed APT repository only after the package and release process is reliable.

## Python packaging

- Use `pyproject.toml`.
- Use the `src/` layout.
- Keep the base runtime dependency set minimal.
- Prefer Debian packages for GTK/PyGObject and native libraries.
- Do not require `sudo pip`.
- Do not modify Kali's system-managed Python environment.
- Keep development dependencies separate from runtime dependencies.

## Debian package requirements

The package must:
- Declare accurate runtime dependencies.
- Install files in standard locations.
- Provide valid desktop/autostart entries only when appropriate.
- Avoid launching GUI applications as root.
- Avoid deleting user configuration on package removal.
- Make maintainer scripts idempotent and noninteractive.
- Avoid starting a graphical process during package installation.
- Support clean upgrade and removal.

## Packaging tests

Test fresh install, upgrade, reinstall, removal, interrupted operations and missing dependencies in a disposable environment. Verify file ownership and ensure no user files are unexpectedly changed.

## Package split

Not yet decided whether Kali UX and SwipeSwitch should be one package, a suite package with feature packages, or separate packages. Keep SwipeSwitch independently auditable and potentially independently releasable until a deliberate decision is made.

## Release hygiene

Each release should include:
- Version and changelog.
- Supported platform matrix.
- Installation/upgrade/removal instructions.
- Known limitations.
- Test evidence.
- Checksums.
- License and third-party notices.

## Alpha.6 status

Alpha.6 is distributed as a source archive and a Python wheel. It does not yet include Debian packaging metadata, a `.deb`, a signed APT repository, a systemd user unit or an autostart installer. This is deliberate: dependency declarations and lifecycle scripts must be tested on the supported Kali release before native packages are published. The install path and current artifact verification are documented in `docs/INSTALL.md` and `docs/VERIFICATION_REPORT.md`.
