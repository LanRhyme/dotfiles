# Configuration Memory

This file serves as a live context buffer for AI agents. It tracks the current state of LanRhyme's system configuration, recent structural decisions, and ongoing tasks to ensure smooth handoffs between sessions.

## Current Setup State
- **Theming**: Handled globally by `~/.config/noctalia/morandi-gen.py` (Morandi colors). Avoid breaking structural CSS in UI-heavy apps.

## Ongoing Configuration Tasks
- Integrated `clash-verge-rev` and `flclash` into the Morandi global theme engine. `flclash` leverages Material 3 dynamic color generated from the injected primary color, while `clash-verge-rev` uses a detailed CSS override block injected via `verge.yaml`. Both require full process restarts (`kill -9` or via service) after updating the configuration files to apply changes.
- Integrated `VSCode` into the Morandi theme engine: full `workbench.colorCustomizations` (~200+ tokens covering sidebar, tabs, terminal ANSI, status bar, menus, input, buttons, git, debug, notifications, diff editor, peek view, scrollbar, breadcrumbs, quick input, settings, command center, keybindings, etc.) plus `editor.tokenColorCustomizations` (~48 rules covering keywords, functions, types, strings, numbers, comments, variables, and language-specific scopes for Python, JS/TS, C/C++, CSS, Rust, Go, Lua). Transparent elements (editor/tab/sidebar/activityBar/panel backgrounds) kept as `#00000000` for `vscode_vibrancy` compatibility. Syntax palette uses warm Morandi-adjusted hues (#c09a7c keywords, #b0c4a0 strings, #c4b488 numbers, #9aafc0 types).

## Structural Patterns
- Dotfiles are managed via `chezmoi` in `~/.local/share/chezmoi`.
- Always sync changes using `~/.local/bin/dotfiles-sync.sh`.
