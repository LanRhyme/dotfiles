<div align="center">
  
  <h1>noctalia-plugin-micyou</h1>
  
  <a href="./README_zh-cn.md">简体中文</a> | <b>English</b>

  <br>
  <br>

  <a href="https://github.com/LanRhyme/MicYou"><img alt="MicYou Main Repo" src="https://img.shields.io/badge/MicYou-Main%20Repo-89a484?style=flat&logo=github&logoColor=white"></a>
  <a href="https://github.com/LanRhyme/noctalia-plugin-micyou/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <a href="https://qm.qq.com/q/V16hPpWPKO"><img alt="QQ" src="https://img.shields.io/badge/QQ-995452107-12B7F5?style=flat&logo=qq&logoColor=white"></a>
  <a href="https://t.me/MicYouChannel"><img alt="TG" src="https://img.shields.io/badge/Telegram-@MicYouChannel-2CA5E0?style=flat&logo=telegram&logoColor=white"></a>

  <h6>Support Me</h6>

  <a href="https://afdian.com/a/LanRhyme" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/afdian-@LanRhyme-946ce6?style=for-the-badge&logo=afdian&logoColor=white" alt="afdian"></a>

  <br>

  Official companion plugin for [MicYou](https://github.com/LanRhyme/MicYou) on Noctalia 5 Desktop Shell

  Real-time audio level ring · Attached control panel · Headless CLI daemon · Control Center shortcut

</div>

## Overview

This plugin is an official companion component of the [MicYou](https://github.com/LanRhyme/MicYou) ecosystem, designed specifically for the Noctalia 5 desktop shell

It brings native desktop status bar integration and streamlined service management for MicYou without needing to keep the full desktop GUI window open

- **Status Bar Audio Meter**: Transforms the status bar icon into a real-time animated volume ring that dynamically pulses with your voice input
- **Native Control Panel**: Click to open a lightweight attached panel to switch Wi-Fi, USB, and Web connection modes, adjust gain, and toggle AI noise reduction
- **Headless Daemon Control**: Manages the low-overhead `micyou` background CLI service with zero unnecessary subprocess polling
- **Control Center Integration**: Provides a quick toggle card in the Noctalia Control Center

## Screenshot

<div align="center">
  <img src="img/screenshot.png" width="480" alt="MicYou Noctalia Plugin Screenshot" />
</div>

## Features

- Dynamic audio level ring replicated from Tauri AudioRing with 21 GPU-cached vector arc frames and lerp interpolation
- Background headless daemon management for `micyou` CLI with zero extra subprocess polling
- Native attached interactive control panel
  - Switch connection mode between Wi-Fi, USB (ADB), and Web
  - Real-time Gain slider adjustment (0 to 30 dB)
  - AI Noise Suppression toggle (PureVox)
  - Fast entrance for TUI terminal console and desktop GUI
- Quick toggle shortcut card for Noctalia Control Center
- Automatic Morandi theme color synchronization

## Prerequisites

This plugin relies on the `micyou` or `micyou-cli` core binary installed on your system:

```bash
# Arch Linux (AUR)
paru -S micyou-bin
```

## Installation

1. Clone or link this repository into your Noctalia plugins directory:

```bash
git clone https://github.com/LanRhyme/noctalia-plugin-micyou ~/.config/noctalia/plugins/micyou
```

2. Enable the plugin in `~/.config/noctalia/settings.toml`:

```toml
[plugins]
enabled = [
  "lanrhyme/micyou"
]
```

3. Add the widget to your bar configuration in `~/.config/noctalia/settings.toml`:

```toml
[bar]
widgets = [
  "lanrhyme/micyou:widget"
]
```

## Gestures

- Left Click: Toggle attached control panel
- Right Click: Toggle service start or stop
- Middle Click: Launch TUI terminal console

## License

MIT License
