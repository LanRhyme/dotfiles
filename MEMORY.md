# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录 LanRhyme 系统配置的当前状态、近期结构决策和进行中的任务，以确保会话间的平滑交接

## 当前配置状态

- **显示管理器**: 已替换为 `greetd` + `noctalia-greeter` (Noctalia 官方原生图形化 Greeter)。通过 `greetd.service` 运行。其主题美化（壁纸、莫兰迪色板）和多显示器布局完全依赖于 Noctalia Shell 的图形界面同步功能（设置 -> Shell -> 安全 -> Noctalia Greeter -> Sync Now）。
- **主题化**: 全局由 `~/.config/noctalia/morandi-gen.py` 处理（莫兰迪色系）。避免破坏 UI 密集型应用的结构化 CSS。具体情况具体分析，部分应用主题不由其管理，像是krita。
- **Niri 动画**: 在 `~/.config/niri/cfg/animation.kdl` 中调优为较慢、弹性轻柔的滑行（stiffness=180-220, damping-ratio=0.8），确保流畅的过渡手感
- **Niri 窗口间距**: 在 `~/.config/niri/cfg/layout.kdl` 中从 12px 缩小到 8px，优化屏幕布局空间
- **Niri 透明度**: 全局窗口规则设置 `opacity 0.9` + `blur true`（Krita 除外）。关键点: 必须设置 `draw-border-with-background false`，否则 niri 会在窗口后方渲染为实心矩形边框，透过半透明窗口显示出来，导致聚焦时窗口看起来不透明
- **Zen 浏览器 (Flatpak)**: 通过 `flatpak override` 配合 NVIDIA 环境变量（`__NV_PRIME_RENDER_OFFLOAD=1`、`__GLX_VENDOR_LIBRARY_NAME=nvidia` 等）实现 GPU 加速。fcitx5 主题修复通过 D-Bus talk 权限（`org.fcitx.Fcitx5`、`org.freedesktop.portal.Fcitx`）和对 `~/.local/share/fcitx5` 及 `~/.config/fcitx5` 的只读文件系统访问实现。Zen `user.js` 已强制开启 WebRender、DMA-BUF、硬件视频解码
- **SPlayer-Next**: 通过 `splayer-next-bin` (AUR) 安装。二进制位于 `/opt/splayer-next/SPlayer-Next`，命令行启动命令 `splayer-next`。桌面文件路径已修正为 `/opt/splayer-next/SPlayer-Next`
- **Fcitx5 输入法**: 皮肤已切换为 `bamboo-dark`（古典竹简花纹主题），由 `~/.config/noctalia/morandi-gen.py` 动态注入莫兰迪配色；候选词排列已调整为竖向（`Vertical Candidate List=True`）
- **Pi Agent**: 已参考 OpenCode 完成 Pi Coding Agent (`~/.pi/agent`) 配置与深度主题/TUI 重构；安装 `pi-zentui` 与 `pi-open-tui` 扩展，配置 `zentui.json` 与 `open-tui.json`（集成 OpenCode / Claude Code 风格 ASCII 艺术 Logo Header、斜角卡片命令提示栏、固定底栏输入框、模型元数据轨、Starship 式 Git/环境状态栏、Arch 专用 Nerd 图标与百分比量规）；主题生成函数 `write_pi` 已扩展至 `~/.config/noctalia/morandi-gen.py`，全套莫兰迪 TUI 配色随壁纸动态同步
- **Krita Morandi-UI 插件**: 位于 `~/.local/share/krita/pykrita/krita_morandi_ui/`，源码同步于 `~/Projects/Krita-MorandiUI/`（chezmoi 不管理 pykrita）。2026 修复了 Win11+Krita 5.3.3 下动画时间轴拖动关键帧落点偏移 bug：根因是全局 QSS 中 `QTableView padding/border-radius`（+3px）与 `QHeaderView::section padding`（+8px）使时间轴内容整体偏移 ~11px，用户以标尺/docker 边框为参照拖动时产生视觉-落点错位（命中计算本身无偏移，Qt5/Qt6 双环境实测验证）。修复为 `variables.py` 新增 `timeline_exempt_style`（对 `KisAnimTimelineFramesView` 及内部 header 豁免 padding/border-radius/::item 几何），`redesign.py` 在全局 QSS 末尾拼入，实测偏移恢复至 ~0。重新发布 zip 后需让报告用户验证
- **Krita Simple-HSV-Sliders 插件**: 位于 `~/.local/share/krita/pykrita/simple_hsv_sliders/`，源码同步于 `~/Projects/Krita-SimpleHSVSliders/simple_hsv_sliders/`（chezmoi 不管理 pykrita，仓库 LanRhyme/Krita-SimpleHSVSliders）。2026 修复了 Krita 5.x（Qt5）下 `QMouseEvent.position()` 不存在的崩溃：`event.position()` 是 Qt6 API，Qt5 只有 `event.pos()`。修复为 `qt_compat.py` 新增 `mouse_x`/`mouse_point` 兼容助手（hasattr 分支自动适配），替换 8 处调用；同时补齐子目录源码缺失的 `NOTATION` 元组（安装版有而源码无）。已发布 v1.0.1（GitHub Release，zip 排除 **pycache**）
