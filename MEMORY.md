# Configuration Memory

This file serves as a live context buffer for AI agents. It tracks the current state of LanRhyme's system configuration, recent structural decisions, and ongoing tasks to ensure smooth handoffs between sessions.

## Current Setup State
- **Theming**: Handled globally by `~/.config/noctalia/morandi-gen.py` (Morandi colors). Avoid breaking structural CSS in UI-heavy apps.

## Ongoing Configuration Tasks
- *[Add current configuration tasks here]*

## Structural Patterns
- Dotfiles are managed via `chezmoi` in `~/.local/share/chezmoi`.
- Always sync changes using `~/.local/bin/dotfiles-sync.sh`.
