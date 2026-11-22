# Install and run Kali UX

## Supported initial environment

- Kali Linux with XFCE.
- X11 session (not Wayland).
- Python 3.10 or newer.
- GTK3, PyGObject and libwnck from Kali/Debian packages.

## Install system dependencies

```bash
sudo apt update
sudo apt install \
  python3 python3-venv python3-pip python3-gi \
  gir1.2-gtk-3.0 gir1.2-wnck-3.0 \
  libinput-tools wmctrl xfconf xfce4-notifyd \
  libglib2.0-bin coreutils
```

Some packages may already be installed. Optional Quick Panel applications include `pavucontrol`, `nm-connection-editor`, `xfce4-display-settings`, `xfce4-power-manager-settings` and `xfce4-keyboard-settings`; the UI disables actions whose executable is missing.

## Install from the source archive

Extract the archive, enter the project directory and create a venv that can see system GI bindings:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

For development dependencies instead:

```bash
python -m pip install -e '.[dev]'
```

Do not use `sudo pip`. Do not run the graphical application as root.

## First run

```bash
kali-ux init
kali-ux gui
```

Open the Features page and enable the modules you want to use. Feature preferences are not service start commands. Clipboard monitoring remains separately opt-in from its Clipboard page.

## Check and start SwipeSwitch

```bash
kali-ux swipeswitch --check
kali-ux swipeswitch
```

The check verifies X11/GTK/libwnck imports, touchpad discovery and whether the selected event device is readable by the current user. If access is denied, stop and review your local input-device permission policy. Kali UX will not add the user to the `input` group or change device permissions automatically. Do not solve this by running the GUI as root.

**Important limitation:** SwipeSwitch currently uses `libinput debug-events`. The libinput documentation describes this as a debugging helper whose output may change and which usually needs access to `/dev/input/event*` (often root access). Kali UX does not elevate itself. The provider therefore only works where your normal user already has suitable access, and it is not yet a production-stable input API. This is the main unresolved integration risk in alpha.6.

It may also conflict with another gesture handler. Open Control Center → Gestures and scan for other handlers before enabling it. Kali UX only reports conflicts; it will not disable them.

## Configuration

- Kali UX: `~/.config/kali-ux/config.json` (or `$XDG_CONFIG_HOME/kali-ux/config.json`)
- SwipeSwitch: `~/.config/swipeswitch/config.toml` (or `$XDG_CONFIG_HOME/swipeswitch/config.toml`)
- Layout snapshots: `~/.local/share/kali-ux/layouts.json` (or `$XDG_DATA_HOME/kali-ux/layouts.json`)

The clipboard history is memory-only. Layout snapshots are explicit, omit window titles and are written with owner-only permissions.

## Verification

```bash
./scripts/check.sh
```

The alpha.6 build-container result is 88 passed and 0 skipped. You must still perform the manual desktop checks in `docs/TESTING.md`.

## Uninstall

For a venv installation, deactivate and remove the project venv and source directory when no longer needed. User configuration/data are not automatically deleted; remove them manually only if you intentionally want to discard your settings and saved layouts. No autostart entry or systemd service is installed by this alpha.

## Packaging status

This alpha includes a Python wheel/source install path only. A Debian package and APT repository are not shipped or claimed as tested.
