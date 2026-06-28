# Alacritty

GPU 加速终端模拟器配置。

## 文件说明

- `alacritty.toml` - 主配置文件

## 配置详情

### 窗口

- 标题：`Alacritty@CachyOS`
- 透明度：0.88
- 内边距：16px
- 默认窗口大小：100 列 × 30 行
- 深色窗口装饰

### 字体

- 主字体：JetBrainsMono Nerd Font（Regular / Bold / Italic / Bold Italic）

### 颜色主题

- 背景色：`#1a1a18`（深灰）
- 前景色：`#f2f2f2`（近白）
- 16 色终端调色板由 `morandi-gen.py` 自动生成，保持原色相但降低饱和度，贴合莫兰迪色系
- 光标：Beam 形状，始终闪烁
- 选中文本：背景 `#43423c`

### 光标

- 形状：Beam（竖线）
- 闪烁：Always
- 厚度：0.15

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+C` | 复制 |
| `Ctrl+Shift+V` | 粘贴 |
| `Ctrl+Shift+F` | 前向搜索 |
| `Ctrl+Shift+B` | 后向搜索 |
| `Ctrl+L` | 清除日志通知 |
| `Ctrl+0` | 重置字体大小 |
| `Shift+PageUp/PageDown` | 滚动 |
| `Shift+Home/End` | 滚动到顶部/底部 |

## 相关链接

- [Alacritty 官网](https://alacritty.org/)
- [配置文档](https://github.com/alacritty/alacritty/blob/master/extra/man/alacritty.5.scd)
