#!/bin/sh

if pgrep -f "syncthing --no-browser" > /dev/null; then
    echo '{"text": "󰤲", "tooltip": "Syncthing: attivo", "class": "active"}'
else
    echo '{"text": "󰼤", "tooltip": "Syncthing: inattivo", "class": "inactive"}'
fi