#!/bin/bash

notify() {
    notify-send -a "Tailscale" "$1" "$2"
}

if ! systemctl is-active --quiet tailscaled.service; then
    notify "Errore" "Il servizio tailscaled non è attivo"
    exit 1
fi

STATUS=$(tailscale status --json 2>/dev/null | jq -r '.BackendState')

if [ "$STATUS" = "Running" ]; then
    CHOICE=$(printf "Sì\nNo" | wofi --dmenu --prompt "Disconnettere Tailscale?")
    
    if [ "$CHOICE" = "Sì" ]; then
        sudo tailscale down
        if [ $? -eq 0 ]; then
            notify "Tailscale" "Disconnesso"
            pkill -RTMIN+8 waybar
        else
            notify "Errore" "Impossibile disconnettere"
        fi
    fi
else
    CHOICE=$(printf "Sì\nNo" | wofi --dmenu --prompt "Connettere Tailscale?")
    
    if [ "$CHOICE" = "Sì" ]; then
        sudo tailscale up
        if [ $? -eq 0 ]; then
            notify "Tailscale" "Connesso"
            pkill -RTMIN+8 waybar
        else
            notify "Errore" "Impossibile connettersi"
        fi
    fi
fi
