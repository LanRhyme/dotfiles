#!/usr/bin/env bash
# 从上游 Antigravity-Star-Suite 源码重新生成猫娘帧图（美术资源不入 dotfiles）
# 用法: build-assets.sh [上游仓库路径]
set -euo pipefail
UPSTREAM="${1:-$HOME/.local/share/antigravity-star-suite}"
SRC="$UPSTREAM/Antigravity-Cat-Widget/assets"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
[[ -d "$SRC" ]] || { echo "找不到上游资源: $SRC" >&2; exit 1; }
command -v magick >/dev/null || { echo "需要 ImageMagick (magick)" >&2; exit 1; }
mkdir -p "$HERE/assets/frames"
magick "$SRC/character-packs/gemini-star-v1/frames/idle.png"     -resize 420x -strip -define webp:method=6 "$HERE/assets/frames/idle.webp"
magick "$SRC/character-packs/gemini-star-v1/frames/blink.png"    -resize 420x -strip -define webp:method=6 "$HERE/assets/frames/blink.webp"
magick "$SRC/character-packs/gemini-star-v1/frames/proud-v3.png" -resize 420x -strip -define webp:method=6 "$HERE/assets/frames/proud.webp"
magick "$SRC/character-packs/gemini-star-v1/frames/sad-v3.png"   -resize 420x -strip -define webp:method=6 "$HERE/assets/frames/sad.webp"
cp "$SRC/dialogue/zh-CN.json" "$HERE/assets/dialogue.json"
echo "已生成: $(ls "$HERE/assets/frames" | tr '\n' ' ')"
