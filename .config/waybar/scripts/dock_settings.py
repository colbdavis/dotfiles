"""Legge le impostazioni .env come dati, senza interpretazione shell."""
import json
import re
import shlex
from pathlib import Path


def read_env(path):
    values = {}
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        key, separator, value = line.partition('=')
        key = key.strip()
        if not separator or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', key):
            raise ValueError(f'.env: invalid assignment on line {number}')
        value = value.strip()
        if value.startswith(('"', "'")):
            try:
                parts = shlex.split(value, comments=True, posix=True)
            except ValueError:
                raise ValueError(f'.env: invalid quotes on line {number}') from None
            if len(parts) != 1:
                raise ValueError(f'.env: invalid value on line {number}')
            value = parts[0]
        else:
            value = value.split(' #', 1)[0].rstrip()
        values[key] = value
    return values


def load_settings(root):
    settings = json.loads((root / 'dock-settings.json').read_text())
    env_path = root / '.env'
    env = read_env(env_path if env_path.exists() else root / '.env.example')
    for name, default in {'PI_START_DIR':'~', 'OCTO_HOST':'', 'OCTO_USER':'', 'SLACK_URL':'', 'SLACK_USER':'', 'SLACK_PROFILE':'Profile 1', 'SLACK_FLATPAK':'io.github.ungoogled_software.ungoogled_chromium'}.items():
        settings[name.lower()] = env.get(name, default)
    return settings


def ssh_command(settings):
    host, user = settings['octo_host'], settings['octo_user']
    if not host or host.startswith('-') or any(c.isspace() for c in host):
        raise ValueError('Set a valid OCTO_HOST in ~/.config/waybar/.env')
    if user and (user.startswith('-') or any(c.isspace() for c in user) or '@' in user or '@' in host):
        raise ValueError('Invalid OCTO_USER: set the username and hostname separately in .env')
    return ['ssh', *(['-l', user] if user else []), '--', host]


def pi_command(settings):
    directory = Path(settings['pi_start_dir'] or '~').expanduser()
    if not directory.is_absolute():
        directory = Path.home() / directory
    if not directory.is_dir():
        raise ValueError('PI_START_DIR in .env must point to an existing directory')
    return ['kitty', '--class', 'waybar-pi', '--title', 'Pi', '--start-as', 'normal', '--directory', str(directory), '--', *settings['pi_command']]
