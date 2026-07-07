# Local Scripts

本目录 (`~/.local/bin`) 存放了系统日常运行所需的一些自定义脚本工具这些脚本在登录时会被加入全局 PATH，方便在终端或启动器中直接调用

## 脚本列表

### 1. `dotfiles-sync.sh`
* **功能**: 自动通过 Chezmoi 搜集配置变化并将其 Commit 到 Github 仓库
* **使用方法**: 直接运行 `dotfiles-sync.sh` 即可自动执行，通常不需要手动干预
* **执行方式**: 绑定了系统 Cron 定时任务，每两小时自动在后台静默运行一次
* **日志**: 同步记录会追加到 `~/.local/share/chezmoi/sync.log`

### 2. `kando-niri.sh`
* **功能**: 专为 Niri 环境编写的 Kando（环形菜单）启动包装器
* **使用方法**: 配置绑定快捷键指向该脚本即可，例如在 Niri 配置中绑定按键执行 `kando-niri.sh`
* **原由**: Electron 应用程序在 Wayland 窗口管理器下往往会默认降级使用 Xwayland，导致模糊或无法正确读取输入该包装器强行注入环境变量 `ELECTRON_OZONE_PLATFORM_HINT=wayland`，使 Kando 能够以原生 Wayland 模式完美运行

### 3. `aether-hub.py`
* **功能**: Aether 桌面系统的集中化配置与应用管理面板
* **使用方法**: 在终端输入 `aether-hub.py` 执行，或通过桌面启动器将其作为应用打开
* **特性**:
  - 基于 PyQt6 构建的可视化交互界面
  - 能够快速调整系统选项，控制各种常驻进程的重启（如 Fcitx5 热重载）
  - 读取并操作 `~/.local/share/applications` 下的 `.desktop` 文件，便于管理应用入口的显示或隐藏

### 4. `colloid-gen.py`
* **功能**: 自动生成符合 Colloid-Dark 风格的无边框大圆角图标的工具脚本
* **使用方法**: 终端执行 `python3 ~/.local/bin/colloid-gen.py <输入图片路径> <输出图标名称>` 即可生成并在主题目录下保存为 PNG 格式
* **特性**:
  - 基于 Pillow 库对输入图像进行自动化边缘裁剪以剔除自带背景
  - 根据输入图像的主色调明度智能生成低饱和度的深色或浅色背景
  - 自动调整尺寸并注入标准的圆角掩码，输出符合现代 UI 规范的 PNG 格式
  - 支持直接处理带透明度的 Logo 或含有纯色背景的应用图标
