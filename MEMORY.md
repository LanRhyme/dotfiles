# Configuration Memory

This file serves as a live context buffer for AI agents. It tracks the current state of LanRhyme's system configuration, recent structural decisions, and ongoing tasks to ensure smooth handoffs between sessions.

## Current Setup State
- **Theming**: Handled globally by `~/.config/noctalia/morandi-gen.py` (Morandi colors). Avoid breaking structural CSS in UI-heavy apps
- **Niri Animations**: Tuned to a slower, springy gentle glide (stiffness=180-220, damping-ratio=0.8) in `~/.config/niri/cfg/animation.kdl` to ensure fluid transition feel
- **Niri Window Gaps**: Shrunk from 12px to 8px in `~/.config/niri/cfg/layout.kdl` to optimize screen layout space







## Ongoing Configuration Tasks
- Integrated `clash-verge-rev` and `flclash` into the Morandi global theme engine. `flclash` leverages Material 3 dynamic color generated from the injected primary color, while `clash-verge-rev` uses a detailed CSS override block injected via `verge.yaml`. Both require full process restarts (`kill -9` or via service) after updating the configuration files to apply changes.
- Integrated `VSCode` into the Morandi theme engine: full `workbench.colorCustomizations` (200+ tokens) + `editor.tokenColorCustomizations` (48 rules). Syntax palette synced to Neovim morandi theme using `_light` variants (keywords=#d47a7e rose_light, strings=#c0c3b8 green_light, types=#d5cfb2 yellow_light, functions=#c4c4b7 blue_light, constants=#d4907e mauve_light, preprocessor=#c5c2b2 violet_light). Transparent elements preserved for `vscode_vibrancy`. VSCode forced to XWayland via `~/.vscode/argv.json` (`"ozone-platform": "x11"`).
- Integrated `cava` into the Morandi global theme engine by adding `write_cava` to `morandi-gen.py` which dynamically generates `~/.config/cava/themes/morandi` with an 8-color gradient (cool-to-warm Morandi colors) and reloads Cava's colors automatically by sending a `USR2` signal to the process; also optimized `~/.config/cava/config` for smooth Wayland terminal rendering using 144Hz framerate, Monstercat smoothing, thin bars (width=2, spacing=1), center alignment, and synchronized sync

## Structural Patterns
- Dotfiles are managed via `chezmoi` in `~/.local/share/chezmoi`.
- Always sync changes using `~/.local/bin/dotfiles-sync.sh`.
