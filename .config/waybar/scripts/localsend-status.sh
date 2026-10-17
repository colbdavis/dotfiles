#!/bin/sh
# When LocalSend is active, only its tray icon is used.
if pgrep -x localsend > /dev/null 2>&1; then
    printf '%s\n' '{"text":"","tooltip":"LocalSend running in the system tray","class":"active"}'
else
    printf '%s\n' '{"text":"󰒍","tooltip":"LocalSend: launch","class":"inactive"}'
fi
