# CachyOS Dotfiles

使用 [chezmoi](https://www.chezmoi.io/) 管理的 CachyOS 个人配置文件

## 截图

![桌面截图](.github/assets/screenshot.png)

## 功能特性

- 自动同步：每 2 小时通过 cron 自动推送到 GitHub
- 敏感文件保护：自动排除密钥、Token 等敏感信息
- 跨机器恢复：一条命令恢复所有配置
- 模块化管理：按应用分类，易于维护

## 软件依赖

| 分类 | 软件 | 用途 |
|------|------|------|
| Shell | [fish](https://fishshell.com/) | 交互式 Shell |
| Shell | [starship](https://starship.rs/) | 终端提示符 |
| 终端 | [alacritty](https://alacrittyty.org/) | GPU 加速终端 |
| 终端 | [kitty](https://sw.kovidgoyal.net/kitty/) | 功能丰富的终端 |
| 编辑器 | [neovim](https://neovim.io/) | 现代 Vim |
| 编辑器 | [micro](https://micro-editor.github.io/) | 简单终端编辑器 |
| 窗口管理 | [niri](https://github.com/YaLTeR/niri) | 滚动式 Wayland 合成器 |
| 桌面栏 | [noctalia](https://github.com/noctalia/noctalia-shell) | Noctalia 桌面栏 |
| 菜单 | [kando](https://kando.menu/) | 环形快捷菜单 |
| 输入法 | [fcitx5](https://fcitx-im.org/) | 输入法框架 |
| 主题 | [Kvantum](https://tsujan.github.io/Kvantum/) | Qt 主题引擎 |
| 监控 | [btop](https://github.com/aristocratos/btop) | 系统监控 |
| 可视化 | [cava](https://github.com/karlstav/cava) | 音频可视化 |
| 文件管理 | [superfile](https://github.com/MHN-SuperFile/superfile) | 终端文件管理器 |
| 信息展示 | [neofetch](https://github.com/dylanaraps/neofetch) | 系统信息 |
| 录屏 | [OBS Studio](https://obsproject.com/) | 录屏/直播 |
| 录屏 | [gpu-screen-recorder](https://nowrep.github.io/gpu-screen-recorder/) | GPU 录屏 |
| 绘图 | [Krita](https://krita.org/) | 数字绘画 |
| 开发 | [GitHub CLI](https://cli.github.com/) | GitHub 命令行工具 |
| 开发 | [uv](https://github.com/astral-sh/uv) | Python 包管理器 |
| 网络 | [KDE Connect](https://kdeconnect.kde.org/) | 设备连接 |
| 网络 | [frp](https://github.com/fatedier/frp) | 内网穿透 |
| AUR | [yay](https://github.com/Jguer/yay) | AUR 助手 |

## 快速安装

```bash
# 安装 chezmoi
paru -S chezmoi

# 初始化并应用配置
chezmoi init --apply LanRhyme
```

## 安装所有依赖

```bash
paru -S fish starship alacritty kitty neovim micro \
        niri noctalia kando fcitx5-rime kvantum \
        btop cava superfile neofetch \
        obs-studio gpu-screen-recorder krita \
        github-cli uv yay kdeconnect frpc
```

## 配置文件结构

```
dotfiles/
├── .chezmoiignore              # 排除规则
├── .bashrc                     # Bash 配置
├── .zshrc                      # Zsh 配置
├── .gitconfig                  # Git 配置
└── .config/
    ├── alacritty/              # Alacritty 终端
    │   └── alacritty.toml      # 主题、字体、快捷键
    ├── kitty/                  # Kitty 终端
    ├── fish/                   # Fish Shell
    │   ├── config.fish         # 主配置
    │   └── conf.d/             # 环境变量加载
    ├── starship.toml           # Starship 提示符
    ├── niri/                   # Niri 窗口管理器
    │   └── config.kdl          # 快捷键、工作区、窗口规则
    ├── noctalia/               # Noctalia 桌面栏
    │   ├── settings.json       # 主题、布局
    │   └── plugins/            # 插件（GitHub Feed、翻译、截图等）
    ├── kando/                  # Kando 环形菜单
    ├── nvim/                   # Neovim 编辑器
    ├── micro/                  # Micro 编辑器
    ├── fcitx5/                 # Fcitx5 输入法
    │   └── conf/rime.conf      # Rime 引擎配置
    ├── btop/                   # Btop 系统监控
    ├── cava/                   # Cava 音频可视化
    ├── superfile/              # Superfile 文件管理器
    ├── neofetch/               # Neofetch 系统信息
    ├── obs-studio/             # OBS 录屏
    ├── krita/                  # Krita 绘图
    ├── gh/                     # GitHub CLI
    ├── kdeconnect/             # KDE Connect
    ├── frp/                    # FRP 内网穿透
    ├── gtk-3.0/                # GTK3 主题
    ├── gtk-4.0/                # GTK4 主题
    ├── qt5ct/                  # Qt5 主题
    ├── environment.d/          # 环境变量
    ├── autostart/              # 自启动应用
    ├── mimeapps.list            # 默认应用
    ├── user-dirs.dirs          # 用户目录
    └── yay/                    # Yay AUR 助手
```

## 常用命令

### chezmoi 命令

```bash
chezmoi add ~/.config/newapp    # 添加新配置
chezmoi diff                    # 查看本地与仓库差异
chezmoi apply                   # 应用仓库配置到本地
chezmoi update                  # 拉取远程更新并应用
chezmoi cd                      # 进入源目录
chezmoi managed | wc -l         # 查看管理文件数量
```

### 手动同步

```bash
# 手动运行同步脚本
~/.local/bin/dotfiles-sync.sh

# 查看 cron 任务
crontab -l

# 查看同步日志
cat ~/.local/share/chezmoi/sync.log
```

## 自动同步

配置每 2 小时通过 cron 自动同步：

1. `chezmoi re-add` 检测本地配置变更
2. `git add` 暂存变更
3. `git commit` 提交变更
4. `git push` 推送到 GitHub

同步脚本位于 `~/.local/bin/dotfiles-sync.sh`。

## 敏感文件保护

以下文件已加入 `.chezmoiignore`，不会被提交：

| 文件 | 原因 |
|------|------|
| `kdeconnect/privateKey.pem` | 设备私钥 |
| `kdeconnect/certificate.pem` | 设备证书 |
| `noctalia/plugins/github-feed/settings.json` | GitHub Token |
| `noctalia/plugins/github-feed/cache/` | GitHub 缓存数据 |

## 新机器恢复

```bash
# 1. 安装必要工具
paru -S chezmoi git

# 2. 初始化并应用配置
chezmoi init --apply LanRhyme

# 3. 安装软件依赖（见上方安装命令）

# 4. 重启或重新登录
```

## 添加新配置

```bash
# 添加单个配置文件
chezmoi add ~/.config/newapp/config

# 添加整个目录
chezmoi add ~/.config/newapp

# 提交并推送
chezmoi cd
git add -A
git commit -m "feat: add newapp config"
git push
```

## 排除敏感文件

如果配置文件包含敏感信息（Token、密钥等），需要：

1. 在 `.chezmoiignore` 中添加文件路径
2. 使用 `git rm --cached` 从暂存区移除
3. 提交排除规则

示例：
```bash
cd ~/.local/share/chezmoi
echo "dot_config/app/secret.json" >> .chezmoiignore
git add .chezmoiignore
git commit -m "chore: exclude secret file"
```

## 许可证

个人配置文件，仅供参考学习
