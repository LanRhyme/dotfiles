# Fcitx5

Fcitx5 输入法框架 + Rime 引擎配置。

## 文件说明

- `config` - Fcitx5 主配置（快捷键、行为设置）
- `profile` - 输入法列表和顺序
- `conf/classicui.conf` - 经典界面配置
- `conf/rime.conf` - Rime 引擎配置（预编辑、切换行为）
- `conf/notifications.conf` - 通知配置

## 配置详情

### 输入法

- 默认输入法：Rime（中州韵）
- 键盘布局：US
- 切换快捷键：`Ctrl+Space`

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Space` | 切换输入法 |
| `Super+Space` | 轮换输入法组 |
| `Shift_L` | 临时英文输入 |
| `Shift+Tab` | 上一页候选词 |
| `Tab` | 下一页候选词 |

### Rime 引擎

#### 中英切换行为

```yaml
ascii_composer:
  switch_key:
    Caps_Lock: clear        # 清除输入并切换
    Shift_L: clear          # 清除输入并切换
    Shift_R: clear          # 清除输入并切换
    Control_L: noop         # 不响应
    Control_R: noop         # 不响应
```

#### 切换输入法时的行为

`SwitchInputMethodBehavior` 设置为 `"Commit raw input"`：

- 输入拼音但未选择候选词时按 `Ctrl+Space` 切换输入法
- 拼音字母会直接作为英文字符上屏
- 类似 Windows 输入法的行为

可选值：
- `"Clear"` - 清除未上屏内容
- `"Commit commit preview"` - 提交候选词（默认）
- `"Commit raw input"` - 提交原始输入（当前设置）

#### 预编辑模式

- 嵌入式预编辑文本（光标固定在开头）
- 共享输入状态：所有窗口共享

### 候选词

- 每页候选词数量：8

## 安装依赖

```bash
# 安装 Fcitx5 和 Rime
sudo pacman -S fcitx5 fcitx5-rime fcitx5-configtool

# 安装依赖库
sudo pacman -S librime librime-lua librime-octagram

# 环境变量（添加到 ~/.config/environment.d/fcitx5.conf）
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
```

## 相关链接

- [Fcitx5 官网](https://fcitx-im.org/)
- [Fcitx5 Rime 插件](https://github.com/fcitx/fcitx5-rime)
- [Rime 输入法](https://rime.im/)
- [Rime 配置文档](https://github.com/rime/home/blob/master/customization.yaml)
