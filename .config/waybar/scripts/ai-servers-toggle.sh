#!/bin/sh

NETWORK="docker_ai_net"
COMPOSE_DIR="$HOME/docker"   # directory dove c’è il docker-compose.yml

running=$(docker ps --filter "network=$NETWORK" --format '{{.Names}}' | wc -l)

if [ "$running" -gt 0 ]; then
  choice=$(printf "No\nYes" | wofi --dmenu -p "Spegnere AI servers?")
  if [ "$choice" = "Yes" ]; then
    cd "$COMPOSE_DIR" && docker compose stop
    notify-send "AI Servers" "Server fermati"
  fi
else
  choice=$(printf "No\nYes" | wofi --dmenu -p "Avviare AI servers?")
  if [ "$choice" = "Yes" ]; then
    cd "$COMPOSE_DIR" && docker compose start
    notify-send "AI Servers" "Server avviati"
  fi
fi
