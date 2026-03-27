#!/bin/sh

notify() {
    notify-send -a "ProtonVPN" "$1" "$2"
}

is_connected() {
    ip addr show proton0 2>/dev/null | grep -q "inet"
}

if is_connected; then
    CHOICE=$(printf "Disconnect\nOpen Status" | wofi --dmenu --prompt "ProtonVPN Connected")

    if [ "$CHOICE" = "Disconnect" ]; then
        protonvpn disconnect
        if [ $? -eq 0 ]; then
            notify "Disconnected" "VPN has been disconnected"
            pkill -RTMIN+8 waybar
        else
            notify "Error" "Failed to disconnect VPN"
        fi
    elif [ "$CHOICE" = "Open Status" ]; then
        protonvpn info
    fi
else
    CHOICE=$(printf "Connect\nOpen Status" | wofi --dmenu --prompt "ProtonVPN Disconnected")

    case "$CHOICE" in
        "Connect")
            protonvpn connect
            notify "Connecting" "Connecting to fastest server..."
            sleep 2
            if is_connected; then
                notify "Connected" "Successfully connected to VPN"
            fi
            pkill -RTMIN+8 waybar
            ;;
        "Open Status")
            protonvpn info
            ;;
    esac
fi
