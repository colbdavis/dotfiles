#!/bin/sh

STATE_FILE="/tmp/tailscale-waybar-state"

# Ottieni stato attuale
get_status() {
    if ! systemctl is-active --quiet tailscaled.service; then
        echo "disabled"
        return
    fi
    
    STATUS=$(tailscale status --json 2>/dev/null | jq -r '.BackendState')
    case "$STATUS" in
        "Running") echo "connected" ;;
        "Stopped"|"NeedsLogin") echo "disconnected" ;;
        *) echo "unknown" ;;
    esac
}

# Leggi stato precedente
PREV_STATE=""
if [ -f "$STATE_FILE" ]; then
    PREV_STATE=$(cat "$STATE_FILE")
fi

# Ottieni stato attuale
CURR_STATE=$(get_status)

# Se lo stato è cambiato, invia notifica
if [ "$PREV_STATE" != "$CURR_STATE" ] && [ -n "$PREV_STATE" ]; then
    case "$CURR_STATE" in
        "connected")
            notify-send -a "Tailscale" "Connected" "Tailscale VPN active"
            ;;
        "disconnected")
            notify-send -a "Tailscale" "Disconnected" "Tailscale VPN inactive"
            ;;
        "disabled")
            notify-send -a "Tailscale" "Service disabled" "tailscaled.service is not running"
            ;;
    esac
fi

# Salva stato corrente
echo "$CURR_STATE" > "$STATE_FILE"
