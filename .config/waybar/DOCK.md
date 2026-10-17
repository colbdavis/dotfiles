# Dock Waybar

16 px monochrome SVG logos in 28 × 28 px cells, lavender gray #c5bdd9 when idle and Dracula green #50fa7b when active. Tray beside the launchers; LocalSend disappears from the dock while its process is active. VM remains as an icon with its status in the tooltip. Tailscale and Proton are green when connected; Syncthing, T3, and Pi when running; Octo during an SSH session; Slack while the web app browser is running; Obsidian while the Flatpak is running. Obsidian launches with `flatpak run md.obsidian.Obsidian`; clicking brings an existing window to the foreground.

## Anki

- Every left click opens the existing wofi-style menu with **Open GUI** and **Start AnkiConnect backend**, even while Anki is running. **Stop GUI** is also offered while the GUI is running; it requests a normal Anki shutdown through AnkiConnect (`guiExitAnki`). Sync or confirmation dialogs may need attention. Escape or an unrecognized entry does nothing.
- The 16 px original star/card icon is lavender `#c5bdd9` when stopped and green `#50fa7b` when a native Anki GUI or offscreen process owned by the current user is running. This indicates process state, **not API health**; startup/profile dialogs can leave a green icon without a working API. The existing `dock-icons.py` status adapter needs no changes.
- GUI command: `anki`. Backend command: `anki` with `QT_QPA_PLATFORM=offscreen` in its environment. Both use the same default Anki base/profile selection and installed AnkiConnect add-on. No separate collection, Rust backend, sync server, service or profile is created. `--syncserver` does not provide AnkiConnect. Existing systemd units only schedule `anki-review-notify`; they do not start Anki.
- A running GUI is focused when possible. Selecting backend while any Anki runs reuses that process and reports whether the read-only AnkiConnect `version` probe succeeds at `127.0.0.1:8765`. The hourly reminder can use this same backend.
- Choosing **Open GUI** while the backend is running requests a normal shutdown through AnkiConnect (`guiExitAnki`), waits up to 30 seconds for the process to exit, then launches the visible GUI. Failed shutdowns or blocked dialogs stop the switch and show a notification. Unknown process modes are never stopped automatically. **Stop GUI** also uses the normal Anki shutdown path. When the offscreen backend is running, the menu offers **Stop AnkiConnect backend**, requests a normal shutdown and waits up to 30 seconds for exit. No forced termination is used.
- Dock launches are serialized with a nonblocking file lock; existing native processes and an already-responsive API block duplicate launches. Anki's own single-instance IPC is retained for external-launch races. Nothing reads or modifies the collection directly. Logs: `$XDG_STATE_HOME/waybar/anki.log` (default `~/.local/state/waybar/anki.log`). Backend readiness is checked for up to about 20 seconds including bounded API probes; failure produces a notification, never a forced shutdown. No API credentials are stored.
- Implementation: `scripts/dock_anki.py`, imported by `dock-apps.py` (no executable bit needed). Focused mock-only tests: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ~/.config/waybar/tests -p 'test_anki.py' -v`. Tests never launch Anki or open its collection.

## Configurazione personale

Copy `.env.example` to `~/.config/waybar/.env` and protect it with `chmod 600 ~/.config/waybar/.env`, then edit the values. `.env` is excluded from Git; if it is missing, launchers use the values from `.env.example`.

Configurazione personale:

```dotenv
OCTO_HOST=octo.example.net
OCTO_USER=nomeutente
SLACK_URL='https://app.slack.com/client/...'
SLACK_USER='nome@example.net'
SLACK_PROFILE='Profile 1'
PI_START_DIR='~'
SLACK_FLATPAK=io.github.ungoogled_software.ungoogled_chromium
```

- `PI_START_DIR`: Pi's starting directory, defaulting to `~` (home). Sono supportati percorsi con spazi. Pi si apre in tiling, senza massimizzazione o fullscreen; le dimensioni seguono il layout del workspace.
- `OCTO_HOST`: hostname or alias defined in `~/.ssh/config`.
- `OCTO_USER`: SSH user passed with `ssh -l`; if empty, the default SSH user is used. You can still put `user@hostname` in OCTO_HOST while leaving OCTO_USER empty.
- `SLACK_URL`: Slack workspace URL.
- `SLACK_USER`: account/email to use on the site, kept as a reminder. Login happens in the browser and remains saved in the profile; the launcher does not automatically fill in the login form.
- `SLACK_PROFILE`: `Profile 1`, verified folder for the Chromium “gugu” profile.

Literal values; use quotes for spaces or special characters. The file is not executed as a shell script and does not expand `$VAR`. You can add other variables for your sites. T3 and Pi commands remain in `dock-settings.json` as argument lists.

Settings are reread on every click; no restart is needed. Launchers bring an existing window to the foreground when identifiable through Hyprland. Launch logs are in `~/.local/state/waybar/` (or `$XDG_STATE_HOME/waybar/`).

Existing service clicks remain as in the previous configuration. Timer: left click toggles/starts/pauses, right click selects a preset or disables it, middle click resets, and the scroll wheel adjusts time/mode. Pomodoro shows the current time and session, with orange indicating a pause.

## Backup e ripristino

Local backups are in `~/.config/waybar/back/` and are excluded from Git. Each folder contains `waybar.tar.gz` and `restore.sh`. Run `bash ~/.config/waybar/back/<backup>/restore.sh` to restore that backup. Restoration first saves the current configuration to `back/pre-restore-*`, then reloads Waybar.

Idle timer: 16 px hourglass only, with no border or background.

All tooltips managed by the Waybar configuration are in English. Tray applet tooltips are provided by their respective applications.
