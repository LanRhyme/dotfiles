#!/usr/bin/env python3
"""Generate Morandi-style color palette from Noctalia's Material You colors and apply to system."""

import json
import colorsys
import os
import re
import sys
import subprocess
import argparse
from pathlib import Path

NOCTALIA_COLORS = Path.home() / ".config/noctalia/colors.json"
NIRI_COLORS_KDL = Path.home() / ".config/niri/cfg/colors.kdl"
MANGO_CONFIG = Path.home() / ".config/mango/config.conf"
STARSHIP_TOML = Path.home() / ".config/starship.toml"
FCITX5_THEME = Path.home() / ".local/share/fcitx5/themes/bamboo-dark/theme.conf"
FASTFETCH_CONFIG = Path.home() / ".config/fastfetch/config.jsonc"
ALACRITTY_TOML = Path.home() / ".config/alacritty/alacritty.toml"
KDE_OUTPUT = Path.home() / ".local/share/color-schemes/Morandi-dark.colors"

def hex_to_hsl(hex_color):
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100

def hsl_to_hex(h, s, l):
    h = h % 360
    s = max(0, min(100, s)) / 100
    l = max(0, min(100, l)) / 100
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def morandi(hex_color, sat_reduction=0.3, light_adjust=0, warm_shift=0, sat_cap=45):
    h, s, l = hex_to_hsl(hex_color)
    s = s * (1 - sat_reduction)
    h = (h + warm_shift) % 360
    l = max(0, min(100, l + light_adjust))
    s = min(s, sat_cap)
    return hsl_to_hex(h, s, l)

def blend(c1, c2, ratio=0.5):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_palette(c):
    p = {}
    primary = c.get("mPrimary", c.get("primary"))
    secondary = c.get("mSecondary", c.get("secondary"))
    tertiary = c.get("mTertiary", c.get("tertiary"))
    error = c.get("mError", c.get("error"))
    surface = c.get("mSurface", c.get("surface"))
    on_surface = c.get("mOnSurface", c.get("on_surface"))
    surface_var = c.get("mSurfaceVariant", c.get("surface_variant"))
    outline = c.get("mOutline", c.get("outline"))

    p["base"] = morandi(surface, 0.5, -2)
    p["mantle"] = morandi(surface, 0.6, -5)
    p["surface0"] = morandi(surface_var, 0.4, 2)
    p["surface1"] = morandi(surface_var, 0.3, 5)
    p["surface2"] = morandi(surface_var, 0.2, 8)
    p["overlay0"] = morandi(outline, 0.3, -2)
    p["overlay1"] = morandi(outline, 0.2, 2)
    p["overlay2"] = morandi(outline, 0.1, 5)
    p["subtext0"] = morandi(on_surface, 0.4, -8)
    p["subtext1"] = morandi(on_surface, 0.3, -4)
    p["text"] = morandi(on_surface, 0.2, 0)
    p["love"] = morandi(error, 0.25, -15)
    p["rose"] = morandi(blend(primary, error, 0.6), 0.3, -15, 5)
    p["gold"] = morandi(blend(primary, "#d4a574", 0.3), 0.35, -10, 15)
    p["peach"] = morandi(blend(error, "#d4a574", 0.4), 0.3, -10, 10)
    p["pine"] = morandi(tertiary, 0.3, -18, -5)
    p["foam"] = morandi(secondary, 0.35, -18, -5)
    p["iris"] = morandi(primary, 0.25, -18)
    p["sky"] = morandi(tertiary, 0.35, -18, -10)

    h, s, l = hex_to_hsl(p["surface1"])
    p["fcitx5_bg"] = hsl_to_hex(h, s * 0.6, min(l, 20))
    p["fcitx5_bg_alt"] = hsl_to_hex(h, s * 0.5, min(l + 3, 22))
    ih, is_, il = hex_to_hsl(p["iris"])
    p["fcitx5_hl_bg"] = hsl_to_hex(ih, is_, min(il, 38))
    p["fcitx5_text"] = p["text"]
    p["fcitx5_hl_text"] = p["base"]
    # Normal terminal colors
    p["term_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.5, -15)
    p["term_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.5, -15)
    p["term_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.5, -15)
    p["term_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.5, -15)
    p["term_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.5, -15)
    p["term_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.5, -15)

    # Bright terminal colors (slightly higher lightness, slightly higher saturation)
    p["term_bright_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.45, -12)
    p["term_bright_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.45, -12)
    p["term_bright_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.45, -12)
    p["term_bright_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.45, -12)
    p["term_bright_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.45, -12)
    p["term_bright_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.45, -12)

    # Dim terminal colors (lower lightness, lower saturation)
    p["term_dim_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.55, -18)
    p["term_dim_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.55, -18)
    p["term_dim_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.55, -18)
    p["term_dim_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.55, -18)
    p["term_dim_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.55, -18)
    p["term_dim_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.55, -18)

    # Terminal background: tinted slightly with primary theme color
    h_p, s_p, _ = hex_to_hsl(primary)
    h_b, s_b, l_b = hex_to_hsl(p["base"])
    p["term_bg"] = hsl_to_hex(h_p, min(s_b + 4, 18), l_b + 1)

    return p

def write_ly(palette):
    config_path = Path("/etc/ly/config.ini")
    startup_path = Path("/etc/ly/startup.sh")
    
    if config_path.exists():
        try:
            content = config_path.read_text()
            replacements = {
                "bg": "0x00000000",
                "fg": "0x0008",
                "border_fg": "0x0005",
                "error_bg": "0x00000000",
                "error_fg": "0x0002",
                "full_color": "false"
            }
            for k, v in replacements.items():
                content = re.sub(rf"^{k}\s*=.*", f"{k} = {v}", content, flags=re.MULTILINE)
            content = re.sub(r"^animation\s*=.*", "animation = none", content, flags=re.MULTILINE)
            config_path.write_text(content)
        except Exception as e:
            print(f"Failed to write ly config: {e}")
            
    if startup_path.exists():
        try:
            def c(hex_val): return hex_val.lstrip("#").lower()
            
            script = f'''#!/bin/sh
# Auto-generated by morandi-gen.py
if [ "$TERM" = "linux" ]; then
    printf "\\033]P0%s" "{c(palette['base'])}"
    printf "\\033]P1%s" "{c(palette['term_red'])}"
    printf "\\033]P2%s" "{c(palette['term_green'])}"
    printf "\\033]P3%s" "{c(palette['term_yellow'])}"
    printf "\\033]P4%s" "{c(palette['term_blue'])}"
    printf "\\033]P5%s" "{c(palette['term_magenta'])}"
    printf "\\033]P6%s" "{c(palette['term_cyan'])}"
    printf "\\033]P7%s" "{c(palette['text'])}"
    printf "\\033]P8%s" "{c(palette['surface2'])}"
    printf "\\033]P9%s" "{c(palette['term_bright_red'])}"
    printf "\\033]Pa%s" "{c(palette['term_bright_green'])}"
    printf "\\033]Pb%s" "{c(palette['term_bright_yellow'])}"
    printf "\\033]Pc%s" "{c(palette['term_bright_blue'])}"
    printf "\\033]Pd%s" "{c(palette['term_bright_magenta'])}"
    printf "\\033]Pe%s" "{c(palette['term_bright_cyan'])}"
    printf "\\033]Pf%s" "{c(palette['subtext0'])}"
    clear
fi
'''
            startup_path.write_text(script)
        except Exception as e:
            print(f"Failed to write ly startup.sh: {e}")

def write_antigravity(palette):
    agy_conf = Path.home() / ".gemini/antigravity-cli/settings.json"
    if not agy_conf.exists(): return
    try:
        import json
        content = json.loads(agy_conf.read_text())
        content["tuiStyle"] = "opencode"
        content["theme"] = {
            "primary": palette["primary"],
            "secondary": palette["term_magenta"],
            "accent": palette["term_yellow"],
            "error": palette["term_red"],
            "warning": palette["term_yellow"],
            "success": palette["term_green"],
            "info": palette["term_blue"],
            "text": palette["text"],
            "textMuted": palette["subtext0"],
            "background": "none",
            "backgroundPanel": palette["base"],
            "backgroundElement": "none",
            "border": palette["surface2"],
            "borderActive": palette["primary"],
            "borderSubtle": palette["surface"],
            "diffAdded": palette["term_green"],
            "diffRemoved": palette["term_red"],
            "diffContext": palette["subtext0"],
            "diffHunkHeader": palette["subtext0"],
            "diffHighlightAdded": palette["term_bright_green"],
            "diffHighlightRemoved": palette["term_bright_red"],
            "diffAddedBg": "none",
            "diffRemovedBg": "none",
            "diffContextBg": "none",
            "diffLineNumber": palette["surface2"],
            "diffAddedLineNumberBg": "none",
            "diffRemovedLineNumberBg": "none",
            "markdownText": palette["text"],
            "markdownHeading": palette["primary"],
            "markdownLink": palette["term_blue"],
            "markdownLinkText": palette["term_cyan"],
            "markdownCode": palette["term_green"],
            "markdownBlockQuote": palette["subtext0"],
            "markdownEmph": palette["term_yellow"],
            "markdownStrong": palette["primary"],
            "markdownHorizontalRule": palette["surface2"],
            "markdownListItem": palette["primary"],
            "markdownListEnumeration": palette["term_yellow"],
            "markdownImage": palette["term_blue"],
            "markdownImageText": palette["term_yellow"],
            "markdownCodeBlock": palette["text"],
            "syntaxComment": palette["subtext0"],
            "syntaxKeyword": palette["term_magenta"],
            "syntaxFunction": palette["term_blue"],
            "syntaxVariable": palette["text"],
            "syntaxString": palette["term_green"],
            "syntaxNumber": palette["term_yellow"],
            "syntaxType": palette["term_cyan"],
            "syntaxOperator": palette["term_cyan"],
            "syntaxPunctuation": palette["subtext0"]
        }
        agy_conf.write_text(json.dumps(content, indent=2))
    except Exception:
        pass

def write_opencode(palette):
    oc_theme = Path.home() / ".config/opencode/themes/transparent.json"
    if not oc_theme.exists(): return
    try:
        import json
        content = json.loads(oc_theme.read_text())
        content["theme"] = {
            "primary": palette["primary"],
            "secondary": palette["term_magenta"],
            "accent": palette["term_yellow"],
            "error": palette["term_red"],
            "warning": palette["term_yellow"],
            "success": palette["term_green"],
            "info": palette["term_blue"],
            "text": palette["text"],
            "textMuted": palette["subtext0"],
            "background": "none",
            "backgroundPanel": palette["base"],
            "backgroundElement": "none",
            "border": palette["surface2"],
            "borderActive": palette["primary"],
            "borderSubtle": palette["surface"],
            "diffAdded": palette["term_green"],
            "diffRemoved": palette["term_red"],
            "diffContext": palette["subtext0"],
            "diffHunkHeader": palette["subtext0"],
            "diffHighlightAdded": palette["term_bright_green"],
            "diffHighlightRemoved": palette["term_bright_red"],
            "diffAddedBg": "none",
            "diffRemovedBg": "none",
            "diffContextBg": "none",
            "diffLineNumber": palette["surface2"],
            "diffAddedLineNumberBg": "none",
            "diffRemovedLineNumberBg": "none",
            "markdownText": palette["text"],
            "markdownHeading": palette["primary"],
            "markdownLink": palette["term_blue"],
            "markdownLinkText": palette["term_cyan"],
            "markdownCode": palette["term_green"],
            "markdownBlockQuote": palette["subtext0"],
            "markdownEmph": palette["term_yellow"],
            "markdownStrong": palette["primary"],
            "markdownHorizontalRule": palette["surface2"],
            "markdownListItem": palette["primary"],
            "markdownListEnumeration": palette["term_yellow"],
            "markdownImage": palette["term_blue"],
            "markdownImageText": palette["term_yellow"],
            "markdownCodeBlock": palette["text"],
            "syntaxComment": palette["subtext0"],
            "syntaxKeyword": palette["term_magenta"],
            "syntaxFunction": palette["term_blue"],
            "syntaxVariable": palette["text"],
            "syntaxString": palette["term_green"],
            "syntaxNumber": palette["term_yellow"],
            "syntaxType": palette["term_cyan"],
            "syntaxOperator": palette["term_cyan"],
            "syntaxPunctuation": palette["subtext0"]
        }
        oc_theme.write_text(json.dumps(content, indent=2))
    except Exception:
        pass

def write_niri(palette):
    kdl = f"""// Auto-generated by morandi-gen.py — do not edit manually
layout {{
    focus-ring {{
        width 1
        active-gradient from="{palette['iris']}" to="{palette['pine']}" angle=45 relative-to="workspace-view"
        inactive-gradient from="{palette['surface0']}" to="{palette['surface1']}" angle=45 relative-to="workspace-view"
    }}
    border {{
        off
    }}
    shadow {{
        color "{palette['surface0']}70"
    }}
    tab-indicator {{
        active-color "{palette['iris']}"
        inactive-color "{palette['surface1']}"
        urgent-color "{palette['love']}"
    }}
    insert-hint {{
        color "{palette['iris']}80"
    }}
}}
recent-windows {{
    highlight {{
        active-color "{palette['iris']}"
        urgent-color "{palette['love']}"
    }}
}}
"""
    with open(NIRI_COLORS_KDL, "w") as f:
        f.write(kdl)

def write_mango(palette):
    if not MANGO_CONFIG.exists(): return
    content = MANGO_CONFIG.read_text()
    
    def c(hex_val, alpha="ff"):
        return "0x" + hex_val.lstrip("#").lower() + alpha
        
    replacements = {
        "focuscolor": c(palette["iris"]),
        "bordercolor": c(palette["surface1"]),
        "shadowscolor": c(palette["surface0"], "70"),
        "rootcolor": c(palette["base"]),
        "urgentcolor": c(palette["love"]),
        "overlaycolor": c(palette["iris"]),
        "scratchpadcolor": c(palette["foam"]),
    }
    
    for key, val in replacements.items():
        content = re.sub(fr"^{key}\s*=.*", f"{key}={val}", content, flags=re.MULTILINE)
        
    MANGO_CONFIG.write_text(content)

def write_starship(palette):
    if not STARSHIP_TOML.exists(): return
    with open(STARSHIP_TOML, "r") as f:
        content = f.read()
    keys = ["base", "mantle", "surface0", "surface1", "surface2", "overlay0", "overlay1", "overlay2", "subtext0", "subtext1", "text", "love", "gold", "peach", "rose", "pine", "foam", "iris", "sky"]
    new_palette = "[palettes.custom]\n" + "\n".join(f"{k} = '{palette[k]}'" for k in keys) + "\n"
    content, count = re.subn(r"\[palettes\.custom\][\s\S]*?(?=\n\[|\Z)", new_palette, content)
    if count == 0: content += "\n" + new_palette
    with open(STARSHIP_TOML, "w") as f:
        f.write(content)

def write_fcitx5(palette):
    theme_dir = FCITX5_THEME.parent
    theme_dir.mkdir(parents=True, exist_ok=True)
    tray_outline, tray_text = palette["surface0"], palette["text"]
    bg, hl = palette['fcitx5_bg'], palette['fcitx5_hl_bg']
    pine = palette.get('pine', '#a8aba0')
    bh, bs, bl = hex_to_hsl(bg)
    border = hsl_to_hex(bh, bs, min(bl + 5, 100))

    panel_svg = f'''<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="40" height="40" rx="8" fill="{bg}" fill-opacity="0.95"/>
<rect x="0.5" y="0.5" width="39" height="39" rx="8" stroke="{border}" stroke-opacity="1.0"/>
</svg>'''

    highlight_svg = f'''<svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M41 1V5.51948H36.5293V10.1667H41V31.8333H36.5293V36.8333H41V41H36.5293V36.8333H32.2V41H9.8V36.8333H5.21655V41H1V36.8333H5.21655V31.8333H1V10.1667H5.21655V5.51948H1V1H5.21655V5.51948H9.8V1H20.2H32.2V5.51948H36.5293V1H41Z" fill="{pine}" fill-opacity="0.2"/>
<path d="M5.21655 5.51948H1V1H5.21655V10.1667H1V31.8333H5.21655V41H1V36.8333H9.8V41H32.2V36.8333H41V41H36.5293V31.8333H41V10.1667H36.5293V1H41V5.51948H32.2V1H20.2H9.8V5.51948H5.21655Z" stroke="{pine}" stroke-width="2"/>
</svg>'''

    prev_svg = f'''<svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="32" height="32"><path d="M404.053333 534.613333a32 32 0 0 1 0-45.226666l213.333334-213.333334a32 32 0 1 1 45.226666 45.226667L471.893333 512l190.72 190.72a32 32 0 1 1-45.226666 45.226667l-213.333334-213.333334z" fill="{palette['subtext0']}"></path></svg>'''

    next_svg = f'''<svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="32" height="32"><path d="M672 512a32 32 0 0 1-9.386667 22.613333l-213.333333 213.333334a32 32 0 1 1-45.226667-45.226667L594.773333 512 404.053333 321.28a32 32 0 0 1 45.226667-45.226667l213.333333 213.333334c6.016 5.973333 9.386667 14.122667 9.386667 22.613333z" fill="{palette['subtext0']}"></path></svg>'''

    with open(theme_dir / "panel.svg", "w") as f: f.write(panel_svg)
    with open(theme_dir / "highlight.svg", "w") as f: f.write(highlight_svg)
    with open(theme_dir / "prev.svg", "w") as f: f.write(prev_svg)
    with open(theme_dir / "next.svg", "w") as f: f.write(next_svg)

    theme = f"""[Metadata]
Name=bamboo-dark
Version=0.0.1
Author=witt & morandi-gen
Description=古典竹简花纹 Morandi 主题

[InputPanel]
NormalColor={palette['fcitx5_text']}
HighlightColor={palette['fcitx5_hl_text']}
HighlightBackgroundColor={pine}
HighlightCandidateColor={pine}
EnableBlur=True
FullWidthHighlight=True
PageButtonAlignment=Bottom

[InputPanel/BlurMargin]
Left=2
Right=2
Top=2
Bottom=2

[InputPanel/Background]
Image=panel.svg
Color={bg}
BorderColor={border}
BorderWidth=0

[InputPanel/Background/Margin]
Left=12
Right=12
Top=12
Bottom=12

[InputPanel/Highlight]
Image=highlight.svg
Color={bg}
BorderColor={border}00
BorderWidth=0
Gravity="Top Left"

[InputPanel/Highlight/Margin]
Left=12
Right=12
Top=1
Bottom=1

[InputPanel/ContentMargin]
Left=10
Right=10
Top=10
Bottom=10

[InputPanel/TextMargin]
Left=10
Right=10
Top=4
Bottom=4

[InputPanel/PrevPage]
Image=prev.svg

[InputPanel/NextPage]
Image=next.svg

[Menu]
NormalColor={palette['fcitx5_text']}
HighlightCandidateColor={palette['fcitx5_text']}
Spacing=0

[Menu/Background]
Image=panel.svg
Color={bg}
BorderColor={border}
BorderWidth=0

[Menu/Background/Margin]
Left=6
Right=6
Top=6
Bottom=6

[Menu/Highlight]
Image=highlight.svg
Color={bg}
BorderColor={border}00
BorderWidth=0

[Menu/Highlight/Margin]
Left=4
Right=4
Top=2
Bottom=2

[Menu/Separator]
Color={palette['fcitx5_bg_alt']}
BorderColor={palette['fcitx5_bg_alt']}00
BorderWidth=0
"""
    with open(FCITX5_THEME, "w") as f: f.write(theme)
    classicui = Path.home() / ".config/fcitx5/conf/classicui.conf"
    if classicui.exists():
        content = classicui.read_text()
        content = re.sub(r"^Theme=.*", "Theme=bamboo-dark", content, flags=re.MULTILINE)
        content = re.sub(r"^DarkTheme=.*", "DarkTheme=bamboo-dark", content, flags=re.MULTILINE)
        content = re.sub(r"^UseDarkTheme=.*", "UseDarkTheme=False", content, flags=re.MULTILINE)
        if "Vertical Candidate List=" in content:
            content = re.sub(r"^Vertical Candidate List=.*", "Vertical Candidate List=True", content, flags=re.MULTILINE)
        else:
            content += "\nVertical Candidate List=True\n"
        content = re.sub(r"^TrayOutlineColor=.*", f"TrayOutlineColor={tray_outline}", content, flags=re.MULTILINE)
        content = re.sub(r"^TrayTextColor=.*", f"TrayTextColor={tray_text}", content, flags=re.MULTILINE)
        classicui.write_text(content)

def write_fastfetch(palette):
    if not FASTFETCH_CONFIG.exists():
        return
    content = FASTFETCH_CONFIG.read_text()

    content = re.sub(
        r'"color"\s*:\s*\{[^}]*\}',
        f'"color": {{ "keys": "{palette["iris"]}", "title": "{palette["text"]}" }}',
        content,
    )

    if '"disk"' not in content:
        content = content.replace(
            '{ "type": "memory", "key": " \uf0e4 Memory" }',
            '{ "type": "memory", "key": " \uf0e4 Memory" }, { "type": "disk", "key": " \uf0a0 Disk" }',
        )

    FASTFETCH_CONFIG.write_text(content)

ALACRITTY_THEME = Path.home() / ".config/alacritty/themes/noctalia.toml"

def write_alacritty(palette):
    if not ALACRITTY_TOML.exists(): return

    ALACRITTY_THEME.parent.mkdir(parents=True, exist_ok=True)
    theme_content = f"""# Auto-generated Morandi theme by morandi-gen.py
[colors.primary]
background = '{palette["term_bg"]}'
foreground = '{palette["text"]}'

[colors.cursor]
text = '{palette["base"]}'
cursor = '{palette["iris"]}'

[colors.vi_mode_cursor]
text = '{palette["base"]}'
cursor = '{palette["foam"]}'

[colors.search.matches]
foreground = '{palette["base"]}'
background = '{palette["term_yellow"]}'

[colors.search.focused_match]
foreground = '{palette["base"]}'
background = '{palette["term_blue"]}'

[colors.footer_bar]
foreground = '{palette["text"]}'
background = '{palette["mantle"]}'

[colors.hints.start]
foreground = '{palette["base"]}'
background = '{palette["term_yellow"]}'

[colors.hints.end]
foreground = '{palette["base"]}'
background = '{palette["term_magenta"]}'

[colors.selection]
text = '{palette["text"]}'
background = '{palette["surface2"]}'

[colors.normal]
black = '{palette["surface1"]}'
red = '{palette["term_red"]}'
green = '{palette["term_green"]}'
yellow = '{palette["term_yellow"]}'
blue = '{palette["term_blue"]}'
magenta = '{palette["term_magenta"]}'
cyan = '{palette["term_cyan"]}'
white = '{palette["text"]}'

[colors.bright]
black = '{palette["surface2"]}'
red = '{palette["term_bright_red"]}'
green = '{palette["term_bright_green"]}'
yellow = '{palette["term_bright_yellow"]}'
blue = '{palette["term_bright_blue"]}'
magenta = '{palette["term_bright_magenta"]}'
cyan = '{palette["term_bright_cyan"]}'
white = '{palette["text"]}'

[colors.dim]
black = '{palette["surface0"]}'
red = '{palette["term_dim_red"]}'
green = '{palette["term_dim_green"]}'
yellow = '{palette["term_dim_yellow"]}'
blue = '{palette["term_dim_blue"]}'
magenta = '{palette["term_dim_magenta"]}'
cyan = '{palette["term_dim_cyan"]}'
white = '{palette["subtext0"]}'
"""
    ALACRITTY_THEME.write_text(theme_content)

    content = ALACRITTY_TOML.read_text()
    # Clean up redundant inline color blocks in alacritty.toml since themes/noctalia.toml is imported
    cleaned = re.sub(r"\[colors\.(?:primary|normal|bright|cursor|selection)\][\s\S]*?(?=\n\[|\Z)", "", content)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if cleaned != content:
        ALACRITTY_TOML.write_text(cleaned)

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def write_kde(colors):
    def rgb_str(c): return f"{c[0]},{c[1]},{c[2]}"
    bg, surface, surface_var = hex_to_rgb(colors["background"]), hex_to_rgb(colors["surface_container"]), hex_to_rgb(colors["surface_variant"])
    primary, primary_cont = hex_to_rgb(colors["primary"]), hex_to_rgb(colors["primary_container"])
    on_surface, on_surface_var, on_primary = hex_to_rgb(colors["on_surface"]), hex_to_rgb(colors["on_surface_variant"]), hex_to_rgb(colors["on_primary"])
    error, window_bg = hex_to_rgb(colors["error"]), hex_to_rgb(colors["surface_container_low"])
    content = f"""[General]\nName=Morandi Dark\nshadeSortColumn=true\n
[Colors:Button]
BackgroundNormal={rgb_str(surface)}\nBackgroundAlternate={rgb_str(surface)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:View]
BackgroundNormal={rgb_str(bg)}\nBackgroundAlternate={rgb_str(surface_var)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:Window]
BackgroundNormal={rgb_str(window_bg)}\nBackgroundAlternate={rgb_str(window_bg)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:Selection]
BackgroundNormal={rgb_str(primary_cont)}\nBackgroundAlternate={rgb_str(primary_cont)}
ForegroundNormal={rgb_str(on_primary)}\nForegroundInactive={rgb_str(on_primary)}\nForegroundActive={rgb_str(on_primary)}
ForegroundLink={rgb_str(on_primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[WM]
activeBackground={rgb_str(surface)}\nactiveForeground={rgb_str(on_surface)}
inactiveBackground={rgb_str(bg)}\ninactiveForeground={rgb_str(on_surface_var)}
activeTitleBtnBg={rgb_str(primary_cont)}\ninactiveTitleBtnBg={rgb_str(surface)}\n"""
    KDE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    KDE_OUTPUT.write_text(content)

def write_blender(palette):
    """Generate Morandi Blender theme via XML string replacement on Eclipse baseline."""
    THEME_DIR = Path.home() / ".config/blender/5.1/scripts/presets/interface_theme"
    THEME_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = THEME_DIR / "Morandi.xml"

    baseline = Path(__file__).parent / "blender-eclipse-theme.xml"
    if not baseline.exists():
        print(f"Baseline XML not found: {baseline}")
        return

    def rgba(h, a="ff"):
        return f"#{h.lstrip('#')}{a}"

    m = palette
    # The Eclipse theme uses #242bf0 as its primary blue accent
    # We replace all color values systematically
    replacements = {
        # ── Primary accent (the big blue #242bf0 -> iris) ──
        "#242bf0":   rgba(m["iris"]),
        "#242bf0ff": rgba(m["iris"]),
        "#242bf033": rgba(m["iris"], "33"),
        "#242bf040": rgba(m["iris"], "40"),
        "#242bf002": rgba(m["iris"], "02"),

        # ── Backgrounds ──
        "#080808":   rgba(m["mantle"]),
        "#080808ff": rgba(m["mantle"]),
        "#08080800": rgba(m["mantle"], "00"),
        "#080808b3": rgba(m["mantle"], "b3"),
        "#121216":   rgba(m["base"]),
        "#18191e":   rgba(m["base"]),
        "#18191eff": rgba(m["base"]),
        "#18191e00": rgba(m["base"], "00"),
        "#18191eab": rgba(m["base"], "ab"),
        "#18191e66": rgba(m["base"], "66"),
        "#1b1c21ff": rgba(m["surface0"]),
        "#020202":   rgba(m["mantle"]),
        "#030303ff": rgba(m["mantle"]),
        "#0d0d0d":   rgba(m["mantle"]),
        "#0d0d0dff": rgba(m["mantle"]),
        "#0d0d0d00": rgba(m["mantle"], "00"),
        "#202124ff": rgba(m["surface0"]),
        "#22232dff": rgba(m["surface0"]),
        "#23252aff": rgba(m["surface1"]),
        "#23252a00": rgba(m["surface1"], "00"),
        "#23252aff": rgba(m["surface1"]),
        "#27292eff": rgba(m["surface1"]),
        "#292b339c": rgba(m["surface1"], "9c"),
        "#292c3373": rgba(m["surface1"], "73"),
        "#2c2e3b":   rgba(m["surface0"]),
        "#2e2f3b":   rgba(m["surface0"]),
        "#2f313b":   rgba(m["surface0"]),
        "#24262e":   rgba(m["surface1"]),
        "#24262eff": rgba(m["surface1"]),
        "#393d45ff": rgba(m["surface1"]),
        "#414452":   rgba(m["surface1"]),
        "#424552":   rgba(m["surface0"]),
        "#484a52ff": rgba(m["surface1"]),
        "#484a5200": rgba(m["surface1"], "00"),
        "#60636eff": rgba(m["surface2"]),
        "#17191f":   rgba(m["mantle"]),

        # ── Text ──
        "#d2d4d9":   rgba(m["text"]),
        "#d2d4d9ff": rgba(m["text"]),
        "#d0d6e0":   rgba(m["text"]),
        "#f8f8f9":   rgba(m["text"]),
        "#f8f8f9ff": rgba(m["text"]),
        "#f7f8f8":   rgba(m["text"]),
        "#e4e7f0":   rgba(m["text"]),
        "#eeefff":   rgba(m["text"]),
        "#eeeeee":   rgba(m["text"]),
        "#e6e6e6":   rgba(m["text"]),
        "#ffffff":   rgba(m["text"]),
        "#b2b3b8":   rgba(m["subtext0"]),
        "#bbbdc2":   rgba(m["subtext0"]),
        "#88898c":   rgba(m["subtext0"]),
        "#a2a9b8":   rgba(m["subtext0"]),
        "#717482":   rgba(m["subtext0"]),
        "#717480":   rgba(m["subtext0"]),
        "#66676e":   rgba(m["subtext0"]),
        "#585b69":   rgba(m["subtext0"]),
        "#b7b7b8":   rgba(m["subtext0"]),

        # ── Active / selection (Eclipse blue -> gold) ──
        "#eef4ff":   rgba(m["gold"]),
        "#f8f8f9":   rgba(m["text"]),

        # ── Greens ──
        "#26ff8a":   rgba(m["pine"]),
        "#33ff9d":   rgba(m["pine"]),
        "#54ffcc":   rgba(m["pine"]),
        "#26ffbe":   rgba(m["pine"]),
        "#78f244":   rgba(m["pine"]),
        "#94e575":   rgba(m["pine"]),
        "#95d600":   rgba(m["pine"]),
        "#188625":   rgba(m["pine"]),
        "#61c042":   rgba(m["pine"]),
        "#53992e":   rgba(m["pine"]),
        "#38a600":   rgba(m["pine"]),
        "#409030":   rgba(m["pine"]),
        "#40c030":   rgba(m["pine"]),
        "#3c5e03":   rgba(m["pine"]),
        "#156e49":   rgba(m["pine"]),
        "#036950":   rgba(m["pine"]),
        "#008062":   rgba(m["pine"]),
        "#0e7ee6":   rgba(m["sky"]),
        "#0ee68b":   rgba(m["pine"]),
        "#00ff00ff": rgba(m["pine"]),

        # ── Reds ──
        "#ff337c":   rgba(m["love"]),
        "#f02814":   rgba(m["love"]),
        "#ff4d84":   rgba(m["love"]),
        "#ff2674":   rgba(m["love"]),
        "#771111":   rgba(m["love"]),
        "#e8b3cc":   rgba(m["rose"]),
        "#f28080":   rgba(m["love"]),
        "#ff1900":   rgba(m["love"]),
        "#740d00":   rgba(m["love"]),
        "#cc5a52":   rgba(m["love"]),
        "#e63776":   rgba(m["love"]),
        "#f090a0":   rgba(m["rose"]),
        "#803232":   rgba(m["love"]),
        "#8054ff":   rgba(m["iris"]),
        "#5e26ff":   rgba(m["iris"]),
        "#548eff":   rgba(m["sky"]),
        "#2670ff":   rgba(m["sky"]),
        "#ff5491":   rgba(m["rose"]),
        "#994030":   rgba(m["peach"]),
        "#f0af90":   rgba(m["peach"]),
        "#803060":   rgba(m["rose"]),
        "#cc0099":   rgba(m["rose"]),
        "#dd23dd":   rgba(m["rose"]),
        "#ff0000ff": rgba(m["love"]),

        # ── Golds / yellows ──
        "#edba18":   rgba(m["gold"]),
        "#ffc300":   rgba(m["gold"]),
        "#f0ff40":   rgba(m["gold"]),
        "#909000":   rgba(m["gold"]),
        "#a28962":   rgba(m["gold"]),
        "#cc7529":   rgba(m["peach"]),
        "#d26400":   rgba(m["peach"]),
        "#ac8737":   rgba(m["gold"]),
        "#ffaf23":   rgba(m["gold"]),
        "#ffff00":   rgba(m["gold"]),
        "#ebc80f":   rgba(m["gold"]),
        "#f4c90c":   rgba(m["gold"]),
        "#eec236":   rgba(m["gold"]),
        "#f3ff00":   rgba(m["gold"]),
        "#d4a233":   rgba(m["gold"]),

        # ── Blues -> morandi sky/iris ──
        "#2670ff":   rgba(m["sky"]),
        "#63ffff":   rgba(m["sky"]),
        "#2e75db":   rgba(m["sky"]),
        "#5db6ea":   rgba(m["sky"]),
        "#00a5ff":   rgba(m["sky"]),
        "#00ffff":   rgba(m["sky"]),
        "#22dddd":   rgba(m["sky"]),
        "#50c8ff":   rgba(m["sky"]),
        "#8cffff":   rgba(m["sky"]),
        "#2361dd":   rgba(m["sky"]),
        "#0000cc":   rgba(m["sky"]),
        "#48d9e6":   rgba(m["sky"]),
        "#93dbe8":   rgba(m["sky"]),
        "#54bfed":   rgba(m["sky"]),
        "#28487d":   rgba(m["sky"]),
        "#4444ff":   rgba(m["sky"]),
        "#232374":   rgba(m["sky"]),
        "#096494":   rgba(m["sky"]),
        "#2a2482":   rgba(m["iris"]),
        "#551a80":   rgba(m["iris"]),
        "#9c73e6":   rgba(m["iris"]),
        "#8d59da":   rgba(m["iris"]),
        "#692196":   rgba(m["iris"]),
        "#332642":   rgba(m["mantle"]),
        "#867acc":   rgba(m["iris"]),
        "#3a40f099": rgba(m["iris"], "99"),
        "#32369966": rgba(m["iris"], "66"),
        "#252ab4":   rgba(m["iris"]),
        "#1d3c692a": rgba(m["iris"], "2a"),

        # ── Teals ──
        "#00c3c3":   rgba(m["sky"]),
        "#118f8f":   rgba(m["sky"]),
        "#4c9797":   rgba(m["sky"]),
        "#084d4d":   rgba(m["sky"]),
        "#54ffff":   rgba(m["sky"]),
        "#33ffff":   rgba(m["sky"]),
        "#1f7a7a":   rgba(m["sky"]),
        "#2b3d3d":   rgba(m["mantle"]),

        # ── Oranges / warm ──
        "#c4753b":   rgba(m["peach"]),
        "#6e3d15":   rgba(m["peach"]),
        "#834326":   rgba(m["peach"]),
        "#8b5811":   rgba(m["peach"]),
        "#bd6a11":   rgba(m["peach"]),
        "#7a5441":   rgba(m["peach"]),
        "#996952":   rgba(m["peach"]),
        "#8f6e56":   rgba(m["peach"]),
        "#6278a3":   rgba(m["sky"]),
        "#8c548c":   rgba(m["iris"]),
        "#7b5f80":   rgba(m["rose"]),
        "#568f6d":   rgba(m["pine"]),
        "#8f5656":   rgba(m["love"]),
        "#9f926f":   rgba(m["peach"]),
        "#689d06":   rgba(m["pine"]),
        "#ff734d":   rgba(m["peach"]),
        "#e62e67":   rgba(m["love"]),

        # ── NLA / strip fills ──
        "#0d0d0d":   rgba(m["mantle"]),
        "#1c2630":   rgba(m["mantle"]),
        "#332642":   rgba(m["mantle"]),
        "#664162":   rgba(m["mantle"]),
        "#76512f":   rgba(m["mantle"]),
        "#33527f":   rgba(m["mantle"]),
        "#7d7d3a":   rgba(m["mantle"]),
        "#4d3b174d": rgba(m["mantle"], "4d"),
        "#4df31a":   rgba(m["pine"]),

        # ── Misc ──
        "#4da84d":   rgba(m["pine"]),
        "#a33535":   rgba(m["love"]),
        "#7fff7f":   rgba(m["pine"]),
        "#ccad63":   rgba(m["gold"]),
        "#cc6670":   rgba(m["rose"]),
        "#e19658":   rgba(m["peach"]),
        "#00d4a3":   rgba(m["pine"]),
        "#74a2ff":   rgba(m["sky"]),
        "#ab3c48":   rgba(m["love"]),
        "#f1a355":   rgba(m["peach"]),
        "#f1dc55":   rgba(m["gold"]),
        "#7bcc7b":   rgba(m["pine"]),
        "#c673b8":   rgba(m["rose"]),
        "#519fcc":   rgba(m["sky"]),
        "#99995c":   rgba(m["gold"]),
        "#7b995c":   rgba(m["pine"]),
        "#cc8a48":   rgba(m["peach"]),
        "#b3a33f":   rgba(m["gold"]),
        "#5c995c":   rgba(m["pine"]),
        "#8d59da":   rgba(m["iris"]),
        "#1e9109":   rgba(m["pine"]),
        "#59b70b":   rgba(m["pine"]),
        "#83ef1d":   rgba(m["pine"]),
        "#0a3694":   rgba(m["sky"]),
        "#3667df":   rgba(m["sky"]),
        "#5ec1ef":   rgba(m["sky"]),
        "#a9294e":   rgba(m["love"]),
        "#c1416a":   rgba(m["love"]),
        "#f05d91":   rgba(m["rose"]),
        "#430c78":   rgba(m["iris"]),
        "#543aa3":   rgba(m["iris"]),
        "#8764d5":   rgba(m["iris"]),
        "#24785a":   rgba(m["pine"]),
        "#3c9579":   rgba(m["pine"]),
        "#6fb6ab":   rgba(m["sky"]),
        "#4b707c":   rgba(m["sky"]),
        "#6a8691":   rgba(m["sky"]),
        "#9bc2cd":   rgba(m["sky"]),
        "#6f2f6a":   rgba(m["iris"]),
        "#9845be":   rgba(m["iris"]),
        "#d330d6":   rgba(m["rose"]),
        "#6c8e22":   rgba(m["pine"]),
        "#7fb022":   rgba(m["pine"]),
        "#bbef5b":   rgba(m["pine"]),
        "#1e2024":   rgba(m["mantle"]),
        "#484c56":   rgba(m["surface1"]),
        "#08310e":   rgba(m["pine"]),
        "#1c430b":   rgba(m["pine"]),
        "#34622b":   rgba(m["pine"]),
        "#f74018":   rgba(m["peach"]),
        "#f66913":   rgba(m["peach"]),
        "#fa9900":   rgba(m["gold"]),
        "#1e9109":   rgba(m["pine"]),
        "#59b70b":   rgba(m["pine"]),
        "#83ef1d":   rgba(m["pine"]),
        "#0a3694":   rgba(m["sky"]),
        "#3667df":   rgba(m["sky"]),
        "#5ec1ef":   rgba(m["sky"]),
        "#a9294e":   rgba(m["love"]),
        "#c1416a":   rgba(m["love"]),
        "#f05d91":   rgba(m["rose"]),
        "#430c78":   rgba(m["iris"]),
        "#543aa3":   rgba(m["iris"]),
        "#8764d5":   rgba(m["iris"]),
        "#24785a":   rgba(m["pine"]),
        "#3c9579":   rgba(m["pine"]),
        "#6fb6ab":   rgba(m["sky"]),
        "#4b707c":   rgba(m["sky"]),
        "#6a8691":   rgba(m["sky"]),
        "#9bc2cd":   rgba(m["sky"]),

        # ── Preview stitch ──
        "#7f7f0033": rgba(m["gold"], "33"),
        "#ff00ff33": rgba(m["rose"], "33"),
        "#0000ff33": rgba(m["sky"], "33"),
        "#e1d2c323": rgba(m["peach"], "23"),

        # ── Remaining blues from Eclipse ──
        "#191d8080": rgba(m["sky"], "80"),
        "#0046cc02": rgba(m["sky"], "02"),
        "#0051f033": rgba(m["sky"], "33"),
        "#3339ff":   rgba(m["iris"]),
        "#1317801a": rgba(m["iris"], "1a"),
        "#001566":   rgba(m["iris"]),
        "#0000ff":   rgba(m["sky"]),
        "#c4c4ff":   rgba(m["sky"]),
        "#0000ff33": rgba(m["sky"], "33"),

        # ── Transparent / overlay fills ──
        "#ffffff04": rgba(m["mantle"], "04"),
        "#ffffff05": rgba(m["mantle"], "05"),
        "#ffffff0a": rgba(m["mantle"], "0a"),
        "#ffffff15": rgba(m["mantle"], "15"),
        "#ffffff1a": rgba(m["mantle"], "1a"),
        "#ffffff1f": rgba(m["mantle"], "1f"),
        "#ffffff26": rgba(m["mantle"], "26"),
        "#ffffff30": rgba(m["mantle"], "30"),
        "#ffffff33": rgba(m["mantle"], "33"),
        "#ffffff4d": rgba(m["mantle"], "4d"),
        "#ffffff80": rgba(m["text"], "80"),
        "#ffffff8f": rgba(m["text"], "8f"),
        "#ffffffb3": rgba(m["text"], "b3"),
        "#ffffffff": rgba(m["text"]),
        "#00000080": rgba(m["mantle"], "80"),
        "#00000099": rgba(m["mantle"], "99"),
        "#0000004d": rgba(m["mantle"], "4d"),
        "#000000ff": rgba(m["mantle"]),
        "#000000":   rgba(m["mantle"]),
        "#0000ffb3": rgba(m["sky"], "b3"),

        # ── Special view3d ──
        "#ececff33": rgba(m["surface1"], "33"),
        "#50c8ff0f": rgba(m["sky"], "0f"),

        # ── Info bar ──
        "#120730ff": rgba(m["mantle"]),
        "#460ee6":   rgba(m["iris"]),
        "#07301fff": rgba(m["mantle"]),
    }

    xml_content = baseline.read_text()

    # Apply replacements (longest first to avoid partial matches)
    for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
        xml_content = xml_content.replace(old, new)

    # Rename theme
    xml_content = xml_content.replace(
        'name="Eclipse"',
        'name="Morandi"'
    ).replace(
        '<ThemeUserInterface',
        '<ThemeUserInterface name="Morandi"'
    )

    # Playhead: mid-dark bg so white text is readable
    xml_content = xml_content.replace(
        'playhead="#afac9cff"',
        'playhead="#302f2cff"'
    )
    xml_content = xml_content.replace(
        'time_marker_selected="#f2f2f2b3"',
        'time_marker_selected="#111112b3"'
    )

    xml_path.write_text(xml_content)
    print(f"Morandi theme written to {xml_path}")

    # Auto-install via Blender
    subprocess.run([
        "blender", "-b", "--python-expr",
        f"import bpy; bpy.ops.preferences.theme_install(filepath='{xml_path}')"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_godot(palette):
    godot_settings = list(Path.home().glob(".config/godot/editor_settings-*.tres"))
    if not godot_settings: return
    
    def hex_to_color(hex_str):
        hex_str = hex_str.lstrip('#')
        r, g, b = (int(hex_str[i:i+2], 16)/255.0 for i in (0, 2, 4))
        return f"Color({r:.3f}, {g:.3f}, {b:.3f}, 1)"
        
    base_color = hex_to_color(palette["base"])
    accent_color = hex_to_color(palette["iris"])
    
    for path in godot_settings:
        content = path.read_text()
        content = re.sub(r'interface/theme/base_color\s*=\s*Color\([^)]+\)', f'interface/theme/base_color = {base_color}', content)
        content = re.sub(r'interface/theme/accent_color\s*=\s*Color\([^)]+\)', f'interface/theme/accent_color = {accent_color}', content)
        content = re.sub(r'interface/theme/color_preset\s*=\s*".*"', 'interface/theme/color_preset = "Custom"', content)
        path.write_text(content)

def write_obs(palette):
    obs_theme_dir = Path.home() / ".config/obs-studio/themes"
    obs_theme_dir.mkdir(parents=True, exist_ok=True)
    
    def rgb_str(hex_c):
        r, g, b = hex_to_rgb(hex_c)
        return f"rgb({r},{g},{b})"
        
    def darken(hex_c, amount=10):
        return morandi(hex_c, 0, -amount, 0, 100)

    obs_iris = darken(palette['iris'], 12)
    obs_foam = darken(palette['foam'], 12)
    obs_sky = darken(palette['sky'], 12)

    content = f"""@OBSThemeMeta {{
    name: 'Morandi';
    id: 'com.obsproject.Yami.Morandi';
    extends: 'com.obsproject.Yami';
    author: 'morandi-gen';
    dark: 'true';
}}

@OBSThemeVars {{
    --primary: {rgb_str(obs_iris)};
    --primary_light: {rgb_str(obs_foam)};
    --primary_lighter: {rgb_str(obs_sky)};
    --primary_dark: {rgb_str(palette['pine'])};
    --primary_darker: {rgb_str(palette['base'])};

    --blue1: {rgb_str(obs_sky)};
    --blue2: {rgb_str(obs_foam)};
    --blue3: {rgb_str(obs_iris)};
    --blue4: {rgb_str(palette['pine'])};
    --blue5: {rgb_str(palette['surface1'])};
    --blue6: {rgb_str(palette['surface0'])};

    --bg_base: {rgb_str(palette['mantle'])};
    --bg_window: {rgb_str(palette['base'])};
    --bg_preview: {rgb_str(palette['mantle'])};

    --border_color: {rgb_str(palette['surface1'])};

    --input_bg: {rgb_str(palette['surface0'])};
    --input_bg_hover: {rgb_str(palette['surface1'])};
    --input_bg_focus: {rgb_str(palette['surface1'])};

    --list_item_bg_selected: {rgb_str(palette['surface0'])};
    --list_item_bg_hover: {rgb_str(palette['surface1'])};

    --input_border: {rgb_str(palette['surface2'])};
    --input_border_hover: {rgb_str(obs_iris)};
    --input_border_focus: {rgb_str(obs_iris)};

    --button_bg: {rgb_str(palette['surface0'])};
    --button_bg_hover: {rgb_str(palette['surface1'])};
    --button_bg_down: {rgb_str(palette['surface2'])};
    --button_bg_disabled: {rgb_str(palette['mantle'])};

    --button_bg_red: {rgb_str(palette['love'])};
    --button_bg_red_hover: {rgb_str(palette['rose'])};
    --button_bg_red_down: {rgb_str(palette['love'])};

    --button_border: {rgb_str(palette['surface2'])};
    --button_border_hover: {rgb_str(obs_iris)};
    --button_border_focus: {rgb_str(obs_iris)};

    --tab_bg: {rgb_str(palette['surface0'])};
    --tab_bg_hover: {rgb_str(palette['surface1'])};
    --tab_bg_down: {rgb_str(palette['surface2'])};
    --tab_bg_disabled: {rgb_str(palette['mantle'])};

    --tab_border: {rgb_str(palette['surface0'])};
    --tab_border_hover: {rgb_str(palette['surface2'])};
    --tab_border_focus: {rgb_str(palette['surface2'])};
    --tab_border_selected: {rgb_str(obs_iris)};

    --scrollbar_handle: {rgb_str(palette['surface1'])};
    --scrollbar_hover: {rgb_str(palette['surface2'])};
    --scrollbar_down: {rgb_str(palette['surface0'])};
    --scrollbar_border: {rgb_str(palette['surface1'])};

    --toolbutton_bg: {rgb_str(palette['surface0'])};
    --toolbutton_bg_hover: {rgb_str(palette['surface1'])};
    --toolbutton_bg_down: {rgb_str(palette['surface2'])};
    --toolbutton_bg_disabled: {rgb_str(palette['mantle'])};
}}
"""
    (obs_theme_dir / "Yami_Morandi.ovt").write_text(content)
    
    obs_config = Path.home() / ".config/obs-studio/global.ini"
    if obs_config.exists():
        conf = obs_config.read_text()
        conf = re.sub(r"^CurrentTheme3=.*", "CurrentTheme3=Yami_Morandi", conf, flags=re.MULTILINE)
        obs_config.write_text(conf)

def write_clash_verge(palette):
    config_path = Path.home() / ".local/share/io.github.clash-verge-rev.clash-verge-rev/verge.yaml"
    if not config_path.exists():
        return

    content = config_path.read_text()

    css = f""":root {{
  --joy-palette-background-body: {palette['base']} !important;
  --joy-palette-background-surface: {palette['surface0']} !important;
  --joy-palette-background-level1: {palette['surface1']} !important;
  --joy-palette-background-level2: {palette['surface2']} !important;
  --joy-palette-background-level3: {palette['overlay0']} !important;
  --mui-palette-background-default: {palette['base']} !important;
  --mui-palette-background-paper: {palette['surface0']} !important;
  --bg-base: {palette['base']} !important;
  --bg-surface: {palette['surface0']} !important;
  --mui-palette-primary-contrastText: #ffffff !important;
  --joy-palette-primary-solidColor: #ffffff !important;
}}
body, #root, main, .MuiDrawer-paper, .MuiAppBar-root, .layout-content, .page, .page-content {{
  background-color: {palette['base']} !important;
  background-image: none !important;
  color: {palette['text']} !important;
}}
.MuiPaper-root, .MuiCard-root, .MuiDialog-paper, .MuiPopover-paper {{
  background-color: {palette['surface0']} !important;
  background-image: none !important;
  border-radius: 12px !important;
  border: 1px solid {palette['surface1']} !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}}
.Mui-selected, .Mui-selected *, .MuiButton-containedPrimary, .MuiButton-containedPrimary *, .clash-active {{
  color: #ffffff !important;
}}
* {{
  transition: background-color 0.4s cubic-bezier(0.4, 0, 0.2, 1), 
              border-color 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              color 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.MuiButtonBase-root:hover, .MuiMenuItem-root:hover, .clash-hover-effect:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2) !important;
}}
.MuiButtonBase-root:active, .MuiMenuItem-root:active, .clash-hover-effect:active {{
  transform: translateY(1px) !important;
  box-shadow: none !important;
}}"""

    css_indented = "\n    ".join(css.split("\n"))
    
    theme_setting = f"theme_setting:\n  primary_color: '{palette['iris']}'\n  secondary_color: '{palette['foam']}'\n  info_color: '{palette['sky']}'\n  error_color: '{palette['love']}'\n  warning_color: '{palette['gold']}'\n  success_color: '{palette['pine']}'\n  css_injection: |\n    {css_indented}"
    
    if "theme_setting: null" in content:
        content = re.sub(r"^theme_setting:\s*null", theme_setting, content, flags=re.MULTILINE)
    elif re.search(r"^theme_setting:", content, flags=re.MULTILINE):
        content = re.sub(r"^theme_setting:.*(\n\s+.*)*", theme_setting, content, flags=re.MULTILINE)
    else:
        content += "\n" + theme_setting + "\n"
        
    content = re.sub(r"^css_injection:.*(\n\s+.*)*", "", content, flags=re.MULTILINE).strip() + "\n"
        
    config_path.write_text(content)




def apply_system_changes(wallpaper_path=None):
    def run_ignore_missing(*args, **kwargs):
        try:
            subprocess.run(*args, **kwargs)
        except FileNotFoundError:
            pass

    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
    run_ignore_missing(["dbus-send", "--session", "--dest=org.kde.plasmashell", "--type=method_call", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", "string: var allDesktops = desktops(); for (var i=0; i<allDesktops.length; i++) { allDesktops[i].wallpaperPlugin = '' }"], env=env, stderr=subprocess.DEVNULL)
    run_ignore_missing(["qdbus", "org.kde.KWin", "/KWin", "reconfigure"], env=env, stderr=subprocess.DEVNULL)
    run_ignore_missing(["niri", "msg", "action", "load-config-file"], stderr=subprocess.DEVNULL)
    run_ignore_missing(["mmsg", "reload_config"], stderr=subprocess.DEVNULL)
    run_ignore_missing(["pkill", "-USR2", "cava"], stderr=subprocess.DEVNULL)
    
    if wallpaper_path and Path(wallpaper_path).exists():
        efi_dir = "/boot/efi"
        subprocess.run(["sudo", "magick", wallpaper_path, "-blur", "0x12", "-resize", "1920x1080!", "-quality", "95", f"{efi_dir}/limine_bg.png"], stderr=subprocess.DEVNULL)
        
    try:
        pid = subprocess.check_output(["pgrep", "-x", "fcitx5"]).decode().strip()
        if pid:
            subprocess.run(["kill", pid])
            subprocess.run(["sleep", "0.3"])
    except subprocess.CalledProcessError:
        pass
    subprocess.Popen(["fcitx5"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def write_flclash(palette):
    config_path = Path.home() / ".local/share/com.follow.clash/shared_preferences.json"
    if not config_path.exists():
        return
        
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            
        if "flutter.config" in data:
            flutter_config = json.loads(data["flutter.config"])
            
            hex_color = palette['iris'].lstrip('#')
            if len(hex_color) == 6:
                argb_int = int("ff" + hex_color, 16)
            else:
                argb_int = int(hex_color, 16)
                
            if "themeProps" not in flutter_config:
                flutter_config["themeProps"] = {}
                
            flutter_config["themeProps"]["primaryColor"] = argb_int
            flutter_config["themeProps"]["pureBlack"] = False
            flutter_config["themeProps"]["themeMode"] = "dark"
            
            data["flutter.config"] = json.dumps(flutter_config, separators=(',', ':'))
            
            with open(config_path, "w") as f:
                json.dump(data, f, separators=(',', ':'))
    except Exception as e:
        print(f"Failed to write flclash theme: {e}")

def write_cava(palette):
    cava_dir = Path.home() / ".config/cava"
    theme_dir = cava_dir / "themes"
    theme_dir.mkdir(parents=True, exist_ok=True)
    theme_path = theme_dir / "morandi"
    content = f"""; Auto-generated by morandi-gen.py — do not edit manually
[color]
background = 'default'
foreground = '{palette['iris']}'

gradient = 1
gradient_color_1 = '{palette['sky']}'
gradient_color_2 = '{palette['foam']}'
gradient_color_3 = '{palette['pine']}'
gradient_color_4 = '{palette['iris']}'
gradient_color_5 = '{palette['gold']}'
gradient_color_6 = '{palette['peach']}'
gradient_color_7 = '{palette['rose']}'
gradient_color_8 = '{palette['love']}'
"""
    theme_path.write_text(content)


def write_libswell(palette):
    swell_conf = Path.home() / ".config/REAPER/libSwell-user.colortheme"
    if not swell_conf.exists(): return
    content = swell_conf.read_text()
    
    bg = palette["base"]
    bg_alt = palette["mantle"]
    bg_dark = morandi(palette["base"], 0, -3)
    text = palette["text"]
    text_dim = palette["subtext0"]
    accent = palette["iris"]
    
    replacements = {
        "#333333": bg, "#2e2e2e": bg_alt, "#282828": bg_alt, "#2a2a2a": bg_alt,
        "#303030": bg, "#2f2f2f": bg_alt, "#292929": bg_alt, "#242424": bg_dark,
        "#202020": bg_dark, "#353535": bg_dark, "#2c2c2c": bg_dark,
        "#d1a660": accent, "#d1d1d1": text, "#c3c3c3": text_dim,
        "#9a9a9a": text_dim, "#7a7a7a": text_dim, "#777777": text_dim,
        "#676767": text_dim, "#585858": text_dim, "#050505": bg_dark,
        "#1a1a1a": bg_alt, "#e6e6e6": text, "#1A1A1A": bg_alt, "#E6E6E6": text
    }
    
    content = re.sub(r"#[0-9a-fA-F]{6}", lambda m: replacements.get(m.group(0), m.group(0).lower()), content)
    # also try lower casing for the map
    content = re.sub(r"#[0-9a-fA-F]{6}", lambda m: replacements.get(m.group(0).lower(), m.group(0)), content)
    swell_conf.write_text(content)

def write_zed(palette):
    zed_theme_dir = Path.home() / ".config/zed/themes"
    zed_theme_dir.mkdir(parents=True, exist_ok=True)
    
    theme = {
        "$schema": "https://zed.dev/schema/themes/v0.1.0.json",
        "name": "Morandi",
        "author": "morandi-gen",
        "themes": [
            {
                "name": "Morandi",
                "appearance": "dark",
                "style": {
                    "border": palette["surface2"],
                    "border.variant": palette["surface1"],
                    "border.focused": palette["iris"],
                    "border.selected": palette["iris"],
                    "border.transparent": "#00000000",
                    "border.disabled": palette["surface1"],
                    "elevated_surface.background": palette["surface0"],
                    "surface.background": palette["base"],
                    "background": palette["base"],
                    "element.background": palette["base"],
                    "element.hover": palette["surface0"],
                    "element.active": palette["surface1"],
                    "element.selected": palette["surface1"],
                    "element.disabled": palette["base"],
                    "drop_target.background": palette["surface1"],
                    "ghost_element.background": "#00000000",
                    "ghost_element.hover": palette["surface0"],
                    "ghost_element.active": palette["surface1"],
                    "ghost_element.selected": palette["surface1"],
                    "ghost_element.disabled": "#00000000",
                    "text": palette["text"],
                    "text.muted": palette["subtext0"],
                    "text.placeholder": palette["subtext1"],
                    "text.disabled": palette["subtext0"],
                    "text.accent": palette["iris"],
                    "icon": palette["text"],
                    "icon.muted": palette["subtext0"],
                    "icon.disabled": palette["subtext0"],
                    "icon.placeholder": palette["subtext1"],
                    "icon.accent": palette["iris"],
                    "status_bar.background": palette["mantle"],
                    "title_bar.background": palette["mantle"],
                    "toolbar.background": palette["mantle"],
                    "tab_bar.background": palette["mantle"],
                    "tab.inactive_background": palette["mantle"],
                    "tab.active_background": palette["base"],
                    "panel.background": palette["mantle"],
                    "panel.focused_border": palette["iris"],
                    "editor.foreground": palette["text"],
                    "editor.background": palette["base"],
                    "editor.gutter.background": palette["base"],
                    "editor.line_number": palette["overlay0"],
                    "editor.active_line_number": palette["text"],
                    "editor.active_line.background": palette["surface0"],
                    "editor.highlighted_line.background": palette["surface0"],
                    "editor.invisible": palette["surface1"],
                    "editor.wrap_guide": palette["surface1"],
                    "editor.active_wrap_guide": palette["surface2"],
                    "search.match_background": palette["surface2"],
                    "terminal.background": palette["base"],
                    "terminal.foreground": palette["text"],
                    "terminal.ansi.black": palette["surface1"],
                    "terminal.ansi.red": palette["love"],
                    "terminal.ansi.green": blend(palette["pine"], palette["surface1"], 0.4),
                    "terminal.ansi.yellow": palette["gold"],
                    "terminal.ansi.blue": blend(palette["iris"], palette["surface1"], 0.4),
                    "terminal.ansi.magenta": palette["rose"],
                    "terminal.ansi.cyan": blend(palette["sky"], palette["surface1"], 0.4),
                    "terminal.ansi.white": palette["text"],
                    "terminal.ansi.bright_black": palette["surface2"],
                    "terminal.ansi.bright_red": palette["love"],
                    "terminal.ansi.bright_green": blend(palette["pine"], palette["surface1"], 0.4),
                    "terminal.ansi.bright_yellow": palette["gold"],
                    "terminal.ansi.bright_blue": blend(palette["iris"], palette["surface1"], 0.4),
                    "terminal.ansi.bright_magenta": palette["rose"],
                    "terminal.ansi.bright_cyan": blend(palette["sky"], palette["surface1"], 0.4),
                    "terminal.ansi.bright_white": palette["text"],
                    "players": [
                        {
                            "cursor": palette["pine"],
                            "background": palette["pine"],
                            "selection": palette["surface2"]
                        }
                    ],
                    "created": palette["pine"] + "50",
                    "modified": palette["iris"] + "50",
                    "deleted": palette["love"] + "50",
                    "conflict": palette["peach"] + "50",
                    "ignored": palette["subtext0"],
                    "hint": palette["subtext0"],
                    "info": palette["foam"],
                    "predictive": palette["subtext0"],
                    "scrollbar_thumb.background": palette["surface2"] + "80",
                    "scrollbar.thumb.background": palette["surface2"] + "80",
                    "scrollbar.thumb.hover_background": palette["surface2"] + "c0",
                    "scrollbar.track.background": "#00000000",
                    "scrollbar.track.border": "#00000000",
                    "syntax": {
                        "keyword": {"color": palette["rose"]},
                        "function": {"color": palette["iris"]},
                        "string": {"color": palette["pine"]},
                        "type": {"color": palette["gold"]},
                        "number": {"color": palette["peach"]},
                        "constant": {"color": palette["peach"]},
                        "property": {"color": palette["text"]},
                        "variable": {"color": palette["text"]},
                        "comment": {"color": palette["subtext0"], "font_style": "italic"},
                        "punctuation": {"color": palette["subtext0"]},
                        "operator": {"color": palette["subtext0"]},
                        "boolean": {"color": palette["peach"]},
                        "label": {"color": palette["pine"]},
                        "predictive": {"color": palette["subtext0"], "font_style": "italic"}
                    }
                }
            }
        ]
    }
    
    (zed_theme_dir / "morandi.json").write_text(json.dumps(theme, indent=2))


def write_vscode(palette):
    vscode_ext_dir = Path.home() / ".vscode/extensions/morandi-theme-0.0.1/themes"
    vscode_user_dir = Path.home() / ".config/Code/User/themes"
    vscode_ext_dir.mkdir(parents=True, exist_ok=True)
    vscode_user_dir.mkdir(parents=True, exist_ok=True)

    theme = {
        "name": "Morandi",
        "type": "dark",
        "colors": {
            "editor.background": palette["base"],
            "editor.foreground": palette["text"],
            "editorLineNumber.foreground": palette["overlay0"],
            "editorLineNumber.activeForeground": palette["text"],
            "editor.lineHighlightBackground": palette["surface0"],
            "editor.selectionBackground": palette["surface2"],
            "editor.inactiveSelectionBackground": palette["surface1"],
            "editorCursor.foreground": palette["pine"],
            "editorWhitespace.foreground": palette["surface1"],
            "editorIndentGuide.background": palette["surface1"],
            "editorIndentGuide.activeBackground": palette["surface2"],
            "editor.findMatchBackground": palette["surface2"],
            "editor.findMatchHighlightBackground": palette["surface2"] + "80",
            "editorBracketMatch.background": palette["surface2"] + "80",
            "editorBracketMatch.border": palette["iris"],
            "editorGutter.background": palette["base"],
            "editorWidget.background": palette["surface0"],
            "editorWidget.border": palette["surface2"],
            "editorSuggestWidget.background": palette["surface0"],
            "editorSuggestWidget.border": palette["surface2"],
            "editorSuggestWidget.selectedBackground": palette["surface1"],
            "editorHoverWidget.background": palette["surface0"],
            "editorHoverWidget.border": palette["surface2"],
            "minimap.background": palette["base"] + "cc",
            "scrollbarSlider.background": palette["surface2"] + "80",
            "scrollbarSlider.hoverBackground": palette["surface2"] + "c0",
            "scrollbarSlider.activeBackground": palette["surface2"],
            "sideBar.background": palette["mantle"],
            "sideBar.foreground": palette["text"],
            "sideBar.border": palette["surface1"],
            "sideBarTitle.foreground": palette["text"],
            "sideBarSectionHeader.background": palette["mantle"],
            "sideBarSectionHeader.foreground": palette["subtext0"],
            "statusBar.background": palette["mantle"],
            "statusBar.foreground": palette["subtext0"],
            "statusBar.border": palette["surface1"],
            "titleBar.activeBackground": palette["mantle"],
            "titleBar.activeForeground": palette["subtext0"],
            "titleBar.inactiveBackground": palette["mantle"],
            "titleBar.border": palette["surface1"],
            "tab.activeBackground": palette["base"],
            "tab.activeForeground": palette["text"],
            "tab.inactiveBackground": palette["mantle"],
            "tab.inactiveForeground": palette["subtext0"],
            "tab.activeBorderTop": palette["iris"],
            "tab.border": palette["mantle"],
            "editorGroupHeader.tabsBackground": palette["mantle"],
            "editorGroupHeader.tabsBorder": palette["surface1"],
            "panel.background": palette["mantle"],
            "panel.border": palette["surface1"],
            "panelTitle.activeBorder": palette["iris"],
            "panelTitle.activeForeground": palette["text"],
            "panelTitle.inactiveForeground": palette["subtext0"],
            "terminal.background": palette["base"],
            "terminal.foreground": palette["text"],
            "terminal.ansiBlack": palette["surface1"],
            "terminal.ansiRed": palette["love"],
            "terminal.ansiGreen": palette["pine"],
            "terminal.ansiYellow": palette["gold"],
            "terminal.ansiBlue": palette["iris"],
            "terminal.ansiMagenta": palette["rose"],
            "terminal.ansiCyan": palette["sky"],
            "terminal.ansiWhite": palette["text"],
            "terminal.ansiBrightBlack": palette["surface2"],
            "terminal.ansiBrightRed": palette["love"],
            "terminal.ansiBrightGreen": palette["pine"],
            "terminal.ansiBrightYellow": palette["gold"],
            "terminal.ansiBrightBlue": palette["iris"],
            "terminal.ansiBrightMagenta": palette["rose"],
            "terminal.ansiBrightCyan": palette["sky"],
            "terminal.ansiBrightWhite": palette["text"],
            "input.background": palette["surface0"],
            "input.border": palette["surface2"],
            "input.foreground": palette["text"],
            "input.placeholderForeground": palette["subtext0"],
            "inputOption.activeBorder": palette["iris"],
            "dropdown.background": palette["surface0"],
            "dropdown.border": palette["surface2"],
            "dropdown.foreground": palette["text"],
            "button.background": palette["iris"],
            "button.foreground": palette["base"],
            "button.hoverBackground": palette["iris"] + "cc",
            "list.activeSelectionBackground": palette["surface1"],
            "list.activeSelectionForeground": palette["text"],
            "list.hoverBackground": palette["surface0"],
            "list.focusBackground": palette["surface1"],
            "list.highlightForeground": palette["iris"],
            "gitDecoration.modifiedResourceForeground": palette["iris"],
            "gitDecoration.deletedResourceForeground": palette["love"],
            "gitDecoration.untrackedResourceForeground": blend(palette["pine"], palette["surface1"], 0.4),
            "gitDecoration.conflictingResourceForeground": palette["peach"],
            "gitDecoration.ignoredResourceForeground": palette["subtext0"],
            "diffEditor.insertedTextBackground": palette["pine"] + "20",
            "diffEditor.removedTextBackground": palette["love"] + "20",
        },
        "tokenColors": [
            {
                "scope": ["comment", "punctuation.definition.comment"],
                "settings": {
                    "foreground": palette["subtext0"],
                    "fontStyle": "italic"
                }
            },
            {
                "scope": [
                    "keyword",
                    "keyword.control",
                    "keyword.operator.new",
                    "keyword.operator.expression",
                    "storage",
                    "storage.type",
                    "storage.modifier"
                ],
                "settings": {
                    "foreground": palette["rose"]
                }
            },
            {
                "scope": [
                    "entity.name.function",
                    "support.function",
                    "meta.function-call"
                ],
                "settings": {
                    "foreground": palette["iris"]
                }
            },
            {
                "scope": [
                    "string",
                    "string.quoted",
                    "string.template"
                ],
                "settings": {
                    "foreground": palette["pine"]
                }
            },
            {
                "scope": [
                    "entity.name.type",
                    "entity.other.inherited-class",
                    "support.type",
                    "support.class"
                ],
                "settings": {
                    "foreground": palette["gold"]
                }
            },
            {
                "scope": [
                    "constant.numeric",
                    "constant.language"
                ],
                "settings": {
                    "foreground": palette["peach"]
                }
            },
            {
                "scope": ["variable.other", "variable.language"],
                "settings": {
                    "foreground": palette["text"]
                }
            },
            {
                "scope": ["variable.parameter", "variable.other.readwrite"],
                "settings": {
                    "foreground": palette["text"]
                }
            },
            {
                "scope": ["entity.name.tag"],
                "settings": {
                    "foreground": palette["rose"]
                }
            },
            {
                "scope": ["entity.other.attribute-name"],
                "settings": {
                    "foreground": palette["gold"]
                }
            },
            {
                "scope": ["punctuation"],
                "settings": {
                    "foreground": palette["subtext0"]
                }
            },
            {
                "scope": ["keyword.operator"],
                "settings": {
                    "foreground": palette["subtext0"]
                }
            },
            {
                "scope": ["support.constant"],
                "settings": {
                    "foreground": palette["peach"]
                }
            },
            {
                "scope": ["entity.name.class", "entity.name.type.class"],
                "settings": {
                    "foreground": palette["gold"]
                }
            },
            {
                "scope": ["entity.name.namespace"],
                "settings": {
                    "foreground": palette["gold"]
                }
            },
            {
                "scope": ["markup.heading", "entity.name.section"],
                "settings": {
                    "foreground": palette["iris"],
                    "fontStyle": "bold"
                }
            },
            {
                "scope": ["markup.italic"],
                "settings": {
                    "fontStyle": "italic"
                }
            },
            {
                "scope": ["markup.bold"],
                "settings": {
                    "fontStyle": "bold"
                }
            },
            {
                "scope": ["markup.deleted"],
                "settings": {
                    "foreground": palette["love"]
                }
            },
            {
                "scope": ["markup.inserted"],
                "settings": {
                    "foreground": palette["pine"]
                }
            },
            {
                "scope": ["markup.changed"],
                "settings": {
                    "foreground": palette["gold"]
                }
            },
        ]
    }

    theme_json = json.dumps(theme, indent=4)
    ext_path = vscode_ext_dir / "morandi.json"
    ext_path.write_text(theme_json)
    user_path = vscode_user_dir / "morandi.json"
    user_path.write_text(theme_json)
    print(f"VSCode Morandi theme written to {ext_path} and {user_path}")


def write_krita(palette):
    """Generate Krita Morandi color scheme (.colors) and theme JSON."""
    krita_colors_dir = Path.home() / ".local/share/krita/color-schemes"
    krita_colors_dir.mkdir(parents=True, exist_ok=True)
    scheme_file = krita_colors_dir / "Morandi-System.colors"

    def rgb_str(hex_c):
        h = hex_c.lstrip("#")
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

    bg = palette["base"]
    bg_alt = palette["surface0"]
    fg = palette["text"]
    fg_inact = palette["subtext0"]
    highlight = palette["iris"]
    negative = palette["love"]
    neutral = palette["gold"]
    positive = palette["pine"]

    bg_rgb = rgb_str(bg)
    bg_alt_rgb = rgb_str(bg_alt)
    fg_rgb = rgb_str(fg)
    fg_inact_rgb = rgb_str(fg_inact)
    hl_rgb = rgb_str(highlight)
    neg_rgb = rgb_str(negative)
    neu_rgb = rgb_str(neutral)
    pos_rgb = rgb_str(positive)

    content = f"""[ColorEffects:Disabled]
Color={bg_rgb}
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=false
Color={fg_inact_rgb}
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Complementary]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Header]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Selection]
BackgroundAlternate={hl_rgb}
BackgroundNormal={hl_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={bg_rgb}
ForegroundInactive={bg_rgb}
ForegroundLink={bg_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={bg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={bg_rgb}

[Colors:Tooltip]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:View]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Window]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[General]
ColorScheme=Morandi-System
Name=Morandi System
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={bg_rgb}
activeBlend={fg_rgb}
activeForeground={fg_rgb}
inactiveBackground={bg_alt_rgb}
inactiveBlend={fg_inact_rgb}
inactiveForeground={fg_inact_rgb}
"""
    scheme_file.write_text(content)

    json_path = Path.home() / ".config/krita/morandi_theme.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    theme_data = {
        "highlight": highlight,
        "background": bg,
        "alternate": bg_alt,
        "text": fg,
        "inactive_text": fg_inact,
        "iris": palette.get("iris", "#8c829e"),
        "gold": palette.get("gold", "#bfa980"),
        "rose": palette.get("rose", "#c48c90"),
        "pine": palette.get("pine", "#7b9c90"),
        "foam": palette.get("foam", "#809c95"),
        "peach": palette.get("peach", "#c79685"),
        "sky": palette.get("sky", "#7f9bb0")
    }
    json_path.write_text(json.dumps(theme_data, indent=2))


def write_tvp_timeline(palette):
    """Generate TVP Timeline Morandi theme JSON config."""
    json_path = Path.home() / ".config/krita/tvp_timeline_morandi.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    theme_data = {
        "bg_dark": palette.get("base", "#1a1a18"),
        "bg_alt": palette.get("mantle", "#222220"),
        "surface0": palette.get("surface0", "#2c2c29"),
        "surface1": palette.get("surface1", "#363632"),
        "border": palette.get("overlay0", "#444440"),
        "text": palette.get("text", "#dededd"),
        "subtext": palette.get("subtext0", "#a5a5a0"),
        "iris": palette.get("iris", "#afac9c"),
        "gold": palette.get("gold", "#bdb79a"),
        "rose": palette.get("rose", "#c25f63"),
        "pine": palette.get("pine", "#a8aba0"),
        "foam": palette.get("foam", "#acac9f"),
        "peach": palette.get("peach", "#c2725f"),
        "sky": palette.get("sky", "#a9aba0")
    }
    json_path.write_text(json.dumps(theme_data, indent=2))




def write_krita_tvp(palette):
    import json
    from pathlib import Path
    out_path = Path.home() / ".local/share/krita/pykrita/tvp_timeline/morandi_colors.json"
    if out_path.parent.exists():
        out_path.write_text(json.dumps(palette, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallpaper", help="Path to current wallpaper for limine sync")
    args = parser.parse_args()

    if not NOCTALIA_COLORS.exists():
        print(f"Error: {NOCTALIA_COLORS} not found")
        sys.exit(1)

    with open(NOCTALIA_COLORS) as f:
        colors = json.load(f)

    palette = generate_palette(colors)
    write_niri(palette)
    write_mango(palette)
    write_starship(palette)
    write_fcitx5(palette)
    write_fastfetch(palette)
    write_alacritty(palette)
    write_kde(colors)
    write_obs(palette)
    write_clash_verge(palette)
    write_cava(palette)
    write_flclash(palette)
    write_libswell(palette)
    write_zed(palette)
    write_vscode(palette)

    apply_system_changes(args.wallpaper)
    
    try:
        write_blender(palette)
    except Exception as e:
        print(f"Failed to write blender theme: {e}")
        
    try:
        write_krita_tvp(palette)
    except Exception as e:
        print(f"Failed to write krita tvp theme: {e}")
        
    try:
        write_godot(palette)
    except Exception as e:
        print(f"Failed to write godot theme: {e}")
        
    try:
        write_krita(palette)
    except Exception as e:
        print(f"Failed to write krita theme: {e}")

    try:
        write_tvp_timeline(palette)
    except Exception as e:
        print(f"Failed to write tvp_timeline theme: {e}")


    try:
        write_obs(palette)
    except Exception as e:
        print(f"Failed to write obs theme: {e}")

    write_opencode(palette)
    write_antigravity(palette)
    write_ly(palette)
    
    apply_system_changes(args.wallpaper)
    print("Morandi theme generated and system changes applied successfully.")

if __name__ == "__main__":
    main()
