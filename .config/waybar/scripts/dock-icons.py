#!/usr/bin/env python3
"""Seleziona logo SVG e colore secondo lo stato del modulo."""
import html
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = {'tailscale':'tailscale-status.sh', 'syncthing':'syncthing-status.sh', 'protonvpn':'vpn-status.sh', 'localsend':'localsend-status.sh', 'vms':'vms-status.sh'}
app = sys.argv[1]
command = [str(ROOT / 'scripts' / SCRIPTS[app])] if app in SCRIPTS else [str(ROOT / 'scripts/dock-apps.py'), 'status', app]
try:
    result = subprocess.run(command, capture_output=True, text=True, timeout=4)
    status = json.loads(result.stdout)
    if app == 'localsend' and not status.get('text'):
        print('\nLocalSend running in the system tray')
    else:
        state = 'active' if status.get('class') in ('active', 'connected', 'running') else 'inactive'
        print(ROOT / 'icons' / f'{app}-{state}.svg')
        print(html.escape(status.get('tooltip', app)).replace('\n', ' · '))
except (OSError, ValueError, subprocess.SubprocessError) as error:
    print(ROOT / 'icons' / f'{app}-inactive.svg')
    print(html.escape(f'{app}: {error}'))
