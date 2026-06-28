#!/bin/bash
# Apply Morandi palette from Noctalia wallpaper colors
# Called by noctalia's wallpaperChange hook

python3 ~/.config/noctalia/morandi-gen.py

# Reload niri config
niri msg action reload-config 2>/dev/null

# Restart fcitx5 to pick up new theme (themes require full restart)
if pgrep -x fcitx5 > /dev/null; then
    kill $(pgrep -x fcitx5)
    sleep 0.3
fi
fcitx5 &
disown
