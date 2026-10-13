#!/bin/bash

# Soglie
WARNING_BATTERY=30
CRITICAL_BATTERY=10

# File temporaneo per tracciare lo stato precedente
STATE_FILE="/tmp/battery_state_prev"

# Leggi lo stato della batteria
BAT_PERCENT=$(cat /sys/class/power_supply/BAT*/capacity 2>/dev/null || acpi -b | awk '{print $4}' | tr -d '%')
BAT_STATUS=$(cat /sys/class/power_supply/BAT*/status 2>/dev/null || acpi -b | awk '{print $3}' | tr -d ',')

# Nerd Font icone batteria (U+F244..U+F240)
BAT_ICONS=($'\uf244' $'\uf243' $'\uf242' $'\uf241' $'\uf240')
BAT_ICON_INDEX=$(( (BAT_PERCENT * (${#BAT_ICONS[@]} - 1) + 99) / 100 ))
BAT_ICON="${BAT_ICONS[$BAT_ICON_INDEX]}"

BOLT=$'\uf0e7'
PLUG=$'\uf1e6'

# Formatta il testo
if [[ "$BAT_STATUS" == "Charging" || "$BAT_STATUS" == "Full" ]]; then
    FORMAT="$BOLT $BAT_PERCENT%"
    TOOLTIP="Charging: $BAT_PERCENT%"
elif [[ "$BAT_STATUS" == "Discharging" ]]; then
    FORMAT="$BAT_ICON $BAT_PERCENT%"
    TOOLTIP="Battery: $BAT_PERCENT%"
else
    FORMAT="$PLUG $BAT_PERCENT%"
    TOOLTIP="External power: $BAT_PERCENT%"
fi

# Notifiche
PREV_STATE=""
if [ -f "$STATE_FILE" ]; then
    PREV_STATE=$(cat "$STATE_FILE")
fi

# Notifica solo quando la batteria è in scarica.
if [[ "$BAT_STATUS" != "Discharging" ]]; then
    echo "" > "$STATE_FILE"
# Notifica sotto il 30%
elif [ "$BAT_PERCENT" -le "$WARNING_BATTERY" ] && [ "$BAT_PERCENT" -gt "$CRITICAL_BATTERY" ]; then
    if [ "$PREV_STATE" != "$BAT_PERCENT" ]; then
        notify-send -u critical "Low Battery" "$BAT_PERCENT% lasting!"
        echo "$BAT_PERCENT" > "$STATE_FILE"
    fi
# Spegnimento al 10%
elif [ "$BAT_PERCENT" -le "$CRITICAL_BATTERY" ]; then
    if [ "$PREV_STATE" != "critical" ]; then
        notify-send -u critical "Batteria critica" "Batteria al $BAT_PERCENT%! Spegnimento in 30 secondi..."
        echo "critical" > "$STATE_FILE"
        sleep 30
        # Non spegnere se nel frattempo è stato collegato il caricatore.
        BAT_STATUS=$(cat /sys/class/power_supply/BAT*/status 2>/dev/null || acpi -b | awk '{print $3}' | tr -d ',')
        if [[ "$BAT_STATUS" == "Discharging" ]]; then
            systemctl poweroff
        fi
    fi
else
    echo "" > "$STATE_FILE"
fi

# Output JSON per Waybar
echo "{\"text\": \"$FORMAT\", \"tooltip\": \"$TOOLTIP\", \"class\": \"$BAT_STATUS\"}"
