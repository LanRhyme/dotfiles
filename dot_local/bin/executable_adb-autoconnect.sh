#!/usr/bin/env bash
# ADB Auto-Connect daemon over Tailscale for K60 and OnePlus Pad

DEVICES=(
    "100.127.72.106:5555" # Redmi K60
    "100.107.36.2:5555"   # OnePlus Pad 2 Pro
)

connect_device() {
    local target="$1"
    local host="${target%:*}"
    local port="${target#*:}"

    # Check if device is already connected and recognized by adb
    if adb devices 2>/dev/null | grep -q "^${target}[[:space:]]\+device"; then
        return 0
    fi

    # Probe port accessibility before running adb connect to avoid blocking
    if nc -z -w 2 "$host" "$port" >/dev/null 2>&1; then
        adb connect "$target" >/dev/null 2>&1
    fi
}

main() {
    while true; do
        for dev in "${DEVICES[@]}"; do
            connect_device "$dev"
        done
        sleep 10
    done
}

main
