# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录 LanRhyme 系统配置的当前状态、近期结构决策和进行中的任务，以确保会话间的平滑交接

## 当前配置状态
- **主题化**: 全局由 `~/.config/noctalia/morandi-gen.py` 处理（莫兰迪色系）。避免破坏 UI 密集型应用的结构化 CSS
- **Niri 动画**: 在 `~/.config/niri/cfg/animation.kdl` 中调优为较慢、弹性轻柔的滑行（stiffness=180-220, damping-ratio=0.8），确保流畅的过渡手感
- **Niri 窗口间距**: 在 `~/.config/niri/cfg/layout.kdl` 中从 12px 缩小到 8px，优化屏幕布局空间
- **Niri 透明度**: 全局窗口规则设置 `opacity 0.9` + `blur true`（Krita 除外）。关键点: 必须设置 `draw-border-with-background false`，否则 niri 会在窗口后方渲染为实心矩形边框，透过半透明窗口显示出来，导致聚焦时窗口看起来不透明
- **Zen 浏览器 (Flatpak)**: 通过 `flatpak override` 配合 NVIDIA 环境变量（`__NV_PRIME_RENDER_OFFLOAD=1`、`__GLX_VENDOR_LIBRARY_NAME=nvidia` 等）实现 GPU 加速。fcitx5 主题修复通过 D-Bus talk 权限（`org.fcitx.Fcitx5`、`org.freedesktop.portal.Fcitx`）和对 `~/.local/share/fcitx5` 及 `~/.config/fcitx5` 的只读文件系统访问实现。Zen `user.js` 已强制开启 WebRender、DMA-BUF、硬件视频解码
- **fcitx5 默认输入法**: `profile` 文件中的 `DefaultIM` 会被 fcitx5 进程在关闭/重启时从运行时状态覆盖回去，编辑 `profile` 不会持久生效。需要通过 `~/.config/fcitx5/config` 或 `fcitx5-remote -s` 来设置默认输入法



## 进行中的配置任务
- 已将 `Reaper` 集成到莫兰迪全局主题引擎: 在 `morandi-gen.py` 中添加了 `write_reaper`，动态生成 `Morandi.ReaperTheme` 用莫兰迪色板覆盖 UI 和轨道颜色，并配置 `reaper.ini` 使用该主题及中文语言包
- 已将 `clash-verge-rev` 和 `flclash` 集成到莫兰迪全局主题引擎。`flclash` 利用注入主色生成的 Material 3 动态颜色，`clash-verge-rev` 通过 `verge.yaml` 注入详细的 CSS 覆盖块。两者都需要在更新配置文件后完全重启进程（`kill -9` 或通过服务）才能生效
- 已将 `VSCode` 集成到莫兰迪主题引擎: 完整的 `workbench.colorCustomizations`（200+ 标记）+ `editor.tokenColorCustomizations`（48 条规则）。语法色板使用 `_light` 变体同步到 Neovim morandi 主题（关键字=#d47a7e rose_light、字符串=#c0c3b8 green_light、类型=#d5cfb2 yellow_light、函数=#c4c4b7 blue_light、常量=#d4907e mauve_light、预处理器=#c5c2b2 violet_light）。为 `vscode_vibrancy` 保留透明元素。VSCode 通过 `~/.vscode/argv.json`（`"ozone-platform": "x11"`）强制使用 XWayland
- 已将 `cava` 集成到莫兰迪全局主题引擎: 在 `morandi-gen.py` 中添加了 `write_cava`，动态生成 `~/.config/cava/themes/morandi`（8 色渐变，从冷色到暖色莫兰迪色），并通过向进程发送 `USR2` 信号自动重载 Cava 颜色; 同时优化了 `~/.config/cava/config`，使用 144Hz 帧率、Monstercat 平滑、细条（width=2, spacing=1）、居中对齐和同步 sync，实现流畅的 Wayland 终端渲染
- **SPlayer 桌面歌词**: 在 `config.kdl` 中添加窗口规则（必须在全局 opacity 规则之后才能生效），匹配 `app-id="splayer" title=".*桌面歌词.*"`，设置 `open-floating true`、`opacity 1.0`、`blur false`，解决歌词背景透过窗口显示的问题
- 已将 `Zed` 集成到莫兰迪主题引擎: 在 `morandi-gen.py` 中添加了 `write_zed`，动态生成 `~/.config/zed/themes/morandi.json`。语法和 UI 颜色映射到莫兰迪色板以模拟 Neovim 主题，并更新了 `~/.config/zed/settings.json` 设置主题为莫兰迪
- 已将 `Blender` 集成到莫兰迪主题引擎: 在 `morandi-gen.py` 中添加了 `write_blender`，基于 Eclipse 主题 XML 模板通过字符串替换生成莫兰迪主题。XML 方式覆盖所有属性（Python API 在 Blender 5.1 中 `save_userpref()` 无法保存所有主题属性）。基线文件: `~/.config/noctalia/blender-eclipse-theme.xml`，输出: `~/.config/blender/5.1/scripts/presets/interface_theme/Morandi.xml`，通过 `bpy.ops.preferences.theme_install()` 自动安装
- 已修复 Alacritty 终端偏蓝问题并完全集成到莫兰迪主题引擎: 修复了 `morandi-gen.py` 中 `write_alacritty` 使用硬编码基础色且未清理 `themes/noctalia.toml` 中残留 Catppuccin Mocha 高饱和蓝色（`#89B4FA`）的问题；重构了 `write_alacritty(palette)`，使 Alacritty 的 primary、normal、bright 和 dim 调色板完整绑定到莫兰迪 `palette`（如 iris、sky、pine、gold 等暖色调），解决加粗文本和语法高亮偏蓝的问题

## 结构模式
- Dotfiles 通过 `chezmoi` 管理，源位于 `~/.local/share/chezmoi`
- 始终使用 `~/.local/bin/dotfiles-sync.sh` 同步变更
- 已为 Noctalia 5 编写并启用了 `clipboard-osd` 插件（利用 `wl-paste` 监听并在复制时弹出 OSD/通知），配置已同步到 chezmoi
