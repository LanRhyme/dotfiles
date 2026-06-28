# Neovim 配置

一个现代化的 Neovim 配置，采用 DuskRose 主题（紫粉色系，低饱和度）。

## 特性

- **现代化 UI**: 美观的状态栏、文件树、启动画面
- **智能补全**: 基于 LSP 的代码补全
- **模糊查找**: Telescope 集成，快速查找文件和文本
- **Git 集成**: Gitsigns 提供实时 git 状态
- **语法高亮**: Treesitter 提供精准的语法高亮
- **自动格式化**: 保存时自动格式化代码
- **诊断集成**: 实时显示代码错误和警告

## 安装

1. 确保安装了 Neovim 0.9+
2. 克隆此配置到 `~/.config/nvim`
3. 启动 Neovim，插件会自动安装

## 快速开始

```bash
# 启动 Neovim
nvim

# 查看快捷键
:help keymaps

# 查看插件状态
:Lazy

# 查看 LSP 状态
:LspInfo
```

## 主要插件

- **lazy.nvim**: 插件管理器
- **neo-tree.nvim**: 文件树
- **telescope.nvim**: 模糊查找
- **nvim-lspconfig**: LSP 配置
- **nvim-cmp**: 自动补全
- **nvim-treesitter**: 语法高亮
- **lualine.nvim**: 状态栏
- **gitsigns.nvim**: Git 集成
- **conform.nvim**: 代码格式化
- **nvim-lint**: 代码检查

## 自定义

编辑 `~/.config/nvim/lua/` 下的文件来自定义配置：

- `config/options.lua` - 编辑器选项
- `config/keymaps.lua` - 快捷键映射
- `plugins/` - 插件配置
- `plugins/themes/duskrose/init.lua` - 主题颜色

## 更新

```bash
# 更新插件
:Lazy update

# 更新 LSP 服务器
:MasonUpdate

# 更新 Treesitter 解析器
:TSUpdate
```

## 故障排除

```bash
# 查看健康检查
:checkhealth

# 查看日志
:messages

# 查看 LSP 日志
:LspLog
```
