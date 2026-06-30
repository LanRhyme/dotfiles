# Agent Memory File

This file stores long-term memory, system quirks, and user preferences discovered during operations. AI Agents should consult this file before undertaking complex tasks and append new findings when appropriate.

## System Quirks & Software Setup
- **Zrythm DAW**: Zrythm 1.0+ has dropped support for VST2 plugins natively. If the user wants to load VST2 plugins (e.g., Cakewalk plugins like BREVERB), they must load the `Carla Rack` or `Carla Patchbay` plugin inside Zrythm and host the VST2 plugins via Carla.
- **Zrythm Audio**: Zrythm may default to `none` for audio/MIDI backends. If there is no sound, set the `audio-backend` to `pulseaudio` and `midi-backend` to `alsa` using `gsettings`.
- **Zrythm Theming**: Do NOT modify Zrythm's internal `background-color` or structural CSS via `morandi-gen.py`, as it breaks the Libadwaita layout. Only override `@define-color accent_color` and `accent_bg_color`.
- **VST Bridging**: Windows `.dll` plugins must be bridged using `yabridge` to be visible to Linux hosts. Run `yabridgectl sync` after adding paths.

## User Preferences
- **Morandi Colors**: The user prefers the cool-toned "Iris" (purple/blue) as the accent color over warm tones like "Rose" (red/orange).
- **Writing**: Never use full stops (periods) or emojis in markdown documentation.
