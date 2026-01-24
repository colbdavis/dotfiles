#!/bin/sh

# Controlla se il processo syncthing è realmente in esecuzione
# Esclude grep e altri script dal conteggio
if pgrep -x syncthing > /dev/null 2>&1; then
    echo '{"text": "󰤲", "tooltip": "Syncthing: active", "class": "active"}'
else
    echo '{"text": "󰼤", "tooltip": "Syncthing: inactive", "class": "inactive"}'
fi