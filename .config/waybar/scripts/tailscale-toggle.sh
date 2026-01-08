#!/bin/sh

notify() {
    notify-send -a "Tailscale" "$1" "$2"
}

if ! systemctl is-active --quiet tailscaled.service; then
    notify "Error" "The tailscale service isn't active"
    exit 1
fi

STATUS=$(tailscale status --json 2>/dev/null | jq -r '.BackendState')

if [ "$STATUS" = "Running" ]; then
    CHOICE=$(printf "Yes\nNo" | wofi --dmenu --prompt "Disconnect Tailscale?")
    
    if [ "$CHOICE" = "Yes" ]; then
        sudo tailscale down
        if [ $? -eq 0 ]; then
            notify "Tailscale" "Disconnected"
            pkill -RTMIN+8 waybar
        else
            notify "Error" "Impossible to disconnect"
        fi
    fi
else
    CHOICE=$(printf "Yes\nNo" | wofi --dmenu --prompt "Connect Tailscale?")
    
    if [ "$CHOICE" = "Yes" ]; then
        sudo tailscale up
        if [ $? -eq 0 ]; then
            notify "Tailscale" "Connected"
            pkill -RTMIN+8 waybar
        else
            notify "Error" "Impossible to connect"
        fi
    fi
fi