# Packaging status

The alpha source archive is installable with `python -m pip install -e .` inside a user-owned virtual environment. GTK3 and libwnck bindings should be installed from Kali/Debian packages (`python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-wnck-3.0`) rather than built through pip.

A production `.deb`, APT repository, autostart entry, systemd user unit and uninstall lifecycle are intentionally not shipped yet. They require target-release dependency verification, safe upgrade/removal tests, and explicit user consent for startup integration. Do not run the GUI as root. Do not add an installer that changes input-group membership, disables another gesture daemon, overwrites user autostart files, or modifies XFCE settings without a clear opt-in flow.
