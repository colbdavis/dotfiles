#!/bin/sh

# Check whether the service is active
if ! systemctl is-active --quiet tailscaled.service; then
    echo '{"text": "󰖂", "tooltip": "Tailscale: service not running", "class": "disabled"}'
    exit 0
fi

# Check the Tailscale status
STATUS=$(tailscale status --json 2>/dev/null | jq -r '.BackendState')

case "$STATUS" in
    "Running")
        echo '{"text": "󰛳", "tooltip": "Tailscale: connected", "class": "connected"}'
        ;;
    "Stopped"|"NeedsLogin")
        echo '{"text": "󰛲", "tooltip": "Tailscale: disconnected", "class": "disconnected"}'
        ;;
    *)
        echo '{"text": "󰋗", "tooltip": "Tailscale: unknown state", "class": "unknown"}'
        ;;
esac
