# Fcitx5

Fcitx5 输入法框架配置，使用 Rime 引擎。

## 文件说明

- `config` - 主配置文件（全局设置）
- `profile` - 输入法激活列表和优先级
- `conf/classicui.conf` - 经典界面配置（主题由 morandi-gen.py 自动生成）
- `conf/rime.conf` - Rime 引擎配置
- `conf/notifications.conf` - 通知配置

## 配置详情

### 主题

Fcitx5 主题由 `morandi-gen.py` 自动生成到 `~/.local/share/fcitx5/themes/morandi/`，包含：
- `theme.conf` - 主题配置（颜色、间距）
- `panel.svg` - 面板背景（圆角 + 模糊）
- `highlight.svg` - 高亮候选背景

主题颜色跟随壁纸变化，与整体莫兰迪色系保持一致。

### 输入法

- 主输入法：Rime（中州韵）
- 支持中英文切换

## 相关链接

- [Fcitx5 官网](https://fcitx-im.org/)
- [Rime 输入法](https://rime.im/)
