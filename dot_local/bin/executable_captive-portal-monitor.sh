#!/bin/bash
# Captive portal detection and notification
# Wrapper executing Python monitor with native libnm bindings
exec /usr/bin/python3 "$HOME/.local/bin/captive-portal-monitor.py" "$@"
