#!/bin/bash
set -euo pipefail
waybar_scripts=$(cd -- "$(dirname -- "$0")" && pwd)
# Hostname e utente vengono letti da ../.env senza eseguire il file.
exec "$waybar_scripts/dock-apps.py" ssh octo
