<div align="center">
  
  <h1>noctalia-plugin-micyou</h1>
  
  <b>简体中文</b> | <a href="./README.md">English</a>

  <br>
  <br>

  <a href="https://github.com/LanRhyme/MicYou"><img alt="MicYou 主仓库" src="https://img.shields.io/badge/MicYou-主仓库-89a484?style=flat&logo=github&logoColor=white"></a>
  <a href="https://github.com/LanRhyme/noctalia-plugin-micyou/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <a href="https://qm.qq.com/q/V16hPpWPKO"><img alt="QQ" src="https://img.shields.io/badge/QQ-995452107-12B7F5?style=flat&logo=qq&logoColor=white"></a>
  <a href="https://t.me/MicYouChannel"><img alt="TG" src="https://img.shields.io/badge/Telegram-@MicYouChannel-2CA5E0?style=flat&logo=telegram&logoColor=white"></a>

  <h6>赞助我</h6>

  <a href="https://afdian.com/a/LanRhyme" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/爱发电-@LanRhyme-946ce6?style=for-the-badge&logo=afdian&logoColor=white" alt="爱发电"></a>

  <br>

  [MicYou](https://github.com/LanRhyme/MicYou) 官方专属 Noctalia 5 桌面 Shell 控制与动态音量环插件

  实时音频动态音量环 · 附着式交互控制面板 · 无头后台 CLI 服务 · 控制中心快捷卡片

</div>

## 插件介绍

本插件是 [MicYou](https://github.com/LanRhyme/MicYou) 官方生态的附属组件，专为 Noctalia 5 桌面环境打造

无需常驻打开桌面 GUI 窗口，即可在状态栏与桌面 Shell 中直接监控与控制 MicYou 音频服务

- **状态栏动态音量环**：将状态栏图标转换为实时动态音量环，说话声音大小随声音电平实时张开与回落
- **原生附着式控制面板**：点击快速展开面板，调节 Wi-Fi / USB / Web 模式、麦克风增益与 AI 智能降噪
- **无头后台守护控制**：直接管理超低内存占用的 `micyou` 后台 CLI 守护进程，零多余子进程轮询开销
- **控制中心卡片集成**：支持在 Noctalia 控制中心内一键快速启停服务

## 软件截图

<div align="center">
  <img src="img/screenshot.png" width="480" alt="MicYou Noctalia 插件截图" />
</div>

## 主要功能

- 复刻 Tauri 端 AudioRing 算法，基于 21 阶 GPU 纹理缓存矢量圆弧帧与 Lerp 插值实现丝滑的实时声音动态反馈
- 纯后台无头守护服务，通过读取进程状态与流式解析监听实时音频电平，零多余子进程开销
- 原生附着式交互控制面板
  - 自由切换 Wi-Fi、USB (ADB) 与 Web 连接模式
  - 实时麦克风增益 Gain 滑块调节（0 至 30 dB）
  - AI 智能降噪 PureVox 一键开关
  - TUI 终端模式与桌面端 GUI 快速唤起入口
- 控制中心快捷开关卡片支持
- 全局自动同步当前桌面的莫兰迪动态配色

## 环境依赖

本插件依赖系统中已安装 `micyou` 或 `micyou-cli` 核心命令行工具：

```bash
# Arch Linux (AUR)
paru -S micyou-bin
```

## 安装指南

1. 克隆或软链接本仓库至 Noctalia 插件目录：

```bash
git clone https://github.com/LanRhyme/noctalia-plugin-micyou ~/.config/noctalia/plugins/micyou
```

2. 在 `~/.config/noctalia/settings.toml` 中启用插件：

```toml
[plugins]
enabled = [
  "lanrhyme/micyou"
]
```

3. 在 `~/.config/noctalia/settings.toml` 中将小部件添加到状态栏：

```toml
[bar]
widgets = [
  "lanrhyme/micyou:widget"
]
```

## 交互手势

- 鼠标左键：打开或关闭附着式控制面板
- 鼠标右键：快速启动或停止 MicYou 服务
- 鼠标中键：在终端中打开 TUI 控制台

## 开源协议

MIT License
