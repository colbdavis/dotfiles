#!/bin/sh

if pgrep -x localsend > /dev/null 2>&1; then
    echo '{"text": "", "tooltip": "Localsend: active", "class": "active"}'
else
    echo '{"text": "", "tooltip": "Localsend: inactive", "class": "inactive"}'
fi
