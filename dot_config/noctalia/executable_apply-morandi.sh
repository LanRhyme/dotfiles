#!/bin/bash
# Apply Morandi palette from Noctalia wallpaper colors
# Called by noctalia's wallpaperChange hook

WALLPAPER_PATH=$(noctalia msg wallpaper-get 2>/dev/null)
if [ -n "$WALLPAPER_PATH" ] && [ -f "$WALLPAPER_PATH" ]; then
    noctalia theme "$WALLPAPER_PATH" --scheme muted -o ~/.config/noctalia/colors.json
fi

python3 ~/.config/noctalia/morandi-gen.py

# Reload niri config
niri msg action load-config-file 2>/dev/null

# Sync blurred wallpaper to Limine bootloader background (PNG format)
EFI_DIR="/boot/efi"
if [ -n "$WALLPAPER_PATH" ] && [ -f "$WALLPAPER_PATH" ]; then
    sudo magick "$WALLPAPER_PATH" -blur 0x12 -resize 1920x1080\! -quality 95 "$EFI_DIR/limine_bg.png" 2>/dev/null
fi

# Restart fcitx5 to pick up new theme (themes require full restart)
if pgrep -x fcitx5 > /dev/null; then
    kill $(pgrep -x fcitx5)
    sleep 0.3
fi
fcitx5 &
disown
