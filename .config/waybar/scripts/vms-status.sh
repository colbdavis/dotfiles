#!/bin/bash

# Temp file to save state
STATE_FILE="/tmp/vm_status_prev"

# Counts vms in execution
RUNNING_VMS=$(virsh -c qemu:///system list --state-running --name | grep -v "^$" | wc -l)

if [ "$RUNNING_VMS" -gt 0 ]; then
    TEXT="$RUNNING_VMS"
    CLASS="running"
else
    TEXT="OFF"
    CLASS="stopped"
fi

PREV_STATE=""
if [ -f "$STATE_FILE" ]; then
    PREV_STATE=$(cat "$STATE_FILE")
fi

# Send notification only if state changed
if [ "$CLASS" != "$PREV_STATE" ]; then
    if [ "$CLASS" = "running" ]; then
        notify-send "active VMs" "$RUNNING_VMS VM in execution"
    else
        notify-send "VMs off" "No active VM"
    fi
    echo "$CLASS" > "$STATE_FILE"
fi

# Output JSON per Waybar
echo "{\"text\": \"$TEXT\", \"class\": \"$CLASS\", \"tooltip\": \"active VMs: $RUNNING_VMS\"}"
