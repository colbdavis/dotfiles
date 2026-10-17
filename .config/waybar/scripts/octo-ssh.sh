#!/bin/bash
set -euo pipefail
waybar_scripts=$(cd -- "$(dirname -- "$0")" && pwd)
# Hostname and user are read from ../.env without executing the file.
exec "$waybar_scripts/dock-apps.py" ssh octo
