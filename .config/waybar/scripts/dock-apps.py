#!/usr/bin/env python3
"""Launcher Waybar: comandi come liste, senza interpretazione shell."""
import json
import os
from pathlib import Path
import subprocess
import sys
import shlex

from dock_settings import load_settings, ssh_command, pi_command
import dock_anki

ROOT = Path(__file__).resolve().parent.parent
ICONS = {'t3code': '󰨞', 'pi': 'π', 'octo': '󰣀', 'slack': '󰒱', 'obsidian': '󱓧', 'anki': '★'}
NAMES = {'t3code': 'T3 Code', 'pi': 'Pi', 'octo': 'SSH · Octo', 'slack': 'Slack', 'obsidian': 'Obsidian', 'anki': 'Anki'}
CLASSES = {'t3code': 'com.t3tools.T3Code', 'pi': 'waybar-pi', 'octo': 'waybar-octo', 'slack': 'waybar-slack', 'obsidian': 'obsidian', 'anki': 'anki'}


def processes():
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            argv = (entry / 'cmdline').read_bytes().split(b'\0')
            yield [arg.decode(errors='replace') for arg in argv if arg]
        except (OSError, ProcessLookupError):
            continue


def is_active(app, settings):
    if app == 'anki':
        return bool(dock_anki.instances())
    if app == 'obsidian':
        try:
            apps = subprocess.check_output(['flatpak', 'ps', '--columns=application'], text=True, stderr=subprocess.DEVNULL, timeout=2)
            return 'md.obsidian.Obsidian' in apps.splitlines()
        except (OSError, subprocess.SubprocessError):
            return False
    if app == 'slack':
        try:
            clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL, timeout=2))
            if any(c.get('class') == CLASSES[app] for c in clients):
                return True
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    for argv in processes():
        if not argv:
            continue
        executable = Path(argv[0]).name
        if app == 't3code' and executable == 't3code':
            return True
        if app == 'pi' and (executable == 'pi' or any('/@earendil-works/pi-coding-agent/' in arg and arg.endswith('/cli.js') for arg in argv)):
            return True
        if app == 'octo' and executable == 'ssh' and settings['octo_host'] and settings['octo_host'] in argv:
            return True
        if app == 'slack' and settings['slack_url'] and executable in ('chrome', 'chromium', 'chromium-browser') and '--app=' + settings['slack_url'] in argv and '--profile-directory=' + settings['slack_profile'] in argv:
            return True
    return False


def focus(app):
    try:
        clients = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], stderr=subprocess.DEVNULL, timeout=2))
        match = next((c for c in clients if c.get('class') == CLASSES[app] or (app == 'obsidian' and c.get('class', '').lower() in ('obsidian', 'md.obsidian.obsidian'))), None)
        if match:
            if app == 'pi':
                window = 'address:' + match['address']
                lua = 'hl.dispatch(hl.dsp.window.fullscreen_state({ window = ' + json.dumps(window) + ', action = "set", internal = 0, client = 0 })); hl.dispatch(hl.dsp.window.float({ window = ' + json.dumps(window) + ', action = "unset" }))'
                subprocess.run(['hyprctl', '--quiet', 'eval', lua], check=True, timeout=3)
            subprocess.run(['hyprctl', 'dispatch', 'focuswindow', 'address:' + match['address']], check=True, stdout=subprocess.DEVNULL, timeout=2)
            return True
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return False


def main():
    action, app = sys.argv[1:]
    if app == 'anki':
        if action == 'status':
            print(json.dumps(dock_anki.status(), ensure_ascii=False))
        elif action == 'launch':
            dock_anki.menu(focus)
        else:
            raise ValueError('Unknown Anki action: ' + action)
        return
    settings = load_settings(ROOT)
    if action == "ssh":
        command = ["kitty", "--class", CLASSES["octo"], "--title", "SSH · Octo", "--start-as", "normal", "--", *ssh_command(settings)]
        os.execvp(command[0], command)
    missing = (app == 'octo' and not settings['octo_host']) or (app == 'slack' and not settings['slack_url'])
    if action == 'status':
        active = is_active(app, settings)
        tooltip = NAMES[app] + (' · running' if active else ' · launch')
        if missing:
            tooltip = NAMES[app] + ' · configure ' + ('OCTO_HOST / OCTO_USER' if app == 'octo' else 'SLACK_URL') + ' in .env'
        print(json.dumps({'text': ICONS[app], 'class': 'active' if active else 'inactive', 'tooltip': tooltip}, ensure_ascii=False))
        return
    if missing:
        subprocess.run(['notify-send', 'Waybar · ' + NAMES[app], 'Set OCTO_HOST / SLACK_URL in ~/.config/waybar/.env.'], check=False)
        return
    if focus(app):
        return
    if app == 't3code':
        command = settings['t3code_command']
    elif app == 'pi':
        command = pi_command(settings)
    elif app == 'obsidian':
        command = ['flatpak', 'run', 'md.obsidian.Obsidian']
    elif app == 'octo':
        command = [str(ROOT / 'scripts/octo-ssh.sh')]
    else:
        if not settings['slack_url'].startswith(('https://', 'http://')):
            raise ValueError('SLACK_URL in .env must be an http(s) URL')
        command = ['flatpak', 'run', settings['slack_flatpak'], '--profile-directory=' + settings['slack_profile'], '--class=' + CLASSES[app], '--app=' + settings['slack_url']]
    logdir = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'waybar'
    logdir.mkdir(parents=True, exist_ok=True)
    if app == 'pi':
        # Startup rules apply to this window without modifying Hyprland.
        shell_command = shlex.join(command) + ' >> ' + shlex.quote(str(logdir / 'pi.log')) + ' 2>&1'
        delimiter = '='
        while ']' + delimiter + ']' in shell_command:
            delimiter += '='
        literal = '[' + delimiter + '[' + shell_command + ']' + delimiter + ']'
        rules = '{ tile = true, fullscreen_state = "0 0", suppress_event = "maximize fullscreen" }'
        subprocess.run(['hyprctl', '--quiet', 'eval', 'hl.dispatch(hl.dsp.exec_cmd(' + literal + ', ' + rules + '))'], check=True, timeout=3)
        return
    with (logdir / (app + '.log')).open('ab') as logfile:
        subprocess.Popen(command, stdout=logfile, stderr=logfile, start_new_session=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        if len(sys.argv) > 1 and sys.argv[1] == 'status':
            print(json.dumps({'text': ICONS.get(sys.argv[-1], '?'), 'class': 'inactive', 'tooltip': str(error)}))
        else:
            subprocess.run(['notify-send', 'Waybar · launcher error', str(error)], check=False)
        sys.exit(1)
