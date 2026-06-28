# Fastfetch

系统信息展示工具配置，替代 neofetch。

## 文件说明

- `config.jsonc` - 主配置文件（由 `morandi-gen.py` 自动生成）
- `avatar.png` - 头像图片，用于 chafa 模式在终端中渲染

## 配置详情

### Logo

- 类型：chafa（通过 chafa 将 PNG 渲染为终端字符画）
- 来源：`avatar.png`（自定义头像）
- 尺寸：40×19 字符
- 顶部间距：2 行

### 颜色

- 键名颜色：`#afac9c`（iris，莫兰迪主色）
- 标题颜色：`#f2f2f2`（text，近白）
- logo 颜色由 morandi-gen.py 从壁纸动态生成

### 显示模块

系统信息分三组显示：
1. **系统信息**：OS、Kernel、Uptime、Packages、Shell、Terminal、DE、WM、WM Theme
2. **硬件信息**：Host、CPU、GPU、Memory、Disk
3. **网络信息**：Local IP

底部显示莫兰迪色系 16 色色块（来自终端调色板）。

### 自动生成

`config.jsonc` 由 `morandi-gen.py` 在壁纸切换时自动重新生成，确保主题色跟随壁纸变化。

## 依赖

- `chafa` - 终端图片渲染

## 相关链接

- [Fastfetch GitHub](https://github.com/fastfetch-cli/fastfetch)
- [配置文档](https://github.com/fastfetch-cli/fastfetch/wiki/Configuration)
