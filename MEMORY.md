# Configuration Memory

This file serves as a live context buffer for AI agents. It tracks the current state of LanRhyme's system configuration, recent structural decisions, and ongoing tasks to ensure smooth handoffs between sessions.

## Current Setup State
- **Theming**: Handled globally by `~/.config/noctalia/morandi-gen.py` (Morandi colors). Avoid breaking structural CSS in UI-heavy apps.

## Ongoing Configuration Tasks
- Integrated `clash-verge-rev` and `flclash` into the Morandi global theme engine. `flclash` leverages Material 3 dynamic color generated from the injected primary color, while `clash-verge-rev` uses a detailed CSS override block injected via `verge.yaml`. Both require full process restarts (`kill -9` or via service) after updating the configuration files to apply changes.
- Integrated `VSCode` into the Morandi theme engine via `workbench.colorCustomizations` injection, including full UI coverage (sidebar, tabs, terminal ANSI colors, status bar, menus, input, buttons, git decorations, peek view, etc.). Transparent elements (editor background, tabs, sidebar, activity bar, panel, minimap) are kept as `#00000000` to preserve `vscode_vibrancy` compatibility.

## Structural Patterns
- Dotfiles are managed via `chezmoi` in `~/.local/share/chezmoi`.
- Always sync changes using `~/.local/bin/dotfiles-sync.sh`.
