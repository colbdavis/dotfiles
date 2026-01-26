#!/bin/sh

NETWORK="docker_ai_net"
STATE_FILE="$HOME/.cache/docker_ai_net.state"

running=$(docker ps --filter "network=$NETWORK" --format '{{.Names}}' | wc -l)

if [ "$running" -gt 0 ]; then
  current_state="running"
else
  current_state="stopped"
fi

# Stato precedente
if [ -f "$STATE_FILE" ]; then
  previous_state=$(cat "$STATE_FILE")
else
  previous_state="unknown"
fi

# Notifica solo se cambia
if [ "$current_state" != "$previous_state" ]; then
  if [ "$current_state" = "running" ]; then
    notify-send "AI Servers" "Servers started" -i network-server
  else
    notify-send "AI Servers" "Servers stopped" -i network-offline
  fi
  echo "$current_state" > "$STATE_FILE"
fi

# Output per Waybar
if [ "$current_state" = "running" ]; then
  echo '{"text":"󰒋 AI","class":"running","tooltip":"AI servers active ($running)"}'
else
  echo '{"text":"󰒋 AI","class":"stopped","tooltip":"AI servers stopped"}'
fi
