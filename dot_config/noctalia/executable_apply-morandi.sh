#!/bin/bash
# Apply Morandi palette from Noctalia wallpaper colors
# Called by noctalia's wallpaperChange hook

python3 ~/.config/noctalia/morandi-gen.py

# Reload niri config
niri msg action reload-config 2>/dev/null

# Sync blurred wallpaper to Limine bootloader background (PNG format)
WALLPAPER_DIR="/home/lanrhyme/图片/WallPapers"
EFI_DIR="/boot/efi"
CURRENT=$(ls -t "$WALLPAPER_DIR"/*.{jpg,png} 2>/dev/null | head -1)
if [ -n "$CURRENT" ]; then
    sudo magick "$CURRENT" -blur 0x12 -resize 1920x1080\! -quality 95 "$EFI_DIR/limine_bg.png" 2>/dev/null
fi

# Restart fcitx5 to pick up new theme (themes require full restart)
if pgrep -x fcitx5 > /dev/null; then
    kill $(pgrep -x fcitx5)
    sleep 0.3
fi
fcitx5 &
disown
