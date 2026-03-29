#!/bin/sh

notify() {
    notify-send -a "Localsend" "$1" "$2"
}

if pgrep -x localsend > /dev/null 2>&1; then
    CHOICE=$(printf "Open UI\nDisable Localsend" | wofi --dmenu --prompt "Localsend active")

    if [ "$CHOICE" = "Open UI" ]; then
        localsend &
    elif [ "$CHOICE" = "Disable Localsend" ]; then
        pkill -x localsend
        notify "Disabled" "Localsend stopped"
        sleep 0.5
    fi
else
    CHOICE=$(printf "Enable Localsend" | wofi --dmenu --prompt "Localsend inactive")

    if [ "$CHOICE" = "Enable Localsend" ]; then
        nohup localsend > /dev/null 2>&1 &
        notify "Enabled" "Localsend started"
        sleep 1
    fi
fi

pkill -RTMIN+8 waybar
