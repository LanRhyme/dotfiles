# LanRhyme's System Guidelines for AI Agents

These rules define the user's system architecture, preferences, and mandatory procedures for configuring or modifying the environment. All agents must follow these instructions closely.

## 1. System Architecture & Package Management
- **OS**: Arch Linux (CachyOS).
- **Package Managers**: Use `paru` for AUR packages and `pacman` for official repositories. Use `--noconfirm` when installing packages.
- **Display Server & WM**: Wayland + `niri` (compositor).
- **Desktop Elements**: `noctalia` (status bar), `kando` (pie menus).

## 2. Global Theming Engine (Morandi Theme)
- The system uses a centralized, dynamic theme generator written in Python that hooks into wallpaper changes to generate "Morandi" (low saturation, warm/cool) colors.
- **Core Script Location**: `~/.config/noctalia/morandi-gen.py`
- **Rule**: If requested to theme a new application or modify UI colors, **DO NOT** edit the application's config files directly in isolation. Instead, you MUST extend `morandi-gen.py`. Add a `write_<app>` function that parses the application's config and injects the `palette` dictionary colors, call it in `main()`, and run the script. This ensures the app syncs automatically with future wallpaper changes.

## 3. Configuration Management (Chezmoi)
- **Tool**: `chezmoi` is used to manage dotfiles.
- **Source Repository**: `~/.local/share/chezmoi`
- **Rule**: When modifying system configuration files (e.g., `~/.config/app/config`), you must ensure the changes are committed to the dotfiles repository. A dedicated sync script is provided at `~/.local/bin/dotfiles-sync.sh`. Run this script immediately after applying and testing any dotfile modifications.
- **Rule**: If you edit scripts directly in `~/.config`, remember to edit the source in `~/.local/share/chezmoi` first and copy it over, or run `chezmoi re-add` if you edit the local copy.

## 4. Documentation & Writing Preferences
- **Formatting Rule**: **NEVER** use full stops/periods (句号) and **NEVER** use emojis when writing or updating `README.md` files or markdown documentation. Keep it clean and minimalist.
- **Tone**: Keep conversational responses concise, direct, and professional.

## 5. Storage & File System
- The system has access to Windows partitions:
  - Windows C Drive: `/mnt/WindowsC`
  - Windows D Drive: `/mnt/WindowsD`
- When searching for external VSTs, games, or Windows configurations, always check these mount points.

## 6. Auto-Memory & Context Retention (MEMORY.md)
- **Concept**: To prevent repeating the same mistakes and to build long-term context, agents must use a centralized memory file.
- **Location**: `~/MEMORY.md`
- **Read Rule**: Whenever starting a new complex task or troubleshooting an issue, you MUST quickly scan `~/MEMORY.md` to see if there are any documented solutions, user preferences, or past quirks related to the task.
- **Write Rule**: If you solve a difficult environment issue (e.g., undocumented paths, dependency conflicts, or weird software behaviors) or if the user explicitly asks you to "remember" something, you MUST summarize it concisely and append it to `~/MEMORY.md`. Do not overwrite existing memory unless it is explicitly obsolete.
