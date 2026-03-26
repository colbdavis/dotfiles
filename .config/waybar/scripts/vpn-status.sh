#!/usr/bin/env bash

if ip link show wg0 &>/dev/null && ip addr show wg0 | grep -q "inet"; then
    echo "{\"text\": \"🔒 VPN\", \"class\": \"connected\", \"tooltip\": \"Connected to ProtonVPN\"}"
else
    echo "{\"text\": \"🔓 VPN\", \"class\": \"disconnected\", \"tooltip\": \"VPN Disconnected\\nClick to connect\"}"
fi
