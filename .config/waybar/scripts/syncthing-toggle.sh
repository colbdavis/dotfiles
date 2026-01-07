#!/bin/sh

notify() {
    notify-send -a "Syncthing" "$1" "$2"
}

if pgrep -x syncthing > /dev/null 2>&1; then
    # Syncthing è attivo
    CHOICE=$(printf "Aprire Browser\nDisattivare Syncthing" | wofi --dmenu --prompt "Syncthing attivo")
    
    if [ "$CHOICE" = "Aprire Browser" ]; then
        io.gitlab.librewolf-community http://127.0.0.1:8384/ -p PAOLO &
    elif [ "$CHOICE" = "Disattivare Syncthing" ]; then
        pkill -x syncthing
        notify "Disattivato" "Disattivato processo syncthing"
        sleep 0.5
    fi
else
    # Syncthing non è attivo
    CHOICE=$(printf "Aprire Browser\nAttivare Syncthing" | wofi --dmenu --prompt "Syncthing inattivo")
    
    if [ "$CHOICE" = "Aprire Browser" ]; then
        io.gitlab.librewolf-community http://127.0.0.1:8384/ -p PAOLO &
    elif [ "$CHOICE" = "Attivare Syncthing" ]; then
        nohup syncthing --no-browser > /dev/null 2>&1 &
        notify "Attivazione" "Avvio processo syncthing..."
        sleep 1
    fi
fi

# Aggiorna waybar
pkill -RTMIN+8 waybar
