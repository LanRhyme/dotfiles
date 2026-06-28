# Noctalia

Noctalia Shell 桌面栏配置，提供状态栏、应用启动器、锁屏、壁纸管理等功能。

## 文件说明

- `settings.json` - 主配置（主题、布局、快捷键）
- `colors.json` - Material You 颜色配置（由 Noctalia 从壁纸自动提取）
- `morandi-gen.py` - 莫兰迪调色板生成器，从 Noctalia 的 Material You 颜色派生出统一的莫兰迪色系，并自动生成以下配置：
  - `niri/cfg/colors.kdl` - Niri 焦点环颜色
  - `starship.toml` - Starship 提示符调色板
  - `fastfetch/config.jsonc` - Fastfetch 主题色和 logo 颜色
  - `alacritty/alacritty.toml` - Alacritty 终端 16 色（保持原色相，降低饱和度）
  - fcitx5 输入法主题（含 SVG 面板和高亮背景）
- `apply-morandi.sh` - 壁纸切换时自动调用的脚本，依次执行：
  1. 运行 `morandi-gen.py` 生成调色板
  2. 重载 niri 配置
  3. 重启 fcitx5 以加载新主题
- `plugins/` - 插件目录
  - `file-search/` - 文件搜索
  - `github-feed/` - GitHub 动态（已排除 token）
  - `kaomoji-provider/` - 颜文字
  - `kde-connect/` - KDE Connect 集成
  - `notes-scratchpad/` - 便签
  - `screen-recorder/` - 录屏
  - `screenshot/` - 截图
  - `translator/` - 翻译

## 莫兰迪调色板系统

`morandi-gen.py` 从 Noctalia 提供的 Material You 颜色（primary、secondary、tertiary、error、surface 等）出发，通过以下步骤生成莫兰迪风格配色：

1. **降低饱和度**：所有颜色饱和度降低 25%~60%，上限 45%
2. **微调明度**：根据用途调整明暗（背景偏暗、文字偏亮）
3. **暖色偏移**：gold 和 peach 色相偏暖 +10~15

生成的调色板包含以下语义色：

| 色名 | 用途 | 来源 |
|------|------|------|
| base | 主背景 | surface |
| mantle | 深背景 | surface（更暗） |
| surface0/1/2 | 层级背景 | surfaceVariant |
| overlay0/1/2 | 次要文字 | outline |
| subtext0/1 | 次要文字 | onSurface |
| text | 主文字 | onSurface（最亮） |
| love | 错误/警告 | error（降低饱和度） |
| gold | 强调色 | primary + 暖色混合 |
| peach | 次强调 | error + 暖色混合 |
| rose | 警告 | primary + error 混合 |
| pine | 第三色 | tertiary |
| foam | 第二色 | secondary |
| iris | 主色 | primary |
| sky | 第三色变体 | tertiary |

## 相关链接

- [Noctalia GitHub](https://github.com/noctalia/noctalia-shell)
- [Noctalia 文档](https://docs.noctalia.dev/)
