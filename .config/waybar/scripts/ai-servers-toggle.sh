#!/bin/sh

NETWORK="docker_ai_net"
COMPOSE_DIR="$HOME/docker"   # directory dove c’è il docker-compose.yml

running=$(docker ps --filter "network=$NETWORK" --format '{{.Names}}' | wc -l)

if [ "$running" -gt 0 ]; then
  choice=$(printf "No\nYes" | wofi --dmenu -p "Turn off AI servers?")
  if [ "$choice" = "Yes" ]; then
    cd "$COMPOSE_DIR" && docker compose stop
    notify-send "AI Servers" "Servers stopped"
  fi
else
  choice=$(printf "No\nYes" | wofi --dmenu -p "Start AI servers?")
  if [ "$choice" = "Yes" ]; then
    cd "$COMPOSE_DIR" && docker compose start
    notify-send "AI Servers" "Servers started"
  fi
fi
