# 星语 · Star Pet

Antigravity 窗口内的 Gemini 猫娘陪伴层，由插件的 sidecar 通过本机 CDP 注入到渲染器里，不修改 `/opt/Antigravity` 任何文件

## 组成

```text
plugin.json                  插件元数据
sidecars/pet/sidecar.json    宿主据此拉起 main.mjs，restart_policy=always
sidecars/pet/main.mjs        连接 CDP、读取额度与日志、按状态推送
sidecars/pet/layer.mjs       页面内图层源码，序列化后注入渲染器
sidecars/pet/assets/         帧图、台词（本地生成，不入 dotfiles）
sidecars/pet/tools/          从上游源码重建素材
```

## 宿主提供的环境

宿主启动 sidecar 时注入以下变量，插件不自己做进程扫描

| 变量 | 用途 |
| --- | --- |
| `AGY_BROWSER_ACTIVE_PORT_FILE` | Chromium `DevToolsActivePort` 路径，用于连 `https://127.0.0.1:<端口>/` 页面 |
| `ANTIGRAVITY_LS_ADDRESS` | 语言服务器 HTTP 端口 |
| `ANTIGRAVITY_CSRF_TOKEN` | 调用 `RetrieveUserQuotaSummary` 的凭据 |
| `ANTIGRAVITY_APP_DATA_DIR` | `~/.gemini/antigravity`，读 `brain/*/.system_generated/logs/transcript_full.jsonl` |
| `ANTIGRAVITY_EXECUTABLE_DATA_DIR` | 插件数据目录，存 `settings.json` 与 `pet.log` |

## 配色：桌面壁纸皮肤

背景直接用**当前桌面壁纸**（从 noctalia 的 `~/.local/state/noctalia/settings.toml` 读 `[wallpaper.monitors.*]` 路径），
sidecar 用 `magick` 压到 1600px、质量 70 存到 `sidecar_data/.../wallpaper.jpg` 后作为 data URL 注入

- 壁纸铺在 `#root` 之下，上面只盖**一层纯色半透明遮罩**（`scrim`，默认 0.5），没有任何渐变、阴影、模糊
- 面板（主壳 0.72、侧栏 0.72、卡片/输入框）都是纯色半透明，保留层次但不加装饰
- 壁纸换了会自动重载（按源文件 mtime 判断）
- 强度：`star-pet skin art 0.25`（越小壁纸越清晰，0–0.95），整体关闭 `star-pet skin off`

## 配色（morandi 回退模式）

宿主把整套主题变量以 inline style 写在 `<html>` 上，所以注入层用 `!important` 盖住，变量来源是
`~/.config/noctalia/antigravity-ide.json` —— 由 `morandi-gen.py` 的 `write_antigravity_ide(palette)` 生成
换壁纸时主题引擎重跑，`antigravity-ide.json` 的 mtime 变化，sidecar 重新读盘并热更样式，IDE 跟着壁纸走

变量对齐宿主用的 Tailwind v4 主题：`--background`、`--content`、`--card`、`--sidebar`、`--muted`、`--border`、`--primary`、`--link`、`--error/--warning/--success` 及其 `--color-*` 别名

```bash
star-pet skin on|off     开/关配色注入
```

## 额度来源

`POST http://{LS_ADDRESS}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary`
取 `groups[].buckets[]` 里 `gemini-5h` 与 `gemini-weekly` 的 `remainingFraction`，每 60 秒刷新
气泡里标「刚刚 / N 分钟前 / 待更新」，缓存不等于实时额度

## 控制

```bash
star-pet status          查看配置、挂载状态与额度
star-pet on | off        显示或隐藏（2 秒内生效）
star-pet scale 260       改大小，120–420
star-pet state auto      自动 | idle | thinking | success | error
star-pet log             sidecar 日志
```

## 素材与上游

角色帧图与台词来自 [Antigravity-Star-Suite](https://github.com/Monokumakuki/Antigravity-Star-Suite)（代码 MIT，美术不适用 MIT，见其 ASSETS.md）
本地用 `tools/build-assets.sh` 从上游源码降采样重建，不提交进 dotfiles

## 卸载

删除 `~/.gemini/config/plugins/star-pet` 并在 Antigravity 里重载窗口，图层随之消失
上游 Electron 桌宠与本插件互不依赖，可单独保留

## 已知边界

宿主界面布局变化可能导致气泡定位需微调，图层本身不依赖任何 Antigravity class 名
宿主刷新或路由跳转时图层会被摘除，1 秒内自动挂回
思考与完成状态由最新 transcript 的 `PLANNER_RESPONSE` 推导，2.17.0 的日志不含 token 字段，因此气泡只显示步数
