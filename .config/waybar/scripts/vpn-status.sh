#!/bin/sh

if ip addr show proton0 2>/dev/null | grep -q "inet"; then
    echo "{\"text\": \"  VPN\", \"class\": \"connected\", \"tooltip\": \"Connected to ProtonVPN\"}"
else
    echo "{\"text\": \"  VPN\", \"class\": \"disconnected\", \"tooltip\": \"VPN Disconnected\nClick to connect\"}"
fi
