#!/bin/sh

notify() {
    notify-send -a "Syncthing" "$1" "$2"
}

if pgrep -x syncthing > /dev/null 2>&1; then
    # Syncthing è attivo
    CHOICE=$(printf "Open Browser\nDisable Syncthing" | wofi --dmenu --prompt "Syncthing active")

    if [ "$CHOICE" = "Open Browser" ]; then
        io.gitlab.librewolf-community http://127.0.0.1:8384/ -p PAOLO &
    elif [ "$CHOICE" = "Disable Syncthing" ]; then
        pkill -x syncthing
        notify "Disabled" "Disabled syncthing process"
        sleep 0.5
    fi
else
    # Syncthing non è attivo
    CHOICE=$(printf "Open Browser\nEnable Syncthing" | wofi --dmenu --prompt "Syncthing inactive")

    if [ "$CHOICE" = "Open Browser" ]; then
        io.gitlab.librewolf-community http://127.0.0.1:8384/ -p PAOLO &
    elif [ "$CHOICE" = "Enable Syncthing" ]; then
        nohup syncthing --no-browser > /dev/null 2>&1 &
        notify "Activation" "Starting syncthing process..."
        sleep 1
    fi
fi

# Aggiorna waybar
pkill -RTMIN+8 waybar
