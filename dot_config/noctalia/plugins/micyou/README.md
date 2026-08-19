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

  MicYou control and dynamic audio level monitor plugin for Noctalia 5 Shell

  Real-time audio level ring · Attached control panel · Background CLI daemon · Control Center shortcut

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

## Installation

Clone or link this repository into your Noctalia plugins directory:

```bash
git clone https://github.com/LanRhyme/noctalia-plugin-micyou ~/.config/noctalia/plugins/micyou
```

Enable the plugin in `~/.config/noctalia/settings.toml`:

```toml
[plugins]
enabled = [
  "lanrhyme/micyou"
]
```

Add the widget to your bar configuration in `~/.config/noctalia/settings.toml`:

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

## Main Project

This plugin is part of the [MicYou](https://github.com/LanRhyme/MicYou) ecosystem

## License

MIT License
