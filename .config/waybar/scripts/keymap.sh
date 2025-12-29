#!/bin/sh

get_layout() {
    hyprctl devices -j \
    | jq -r '.keyboards[].active_keymap' \
    | head -n1 \
    | grep -qi italian && echo "it" || echo "us"
}

if [[ "$1" == "toggle" ]]; then
    CURRENT=$(get_layout)
    if [[ "$CURRENT" == "it" ]]; then
        hyprctl keyword input:kb_layout us
        notify-send "Keyboard layout" "US 🇺🇸" -t 1200
    else
        hyprctl keyword input:kb_layout it
        notify-send "Keyboard layout" "IT 🇮🇹" -t 1200
    fi
fi

get_layout

