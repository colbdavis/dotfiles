#!/bin/sh

# Controlla se il servizio è attivo
if ! systemctl is-active --quiet tailscaled.service; then
    echo '{"text": "󰖂", "tooltip": "Tailscale: servizio non attivo", "class": "disabled"}'
    exit 0
fi

# Controlla lo stato di Tailscale
STATUS=$(tailscale status --json 2>/dev/null | jq -r '.BackendState')

case "$STATUS" in
    "Running")
        echo '{"text": "󰛳", "tooltip": "Tailscale: connesso", "class": "connected"}'
        ;;
    "Stopped"|"NeedsLogin")
        echo '{"text": "󰛲", "tooltip": "Tailscale: disconnesso", "class": "disconnected"}'
        ;;
    *)
        echo '{"text": "󰋗", "tooltip": "Tailscale: stato sconosciuto", "class": "unknown"}'
        ;;
esac
