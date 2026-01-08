#!/bin/sh

# Created by cbd as a wofi alternative to default firefox/librefox profile switcher
CHOICE=$(printf "Proprietary\nNo" | wofi --dmenu --prompt "Choose profiles: ")
    
if [ "$CHOICE" = "Proprietary" ]; then
	io.gitlab.librewolf-community -P Proprietary
fi
