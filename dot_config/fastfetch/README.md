# Fastfetch

系统信息展示工具配置，替代 neofetch

## 文件说明

- `config.jsonc` 主配置文件，由 `morandi-gen.py` 自动生成
- `avatar.png` 头像图片，用于 chafa 模式在终端中渲染

## 配置详情

### Logo

- 类型 chafa，通过 chafa 将 PNG 渲染为终端字符画
- 来源 `avatar.png` 自定义头像
- 尺寸 40×19 字符
- 顶部间距 2 行

### 颜色

- 标题三色分区 user=text，at=iris，host=pine
- 键名颜色 iris，莫兰迪主色
- 分隔线颜色 overlay0，宽度与 logo 等宽（40 字符）
- 主题色由 morandi-gen.py 从壁纸动态生成

### 显示模块

信息分三组展示

1. **系统** OS、Kernel、Uptime、Packages、Shell、Terminal、Terminal Font、DE、WM
2. **硬件** Host、CPU、GPU、Memory、Disk、Display
3. **网络** Local IP

底部展示 8 个莫兰迪圆形色点（●）横向排列，来自终端调色板

### 自动生成

`config.jsonc` 由 `morandi-gen.py` 的 `write_fastfetch` 在壁纸切换时全量重写，确保模块结构与主题色跟随壁纸变化

## 依赖

- `chafa` 终端图片渲染

## 相关链接

- [Fastfetch GitHub](https://github.com/fastfetch-cli/fastfetch)
- [配置文档](https://github.com/fastfetch-cli/fastfetch/wiki/Configuration)
