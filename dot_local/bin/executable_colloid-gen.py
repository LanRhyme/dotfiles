#!/usr/bin/env python3
import os
import sys
import argparse
from PIL import Image, ImageDraw

def get_dominant_color(img):
    img = img.convert("RGBA")
    # Resize to 50x50 to speed up and average out noise
    img_small = img.resize((50, 50))
    colors = img_small.getcolors(50 * 50)
    
    max_count = 0
    dominant_color = (44, 44, 44)
    
    if colors:
        for count, color in colors:
            r, g, b, a = color
            if a < 50:
                continue
            brightness = (r*299 + g*587 + b*114) / 1000
            # Ignore completely white or black backgrounds to find actual icon color
            if 20 < brightness < 240:
                if count > max_count:
                    max_count = count
                    dominant_color = (r, g, b)
                    
        if max_count == 0:
            # Fallback to average color
            r_sum, g_sum, b_sum, count = 0, 0, 0, 0
            for count_i, color in colors:
                r, g, b, a = color
                if a >= 50:
                    r_sum += r * count_i
                    g_sum += g * count_i
                    b_sum += b * count_i
                    count += count_i
            if count > 0:
                dominant_color = (r_sum // count, g_sum // count, b_sum // count)
            
    return dominant_color

def create_squircle_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask

def generate_icon(input_path, output_name, bg_color_hex=None, padding_ratio=0.6, theme_dir="Colloid-Dark"):
    original_input = input_path
    tmp_png = None
    
    if input_path.lower().endswith(".svg"):
        tmp_png = f"/tmp/{output_name}_tmp.png"
        print("Converting SVG to PNG...")
        os.system(f"magick -background none -resize 512x512 '{input_path}' '{tmp_png}'")
        input_path = tmp_png

    try:
        fg_img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening input image: {e}")
        sys.exit(1)

    size = 512
    radius = 115 # iOS-like squircle corner radius

    if bg_color_hex:
        bg_color_hex = bg_color_hex.lstrip('#')
        if len(bg_color_hex) == 3:
            bg_color_hex = "".join([c*2 for c in bg_color_hex])
        bg_color = tuple(int(bg_color_hex[i:i+2], 16) for i in (0, 2, 4))
    else:
        bg_color = get_dominant_color(fg_img)

    bg_img = Image.new("RGBA", (size, size), bg_color + (255,))
    mask = create_squircle_mask((size, size), radius)
    
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    icon.paste(bg_img, (0, 0), mask)

    fg_w, fg_h = fg_img.size
    aspect = fg_w / fg_h
    target_dim = int(size * padding_ratio)
    
    if fg_w > fg_h:
        new_w = target_dim
        new_h = int(target_dim / aspect)
    else:
        new_h = target_dim
        new_w = int(target_dim * aspect)
        
    fg_img = fg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    paste_x = (size - new_w) // 2
    paste_y = (size - new_h) // 2
    
    icon.paste(fg_img, (paste_x, paste_y), fg_img)

    save_dir = os.path.expanduser(f"~/.local/share/icons/{theme_dir}/apps/scalable")
    if not os.path.exists(save_dir):
        save_dir = os.path.expanduser(f"~/.local/share/icons/hicolor/512x512/apps")
        os.makedirs(save_dir, exist_ok=True)
        
    output_path = os.path.join(save_dir, f"{output_name}.png")
    
    icon.save(output_path)
    print(f"✅ Icon successfully generated and saved to: {output_path}")
    print(f"   Background color used: rgb{bg_color}")
    
    if tmp_png and os.path.exists(tmp_png):
        os.remove(tmp_png)
        
    print("🔄 Updating icon cache...")
    os.system(f"gtk-update-icon-cache -f -t ~/.local/share/icons/{theme_dir} >/dev/null 2>&1")
    os.system("killall noctalia 2>/dev/null && noctalia &")
    print("✅ Done! Noctalia has been restarted to apply changes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Colloid-style flat squircle icon for a missing app.")
    parser.add_argument("input", help="Path to the original icon image (PNG or SVG)")
    parser.add_argument("name", help="The application/icon name (e.g., 'qq', 'netease-cloud-music')")
    parser.add_argument("--bg", help="Background hex color (e.g., '#FF5555'). If omitted, extracts dominant color.", default=None)
    parser.add_argument("--ratio", help="Padding ratio for the inner icon (default: 0.6)", type=float, default=0.6)
    parser.add_argument("--theme", help="Target icon theme folder", default="Colloid-Dark")
    
    args = parser.parse_args()
    generate_icon(args.input, args.name, args.bg, args.ratio, args.theme)
