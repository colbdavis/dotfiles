#!/bin/bash

# File temporaneo per salvare lo stato precedente
STATE_FILE="/tmp/vm_status_prev"

# Conta le VM in esecuzione
RUNNING_VMS=$(virsh -c qemu:///system list --state-running --name | grep -v "^$" | wc -l)

# Determina testo e classe
if [ "$RUNNING_VMS" -gt 0 ]; then
    TEXT="$RUNNING_VMS"
    CLASS="running"
else
    TEXT="OFF"
    CLASS="stopped"
fi

# Leggi stato precedente
PREV_STATE=""
if [ -f "$STATE_FILE" ]; then
    PREV_STATE=$(cat "$STATE_FILE")
fi

# Invia notifica solo se lo stato è cambiato
if [ "$CLASS" != "$PREV_STATE" ]; then
    if [ "$CLASS" = "running" ]; then
        notify-send "VM attive" "$RUNNING_VMS VM in esecuzione"
    else
        notify-send "VM spente" "Nessuna VM attiva"
    fi
    echo "$CLASS" > "$STATE_FILE"
fi

# Output JSON per Waybar
echo "{\"text\": \"$TEXT\", \"class\": \"$CLASS\", \"tooltip\": \"VM attive: $RUNNING_VMS\"}"
