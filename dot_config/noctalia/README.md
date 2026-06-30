# Noctalia Morandi Theme Generator

这是一套用于系统级全局动态配色的自动化工具脚本。它会根据当前的壁纸自动提取颜色，转换为低饱和度、偏暖色的“莫兰迪 (Morandi)”风格配色，并同步应用到整个桌面的所有常用软件中。

## 目录结构

* `apply-morandi.sh`: **入口脚本**。通常由 Noctalia 的 `wallpaperChange` hook 触发运行。它负责调用 Noctalia 获取壁纸的 Material You 主题色，生成 `colors.json`，并将信息传递给主控 Python 脚本。
* `morandi-gen.py`: **核心主控脚本**。负责读取颜色信息，计算各个子程序的色彩配置，然后修改目标软件的配置文件，并在最后执行系统热重载指令。
* `colors.json` *(自动生成)*: 暂存由 Noctalia 获取的原始颜色数据。

## 当前支持的应用程序

该脚本会自动接管并更新以下程序的色彩配置：

1. **Niri (Wayland Compositor)**: 窗口边框、激活状态、阴影和标签页指示器等 (`colors.kdl`)。
2. **Fcitx5**: 全局暗色输入法面板，使用带有 SVG 圆角的现代风格面板。
3. **Starship**: 终端 Prompt 提示符。
4. **Fastfetch**: 终端系统信息打印工具的主题色。
5. **Alacritty**: 终端仿真器的主要色彩映射。
6. **KDE / Qt 生态 (如 Kdenlive)**: 自动生成 `Morandi-dark.colors` KDE 配色方案，并通过 DBus 自动刷新 Qt 应用。
7. **Blender**: 利用 Blender Python API 后台自动修改并保存 `userpref.blend`，使 3D 软件与系统 UI 无缝融合。
8. **Limine 引导加载器**: 将当前壁纸进行模糊化处理，设为引导菜单背景 (`limine_bg.png`)。

## 如何新增支持的软件？

如果你想让它支持新的软件，只需要在 `morandi-gen.py` 里进行以下简单三步：

1. **编写写入函数**：在脚本中新建一个 `write_your_app(palette)` 函数，根据传入的 `palette` 字典提取所需的 Hex 颜色，并替换/生成你的应用配置文件。
2. **在 `main()` 中注册**：在 `main()` 函数的执行列表里调用 `write_your_app(palette)`。
3. **添加热重载（可选）**：如果该软件需要重启或者发送 DBus 信号才能生效新配置，将对应命令添加到 `apply_system_changes()` 函数的末尾即可。

## Chezmoi 同步提示

这些脚本受 **Chezmoi** 管理。在修改这些脚本后，请注意：
* 如果你直接修改了 `~/.config/noctalia/` 下的文件，请运行 `chezmoi re-add ~/.config/noctalia` 同步更改。
* 反之，你也可以直接在 Chezmoi 源码目录 (`~/.local/share/chezmoi/dot_config/noctalia/`) 中进行修改。
