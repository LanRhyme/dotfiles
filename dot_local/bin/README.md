# Local Scripts

本目录 (`~/.local/bin`) 存放了系统日常运行所需的一些自定义脚本工具。这些脚本在登录时会被加入全局 PATH，方便在终端或启动器中直接调用。

## 脚本列表

### 1. `dotfiles-sync.sh`
* **功能**: 自动通过 Chezmoi 搜集配置变化并将其 Commit 到 Github 仓库。
* **执行方式**: 绑定了系统 Cron 定时任务，每两小时自动在后台静默运行一次。
* **日志**: 同步记录会追加到 `~/.local/share/chezmoi/sync.log`。

### 2. `kando-niri.sh`
* **功能**: 专为 Niri 环境编写的 Kando（环形菜单）启动包装器。
* **原由**: Electron 应用程序在 Wayland 窗口管理器下往往会默认降级使用 Xwayland，导致模糊或无法正确读取输入。该包装器强行注入环境变量 `ELECTRON_OZONE_PLATFORM_HINT=wayland`，使 Kando 能够以原生 Wayland 模式完美运行。

### 3. `aether-hub.py`
* **功能**: Aether 桌面系统的集中化配置与应用管理面板。
* **特性**:
  - 基于 PyQt6 构建的可视化交互界面。
  - 能够快速调整系统选项，控制各种常驻进程的重启（如 Fcitx5 热重载）。
  - 读取并操作 `~/.local/share/applications` 下的 `.desktop` 文件，便于管理应用入口的显示或隐藏。
