"""Anki launcher: graceful GUI shutdown and single-instance launches."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

MENU = 'Open GUI\nStart AnkiConnect backend\n'


def instances(proc=Path('/proc')):
    """Find this user's native Anki, including Python entry-point launches."""
    found = []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            argv = [a.decode(errors='replace') for a in
                    (entry / 'cmdline').read_bytes().split(b'\0') if a]
            if not argv:
                continue
            exe = Path(argv[0]).name
            native = exe in ('anki', 'ankiw')
            python = exe.startswith('python') and (
                any(a in ('/usr/bin/anki', '/usr/bin/ankiw') for a in argv[1:2])
                or argv[1:3] == ['-m', 'aqt'])
            if not (native or python) or '--syncserver' in argv:
                continue
            # If environ is unreadable, still count the process, but do not
            # assume it is safe to start another instance or focus it.
            mode = 'unknown'
            try:
                env = (entry / 'environ').read_bytes().split(b'\0')
                mode = 'backend' if any(e.startswith(b'QT_QPA_PLATFORM=offscreen')
                                        for e in env) else 'GUI'
            except OSError:
                pass
            found.append((int(entry.name), mode))
        except OSError:
            continue
    return found


def status():
    running = instances()
    modes = ', '.join(sorted({mode for _, mode in running}))
    return {
        'text': '★',
        'class': 'active' if running else 'inactive',
        'tooltip': ('Anki · ' + modes + ' running' if running else 'Anki · not running')
                   + ' · click to choose GUI or AnkiConnect backend',
    }


def notify(message):
    subprocess.run(['notify-send', '--app-name=Anki', '--icon=anki',
                    'Waybar · Anki', message], check=False, timeout=3)


def api_ready():
    """Read-only probe; never request permissions or mutate the collection."""
    request = urllib.request.Request(
        'http://127.0.0.1:8765/',
        data=b'{"action":"version","version":6}',
        headers={'Content-Type': 'application/json'})
    try:
        # Ignore proxy environment variables for the local-only API.
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
                request, timeout=0.5) as response:
            payload = json.load(response)
        return (isinstance(payload, dict) and payload.get('error') is None
                and type(payload.get('result')) is int and payload['result'] >= 6)
    except (OSError, ValueError, urllib.error.URLError):
        return False


def launch(mode, focus):
    """Serialize dock launches; Anki's own single-instance IPC remains intact."""
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'waybar'
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'anki-launch.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            notify('Anki is already starting. Please wait and try again.')
            return
        running = instances()
        if running:
            if mode == 'GUI' and all(kind == 'backend' for _, kind in running):
                if not request_close():
                    notify('Could not stop the AnkiConnect backend. Check AnkiConnect and try again.')
                    return
                for _ in range(60):
                    if not instances():
                        break
                    time.sleep(0.5)
                else:
                    notify('Anki is still closing or waiting for a dialog. Try Open GUI again after it exits.')
                    return
            elif mode == 'GUI':
                if any(kind != 'GUI' for _, kind in running):
                    notify('Cannot identify the running Anki mode. Close Anki normally before reopening it.')
                elif not focus('anki'):
                    notify('Anki is already running. Open its existing window or finish its startup.')
                return
            else:
                ready = api_ready()
                notify('Anki is already running; its GUI can also provide AnkiConnect. '
                       + ('AnkiConnect is responding on port 8765.' if ready else
                          'AnkiConnect is not responding on port 8765. Check the add-on, '
                          'profile, API key and port settings in the existing instance.'))
                return
        # Do not start against an API served by an unrecognized Anki process.
        if api_ready():
            notify('AnkiConnect is already responding, but its Anki process was not identified. '
                   'Close that instance gracefully before starting another mode.')
            return
        env = os.environ.copy()
        if mode == 'backend':
            env['QT_QPA_PLATFORM'] = 'offscreen'
        else:
            # Do not inherit a hidden platform when Open GUI was requested.
            if env.get('QT_QPA_PLATFORM', '').startswith(('offscreen', 'minimal')):
                env.pop('QT_QPA_PLATFORM')
        with (state / 'anki.log').open('ab') as log:
            log.write(('\nWaybar: starting Anki ' + mode + '\n').encode())
            log.flush()
            child = subprocess.Popen(['anki'], env=env, stdout=log, stderr=log,
                                     start_new_session=True)
        # Hold the launch lock until the API responds, the child exits, or
        # startup times out. Subsequent clicks also inspect /proc.
        for _ in range(20):
            if child.poll() is not None:
                notify('Anki exited during startup. See ' + str(state / 'anki.log') + '.')
                return
            if api_ready():
                if mode == 'backend':
                    notify('AnkiConnect backend is responding on port 8765.')
                return
            time.sleep(0.5)
        if mode == 'backend':
            notify('Anki started offscreen, but AnkiConnect is not responding on port 8765. '
                   'A profile, sync, login or add-on dialog may be blocking startup. '
                   'No forced shutdown will be attempted. See ' + str(state / 'anki.log') + '.')


def stop_gui(focus):
    running = instances()
    if not running or any(mode != 'GUI' for _, mode in running):
        notify('Anki GUI is no longer running. Reopen the menu to refresh its state.')
        return
    if not request_close():
        focus('anki')
        notify('Could not close Anki through AnkiConnect. Close its window normally.')
        return
    notify('Anki is closing. Complete any sync or confirmation dialog in its window.')


def stop_backend():
    running = instances()
    if not running or any(mode != 'backend' for _, mode in running):
        notify('AnkiConnect backend is no longer running. Reopen the menu to refresh its state.')
        return
    if not request_close():
        notify('Could not stop the AnkiConnect backend. Check AnkiConnect and try again.')
        return
    for _ in range(60):
        if not instances():
            notify('AnkiConnect backend stopped.')
            return
        time.sleep(0.5)
    notify('Anki is still closing or waiting for a dialog. No forced shutdown was attempted.')


def request_close():
    """Ask Anki to save and close using its normal asynchronous close path."""
    request = urllib.request.Request(
        'http://127.0.0.1:8765/',
        data=b'{"action":"guiExitAnki","version":6}',
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
                request, timeout=3) as response:
            payload = json.load(response)
        if not isinstance(payload, dict) or payload.get('error') is not None:
            raise ValueError('AnkiConnect rejected the close request')
    except (OSError, ValueError, urllib.error.URLError):
        return False
    return True


def menu(focus):
    options = MENU
    running = instances()
    if any(mode == 'GUI' for _, mode in running):
        options += 'Stop GUI\n'
    if running and all(mode == 'backend' for _, mode in running):
        options += 'Stop AnkiConnect backend\n'
    # Same wofi defaults and stylesheet as the existing service menus.
    result = subprocess.run(['wofi', '--dmenu', '--prompt', 'Anki'], input=options,
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return
    choice = result.stdout.strip()
    if choice == 'Open GUI':
        launch('GUI', focus)
    elif choice == 'Start AnkiConnect backend':
        launch('backend', focus)
    elif choice == 'Stop GUI' and 'Stop GUI\n' in options:
        stop_gui(focus)
    elif choice == 'Stop AnkiConnect backend' and 'Stop AnkiConnect backend\n' in options:
        stop_backend()
