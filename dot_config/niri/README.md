# Niri

滚动式 Wayland 合成器配置，搭配 noctalia-shell 桌面栏使用。

## 文件说明

- `config.kdl` - 主配置文件，通过 `include` 引入各模块
- `cfg/` - 模块化配置片段
  - `autostart.kdl` - 自启动应用（noctalia-shell、polkit、clipse 剪贴板）
  - `keybinds.kdl` - 快捷键绑定
  - `input.kdl` - 输入设备设置（鼠标加速 profile 为 flat）
  - `display.kdl` - 显示器设置
  - `layout.kdl` - 窗口布局（间隙 12px、默认半屏）
  - `rules.kdl` - 窗口规则（全局圆角 12px、fcitx 浮动、noctalia 壁纸置于底层）
  - `misc.kdl` - 其他设置
  - `animation.kdl` - 动画参数（spring 弹簧动画）
  - `colors.kdl` - 焦点环颜色（由 morandi-gen.py 自动生成，跟随壁纸变化）

## 主要配置

- 全局窗口透明度 0.8 + 背景模糊（Krita 除外）
- 鼠标加速关闭（flat profile）
- 光标主题 Bibata-Modern-Classic，大小 16
- fcitx5 输入法环境变量已配置

## 快捷键一览

### 应用启动

| 快捷键 | 功能 |
|--------|------|
| `Mod+Return` | 打开终端 (Alacritty) |
| `Mod+Ctrl+Return` | 打开应用启动器 |
| `Mod+B` | 打开浏览器 (Firefox) |
| `Mod+E` | 打开文件管理器 (Nautilus) |
| `Mod+Alt+L` | 锁屏 |
| `Mod+Shift+Q` | 会话菜单（关机/重启等） |
| `Mod+Shift+Z` | Kando 轮盘菜单 |

### 窗口操作

| 快捷键 | 功能 |
|--------|------|
| `Mod+Q` | 关闭窗口 |
| `Mod+T` | 切换浮动/平铺 |
| `Mod+F` | 最大化列（再按恢复半屏） |
| `Mod+Ctrl+F` | 真正全屏（隐藏 panel） |
| `Mod+W` | 切换标签页显示模式 |
| `Mod+C` | 居中当前列 |
| `Mod+Ctrl+C` | 居中所有可见列 |

### 窗口移动与聚焦

| 快捷键 | 功能 |
|--------|------|
| `Mod+H` / `Mod+Left` | 聚焦左侧列 |
| `Mod+L` / `Mod+Right` | 聚焦右侧列 |
| `Mod+K` / `Mod+Up` | 聚焦上方窗口 |
| `Mod+J` / `Mod+Down` | 聚焦下方窗口 |
| `Mod+Ctrl+H` / `Mod+Ctrl+Left` | 左移列 |
| `Mod+Ctrl+L` / `Mod+Ctrl+Right` | 右移列 |
| `Mod+Ctrl+K` / `Mod+Ctrl+Up` | 上移窗口 |
| `Mod+Ctrl+J` / `Mod+Ctrl+Down` | 下移窗口 |
| `Mod+Home` | 聚焦第一列 |
| `Mod+End` | 聚焦最后一列 |
| `Mod+Ctrl+Home` | 移动列到最前 |
| `Mod+Ctrl+End` | 移动列到最后 |

### 多显示器

| 快捷键 | 功能 |
|--------|------|
| `Mod+Shift+方向键` | 切换到相邻显示器 |
| `Mod+Shift+Ctrl+方向键` | 移动列到相邻显示器 |

### 工作区

| 快捷键 | 功能 |
|--------|------|
| `Mod+1~9` | 切换到工作区 1~9 |
| `Mod+Ctrl+1~9` | 移动列到工作区 1~9 |
| `Mod+Tab` | 切换上一个工作区 |
| `Mod+滚轮上/下` | 切换工作区 |
| `Mod+Ctrl+滚轮上/下` | 移动列到相邻工作区 |
| `Mod+滚轮左/右` | 聚焦左/右列 |
| `Mod+Ctrl+滚轮左/右` | 移动列左/右 |

### 列布局

| 快捷键 | 功能 |
|--------|------|
| `Mod+[` | 合并/弹出左侧窗口 |
| `Mod+]` | 合并/弹出右侧窗口 |
| `Mod+,` | 将右侧窗口合并到当前列 |
| `Mod+.` | 将底部窗口从列中弹出 |
| `Mod+-` | 列宽度 -10% |
| `Mod+=` | 列宽度 +10% |
| `Mod+Shift+-` | 窗口高度 -10% |
| `Mod+Shift+=` | 窗口高度 +10% |

### 截图

| 快捷键 | 功能 |
|--------|------|
| `Mod+Print` | mark-shot 截图 |
| `Ctrl+Shift+1` | 区域截图 |
| `Ctrl+Shift+2` | 全屏截图 |
| `Ctrl+Shift+3` | 截取当前窗口 |

### 其他

| 快捷键 | 功能 |
|--------|------|
| `Mod+Shift+Esc` | 显示快捷键覆盖 |
| `Mod+Escape` | 切换快捷键抑制（全屏应用卡住时使用） |
| `Mod+O` | 切换概览模式 |
| `Mod+Shift+U` | 切换 UGEE 数位板桥接 |
| `Mod+Shift+P` | 关闭显示器（OLED 省电/隐私） |
| `Ctrl+Alt+Delete` | 退出 Niri |

## 窗口规则

- 所有窗口：圆角 12px，裁剪到几何体
- fcitx：自动浮动
- noctalia 壁纸层：置于底层背景
- 全局窗口透明度 0.8 + 背景模糊
- Krita：不透明、无模糊
- Kando：浮动、无边框、无阴影、无圆角

## 动画

使用 spring 弹簧动画系统，各动画参数：
- 工作区切换：damping 0.8, stiffness 600
- 窗口打开：damping 0.7, stiffness 300
- 窗口关闭：damping 0.85, stiffness 1000
- 窗口移动/调整大小：damping 0.8~0.85, stiffness 700~800

## 相关链接

- [Niri GitHub](https://github.com/YaLTeR/niri)
- [配置文档](https://github.com/YaLTeR/niri/wiki/Configuration:-Introduction)
- [快捷键文档](https://github.com/YaLTeR/niri/wiki/Configuration:-Key-Bindings)
