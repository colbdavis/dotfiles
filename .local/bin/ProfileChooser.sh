#!/bin/sh

# Created by cbd as a wofi alternative to default firefox/librefox profile switcher
CHOICE=$(printf "Proprietary\nAI\nFoss\nGit\nOther" | wofi --dmenu --prompt "Choose profiles: ")

case $CHOICE in
Proprietary)
	io.gitlab.librewolf-community -P Proprietary;;
AI)
	io.gitlab.librewolf-community -P AI;;
Foss)
	io.gitlab.librewolf-community -P Foss;;
Git)
	io.gitlab.librewolf-community -P Git;;
Other)
	io.gitlab.librewolf-community --ProfileManager;;
*)
esac