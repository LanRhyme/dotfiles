#!/usr/bin/env python3
"""Generate KDE color scheme from Noctalia morandi palette."""

import json
import sys
import subprocess
from pathlib import Path

COLORS_JSON = Path.home() / ".config/noctalia/colors.json"
OUTPUT = Path.home() / ".local/share/color-schemes/Morandi-dark.colors"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_str(c: tuple[int, int, int]) -> str:
    return f"{c[0]},{c[1]},{c[2]}"


def main():
    if not COLORS_JSON.exists():
        print(f"Error: {COLORS_JSON} not found", file=sys.stderr)
        sys.exit(1)

    with open(COLORS_JSON) as f:
        colors = json.load(f)

    bg = hex_to_rgb(colors["background"])
    surface = hex_to_rgb(colors["surface_container"])
    surface_var = hex_to_rgb(colors["surface_variant"])
    primary = hex_to_rgb(colors["primary"])
    primary_cont = hex_to_rgb(colors["primary_container"])
    on_surface = hex_to_rgb(colors["on_surface"])
    on_surface_var = hex_to_rgb(colors["on_surface_variant"])
    on_primary = hex_to_rgb(colors["on_primary"])
    error = hex_to_rgb(colors["error"])
    outline = hex_to_rgb(colors["outline"])
    window_bg = hex_to_rgb(colors["surface_container_low"])

    content = f"""[General]
Name=Morandi Dark
Name[zh_CN]=莫兰迪暗色
shadeSortColumn=true

[ColorEffects:Disabled]
Color=56,55,50
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundNormal={rgb_str(surface)}
BackgroundAlternate={rgb_str(surface)}
ForegroundNormal={rgb_str(on_surface)}
ForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}
ForegroundLink={rgb_str(primary)}
ForegroundNegative={rgb_str(error)}
ForegroundNeutral={rgb_str(primary)}
ForegroundPositive={rgb_str(primary)}
ForegroundVisited={rgb_str(primary)}
DecorationFocus={rgb_str(primary_cont)}
DecorationHover={rgb_str(primary)}

[Colors:Selection]
BackgroundNormal={rgb_str(primary_cont)}
BackgroundAlternate={rgb_str(primary_cont)}
ForegroundNormal={rgb_str(on_primary)}
ForegroundInactive={rgb_str(on_primary)}
ForegroundActive={rgb_str(on_primary)}
ForegroundLink={rgb_str(on_primary)}
ForegroundNegative={rgb_str(error)}
ForegroundNeutral={rgb_str(on_primary)}
ForegroundPositive={rgb_str(on_primary)}
ForegroundVisited={rgb_str(on_primary)}
DecorationFocus={rgb_str(primary_cont)}
DecorationHover={rgb_str(primary)}

[Colors:Tooltip]
BackgroundNormal={rgb_str(surface)}
BackgroundAlternate={rgb_str(surface)}
ForegroundNormal={rgb_str(on_surface)}
ForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}
ForegroundLink={rgb_str(primary)}
ForegroundNegative={rgb_str(error)}
ForegroundNeutral={rgb_str(primary)}
ForegroundPositive={rgb_str(primary)}
ForegroundVisited={rgb_str(primary)}
DecorationFocus={rgb_str(primary_cont)}
DecorationHover={rgb_str(primary)}

[Colors:View]
BackgroundNormal={rgb_str(bg)}
BackgroundAlternate={rgb_str(surface_var)}
ForegroundNormal={rgb_str(on_surface)}
ForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}
ForegroundLink={rgb_str(primary)}
ForegroundNegative={rgb_str(error)}
ForegroundNeutral={rgb_str(primary)}
ForegroundPositive={rgb_str(primary)}
ForegroundVisited={rgb_str(primary)}
DecorationFocus={rgb_str(primary_cont)}
DecorationHover={rgb_str(primary)}

[Colors:Window]
BackgroundNormal={rgb_str(window_bg)}
BackgroundAlternate={rgb_str(window_bg)}
ForegroundNormal={rgb_str(on_surface)}
ForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}
ForegroundLink={rgb_str(primary)}
ForegroundNegative={rgb_str(error)}
ForegroundNeutral={rgb_str(primary)}
ForegroundPositive={rgb_str(primary)}
ForegroundVisited={rgb_str(primary)}
DecorationFocus={rgb_str(primary_cont)}
DecorationHover={rgb_str(primary)}

[WM]
activeBackground={rgb_str(surface)}
activeBlend={rgb_str(surface)}
activeForeground={rgb_str(on_surface)}
inactiveBackground={rgb_str(bg)}
inactiveBlend={rgb_str(bg)}
inactiveForeground={rgb_str(on_surface_var)}
activeTitleBtnBg={rgb_str(primary_cont)}
inactiveTitleBtnBg={rgb_str(surface)}
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content)
    print(f"Wrote KDE color scheme to {OUTPUT}")


if __name__ == "__main__":
    main()
