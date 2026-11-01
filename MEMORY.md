# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **逃生 1 (Outlast, AppID 238320) 卡顿排查 + 3DM 汉化落地 (2026-11-01, 已完成)**:
  - 现场: 22:38:27 启动, 22:43:22 退出 (码 -1), 全程只有一个 1280x720 窗口, 窗口类 `OLGame.x86_64`, 进程 RSS 4.9GB / 35 线程
  - 根因一: **跑在核显上** —— 进程 maps 里 NVIDIA 库 0 条、Mesa/iris 库 10411 条, 同时 `nvidia-smi` 只有 niri 与 steam 两个图形上下文, RTX 3050 全程 1% / 14W; 因为 2026-10-29 移除了全局 PRIME offload 改按需 prime-run, 而该游戏没设启动选项
  - 根因二: **niri 全局规则把游戏窗口圈进模糊** —— 原生移植窗口类不是 `steam_app_*`, 于是吃 `match app-id=".*"` 的 opacity 0.98 + blur true, 与 Steam 大屏、影之刃零完全同构
  - 根因三: 后台超卖, 当时 `language_server` 单进程 5.5GB/14-17% CPU, Antigravity + steamwebhelper + QQ + Bettbox 一起压在 12 线程上, swap 已用 6.7G; 可用 `~/.local/bin/game-mode.sh on` 冻结
  - 中文现状: Steam API 确认官方语言只有 英/法/意/德/西/俄/波/葡/日, **没有中文**; 原生包 `OLGame/Localization/` 也只有 INT/DEU/ESN/FRA/ITA/JPN/POL/PTB/RUS, 论坛汉化补丁全是 Windows 版 (`CookedPCConsole`), 所以要么切 Proton 跑 Windows 版, 要么自己做字体与文本 (Scaleform 字体是硬门槛)
  - 兼容层现状: `config.vdf` 里 238320 已映射 `proton-cachyos-slr` (`/usr/share/steam/compatibilitytools.d/proton-cachyos-slr`), 22:43 起 Steam 在补 Windows depot 238321 共 3.78GB, 补完前点开始还会走原生 720p
  - 已落地: chezmoi `dot_config/niri/config.kdl` 全局规则加 `exclude` 掉 `steam_app_.*` / `pbz[.]exe` / `OLGame.*` / `.*[Oo]utlast.*`, 游戏规则补 `^OLGame[.].*` / `^Outlast[.].*` / `^Outlast.*`; `niri validate` 通过并已热重载
  - 硬件注记: DXVK 会把 DISCRETE_GPU 排到最前, 所以 Proton 路径不需要额外 env 就会落到 3050; 原生 GL 路径才需要 `prime-run %command%`
  - **汉化已装 (3DM 轩辕 v2.0)**: 来源 `https://dl2.wsyhn.com/CHS1/3DMGAME-Outlast.CHS.Patch.v2.0-3DM.rar` (34,230,900B, md5 `eb719a2a1f9ac1971045d4975c689b14`), 静态审查过: PE32 GUI, 无 Inno/NSIS 特征、正文零 URL, 后面 33MB 载荷是加密的; 用 `bwrap --unshare-net` + 独立 WINEPREFIX 关笼子跑 (只写游戏目录), 汉化器自动完成, 不需要点按钮
  - 替换清单 (Windows `CookedPCConsole`): `OLFrontEnd_LOC_INT.upk` 689KB→30.1MB、`OLFrontEnd.upk` 3.09→6.82MB、`Startup_LOC_INT.upk` 14.8KB→112KB、`Startup.upk` 4.9→13.9MB、`UDKBase_LOC_INT.upk` 110KB→25.2MB、`Asylum_Exterior-LD.upk` 10.4→19.1MB; 外加 `Localization/INT/` 六个 .int 全换中文 UTF-16 (字幕每个汉字间夹空格, 是汉化组绕 UE3 换行的手段, 看着字距大属正常)
  - 补丁副作用: 会往游戏根目录丢 `说明.txt` 与 `www.3dmgame.com.url` (已删 .url 与 bwrap 留下的 0 字节 exe 挂载点, 保留 说明.txt); 手工挂载 exe 到游戏目录会在卸载后残留 0 字节文件, 下次要记得删
  - 回滚口径: Steam「验证游戏文件完整性」即可还原全部 .upk 与 .int; 该游戏以后若自动更新也会把汉化冲掉
  - 实测结论: 同一个 Proton 会话里 `Using D3D9 device (0): NVIDIA GeForce RTX 3050 Laptop GPU`, 日志走到 `Resetting level dlc_mainmenugame` + `Resizing to 1920x1080 (fullscreen)`; 首次 Proton 启动会卡在 UE3 logo 一次 (日志停在 4.3s, 主线程 1 核跑满、GPU 2%), 关掉重开一次就过, `-nostartupmovies` 会被 `OutlastLauncher.exe` 吞掉不生效 (日志 Command line 只有 `-installed -seekfreeloadingpcconsole`)
  - 备份: `~/tmp/niri-config.kdl.bak-*`; 快照与汉化包留在 `~/tmp/outlast-chs/` (`patch.rar` / `extracted/` / `manifest-before.tsv` / `manifest-after.tsv`)

- **Antigravity 星语猫娘桌宠改造为插件注入版 (2026-11-01, 完成)**:
  - 起因: 上游 `Monokumakuki/Antigravity-Star-Suite`（Gemini 猫娘桌宠 + 蓝紫 Dream Skin）官方只给 Windows x64, 其桌宠是独立的 Electron 透明窗口 + `.NET ForegroundHost.exe` 跟随宿主; Linux 上跟随能力直接缺失, 且 Wayland 客户端无法自己摆窗口位置, 桌宠只能乱停
  - 关键结论: Antigravity 的「插件」不是 VS Code 扩展模型, `~/.gemini/config/plugins/<name>/` 只认三种扩展点 —— `plugin.json` 元数据、`sidecars/<name>/sidecar.json`（宿主代拉 Node 子进程, `restart_policy` 生效）、`hooks/` 与 `mcp_config.json`; 官方 UI 槽位只有一个 `ui_config.views[].entrypoint: SIDECAR_UI_ENTRYPOINT_AUX_PANE`（辅助面板, 拿不到「浮在整窗上的猫」）
  - 同机 `antigravity-pulse` 的做法印证: 它是靠 `patch-loader.py` 改 `app.asar` 塞 `// AG_PULSE_INLINE_V1` 内联 UI, 且写死 `SUPPORTED_VERSIONS = {'2.19.1'}`; 故不改安装目录、改走 CDP 注入更干净
  - **宿主给 sidecar 的现成凭据（免进程扫描, 最重要）**: sidecar 进程环境里有 `AGY_BROWSER_ACTIVE_PORT_FILE`（= `~/.config/Antigravity/DevToolsActivePort`）、`ANTIGRAVITY_LS_ADDRESS`（如 `localhost:42815`）、`ANTIGRAVITY_CSRF_TOKEN`、`ANTIGRAVITY_APP_DATA_DIR`（`~/.gemini/antigravity`）、`ANTIGRAVITY_EXECUTABLE_DATA_DIR`（`~/.gemini/antigravity/sidecar_data/star-pet/pet/data`）; 宿主 Node 为 v24.20.0 且自带 global `WebSocket`, 无需 vendor ws
  - **额度接口（比上游的 React fiber 抓取可靠得多）**: `POST http://{LS_ADDRESS}/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary`, 头带 `x-codeium-csrf-token` 与 `Connect-Protocol-Version: 1`, 返回 `response.groups[].buckets[]` 的 `gemini-5h` / `gemini-weekly` 的 `remainingFraction` 与 `resetTime`; `GetUserStatus` 只给 per-model `quotaInfo`, 没有双窗口条
  - 落地: 新插件 `~/.gemini/config/plugins/star-pet/`（main.mjs 编排 + layer.mjs 页面图层, Shadow DOM 隔离, 帧图为 420px webp data URL, CSP 只放行 data:）; 猫固定在窗口内 `z-index:6000`, 可拖动（位置存页面 localStorage）, 悬停出额度气泡, 点击换台词, 思考时三个跳动点; 宿主重建 `document.body` 或换路由后图层被摘除, 靠 1 秒 keep-alive 自愈
  - 控制入口: `~/.local/bin/star-pet status|on|off|scale|state|log`, 改的是插件数据目录里的 `settings.json`, sidecar 每 2 秒重读
  - 踩坑: `pkill -f '<pattern>'` 会把执行它的 `bash -c` 自己匹配进来直接杀掉 (本次连踩两次), 杀应用一律用 `/proc/*/cmdline` 精确匹配并排除自身的脚本; 图层 `document.body.appendChild` 必须显式写出, 只靠 MutationObserver/定时器会晚 1 秒; `:host { all: initial }` 之后气泡的 `position:absolute` 相对的是 `.wrap` 而不是视口
  - 宿主现状: 本机 Antigravity 2.17.0 离线时语言服务器卡在 Google 授权（`oauth2.googleapis.com` 30 秒超时）, 窗口 `ERR_TIMED_OUT` 且 12 秒后自行退出; 带 `HTTPS_PROXY=http://127.0.0.1:7890` 启动即可正常渲染, 说明这类「窗口打不开」要先怀疑代理没开
  - **Dream Skin 改为 Morandi 版（已落地）**: 上游选择的蓝紫换肤整套 CSS 照 2.28 写, `.agy-sheet` / `.surface-composer` 在 2.17.0 匹配数为 0, 故不移植; 改为在 `morandi-gen.py` 新增 `write_antigravity_ide(palette)`, 生成 `~/.config/noctalia/antigravity-ide.json`（33 个变量）, 换壁纸自动重算, 插件按 mtime 热更
  - **关键坑: 宿主把主题变量写成 `<html>` 的 inline style**（`--background`、`--foreground`、`--primary`、`--card`、`--sidebar`… 全在 style 属性里, 还有整套 `--vscode-*`），所以注入的 `:root{...}` 一律被压住, 必须每条声明都带 `!important` 才能生效; 判断是否生效只看 `getComputedStyle(documentElement).getPropertyValue('--background')`
  - **桌宠「一闪一闪」根因（2026-11-01 修复）**: `blink.png` 不是 idle 的小改, 而是另一次渲染 —— 整张画布 24.6% 像素不同且脸部位置/缩放都变了（diffBBox 覆盖全图）, 切过去就是整张脸跳一下; 叠加原实现每 2 秒把近百 KB 的 `frames` 整包推送且重置 `frameName`, 于是每 2 秒强制换帧一次。修法: 帧图只在首次注入时发（`injectionConfig(state, withFrames)`）+ 配置签名节流（`configSignature`）+ 停用 blink 帧 + 两张帧图都 `position:absolute` 放在 `aspect-ratio: 420/351` 的固定画框里（换表情不再引起任何布局位移）。实测 15 秒内帧属性变更 0 次
  - **皮肤「看不出变化」根因**: (1) 宿主把主题变量写成 `<html>` 的 inline style, 注入的 `:root{...}` 被压住, 必须每条声明加 `!important`; (2) 只在 `body` 上画渐变完全无效, 因为主壳 `[class~="bg-background"]`、侧栏 `[class~="bg-sidebar"]`、输入框 `[class~="bg-card-border"]` / `bg-card` 各自自绘背景, 渐变必须命中这些容器; (3) 选择器要用 `[class~="bg-card"]`（完整 class token）而不是 `[class*="bg-card"]`, 否则 `hover:bg-card`、`data-[state]:bg-card` 这些变体会被一起染色, 每一行都变成渐变卡片
  - **调色板偏中性的处理**: 壁纸 source 色 `#eee6ba` 虽然 s≈60%, 但 `mPrimary #dad8ce` 只有 s=14%, 直接推导出的暗色面几乎和 IDE 自带暖灰撞成一片; 故在 `write_antigravity_ide` 里给饱和度下限 15、亮度分别取 10/13/17/22 → bg `#1c1b16`、sidebar `#25231c`、card `#302f25`、secondary `#3f3c30`, 强调色取 `palette["gold"]` `#bdb79a`, 边框 `gold 34%`
  - **宿主 sidecar 重启有延迟**: SIGTERM 掉 sidecar 后宿主约 **45 秒**才按 `restart_policy: always` 重新拉起, 期间 `star-pet off/on` 会打到还没死的旧进程, 导致改了代码却没换图层 —— 判断是否换了新代码看 `pet.log` 里有没有新的 `injected layer`, 没有就先 `star-pet off` 再 `on` 强制重挂
  - **配色返工（2026-11-01 晚）**: 暖橄榄 Morandi 版被否（"配色好奇怪"）—— 壁纸 `mPrimary` 本身偏中性, 强行加饱和只会得到一片土黄; 一度改用皮肤自带设定集插画, 又被否（"背景用我的壁纸"）
  - **最终口径（2026-11-01 深夜）**: 背景改用**当前桌面壁纸** —— 从 `~/.local/state/noctalia/settings.toml` 读 `[wallpaper.monitors.eDP-1] path`（回退 monitors 首项 / last / default）, sidecar 用 `magick` 压到 1600px q70 存 `sidecar_data/.../wallpaper.jpg`（约 250KB）, 按源文件 mtime 重算, 换壁纸自动重载
  - **全部拍平**: 去掉所有渐变（径向暗角、侧栏 linear-gradient）、所有 `box-shadow`（含卡片/输入框/桌宠气泡/猫的 drop-shadow）与 `backdrop-filter`; 壁纸之上只盖一层纯色半透明遮罩（`skin.json` 的 `scrim`, 默认 0.5, 面板 bg-background / bg-sidebar 各 .72）
  - **最终口径（2026-11-02 定稿）**: 用户要「原配色原 UI，只加背景」—— 皮肤现在**不覆盖任何主题变量**（`skin.vars` 机制保留但不使用）, 只做三件事: 壁纸铺在 `#root` 之下、`body` 与 `[class~="bg-background"]` 设成透明让壁纸透出来、盖一层半透明遮罩 —— **遮罩颜色必须是宿主自己的 `var(--background)`**, 用近黑色会把整窗色相拉偏（用户反馈「颜色不对劲」）; 默认 0.4, `star-pet skin art <0-0.95>` 可调（0.9 时壁纸只剩淡淡纹理, 但色温和原版一致）; 侧栏/卡片/输入框/圆角/字体/配色全部保持宿主原样
  - **两个连环 bug（都踩了）**: (1) 热更包里带了不完整的 `skin`（缺 wallpaper）, `Object.assign` 把壁纸对象冲掉, `applySkin` 于是删掉背景层 —— 首帧有、两秒后没; 修法: 皮肤只在首次注入下发 + 图层侧对 `next.skin` 做浅合并; (2) `Number(null) === 0`, 把「跟随默认」的 `scrim: null` 读成 0, 遮罩强度归零 —— 判空必须显式
  - 保留: 上游源码 `~/.local/share/antigravity-star-suite`（26MB, 供 `tools/build-assets.sh` 重建素材）, 独立窗口版 Electron 桌宠仍可 `npm run start:widget` 手动跑

- **noctalia 从 AUR 夜版切换到官方稳定版 5.4.0 与 v5 配置分层真相 (2026-10-31, 完成)**:
  - 处置: `aur/noctalia-git 5.0.0.r5361`（真实串 `v5.0.0-beta.10-17-gf840b01baf16`, 8-31 编译）换成官方仓库 `noctalia 5.4.0-1.1`（cachyos-extra-v3 重建, 打包者 CachyOS, 非 AUR 无需审 PKGBUILD）, 依赖 `cachyos-niri-noctalia` 靠包名本身满足; 上游最新 tag 是 5.4.1（10-29）尚未进仓, 下次 `-Syu` 自然跟上
  - **pacman 撞坑**: `pacman -S --noconfirm noctalia` 会在「与 noctalia-git 冲突, 删除它吗」这一步采用默认值 **No** 直接失败; 且 noctalia-git 提供虚包 `noctalia` 被 `cachyos-niri-noctalia` 依赖, 普通 `-R` 会被拒绝; 可用解法是 `pacman -Sw`（先只下载, 失败则不动现有安装）→ `pacman -Rdd`（跳过虚包依赖检查显式移除）→ `pacman -S` 安装
  - 该包 33 个依赖全为无版本约束的普通库名, 所以这次只动 noctalia 一个包, 不引发部分升级（`pacman -Dk` 事后报数据库正常）
  - **配置分层真相（最重要）**: v5 起运行期实际读写的设置在 `~/.local/state/noctalia/settings.toml`（state-dir 覆盖 config-home）, `~/.config/noctalia/settings.json`（chezmoi 里那份 29KB）已是 v4 遗留、运行时不读; 仍生效的只有 `~/.config/noctalia/settings.toml` 里的 `[hooks] wallpaper_changed`、`colors.json`、`plugins/` 目录; `noctalia config export` 打印合并后的有效配置（当前 301 行）, `noctalia config validate` 校验
  - 5.4 调色板键名改名 `surface_variant`→`surface_container`、`outline`→`outline_variant`（启动日志自动迁移 lockscreen 里的旧用法）, 但 `noctalia theme` 生成时**新旧键名双写**（实测 74 键新旧都在）, 故 `morandi-gen.py` 读 `surface_variant` 不会 KeyError, 无需改主题引擎
  - 5.4 的 Luau 沙箱**不再提供 `io` 库**, 旧写法 `io.open(...)` 报 `attempt to index nil with 'open'`; 正确 API 是 `noctalia.readFile(path)`（文件不存在返回 nil, 空文件返回 `""`）, 已据此修好 `clipboard-osd` 插件的远控静音判断
  - **重启配方更新**: `noctalia msg` 没有 quit/exit 子命令, 直接 `pkill -x noctalia` 会把 `wl-paste --watch` 等 runStream 子进程甩给 systemd 变孤儿、导致复制通知重复; 正确顺序是先 `pkill -P $(pgrep -x noctalia)` 清子进程再杀主进程
  - 清理: 删掉 settings.toml 里遗留的 `[widget.cat] type = "noctalia/bongocat:cat"`（该定义没挂在任何 bar 上; 注意 `noctalia/bongocat [official] 1.1.4` 插件本体**仍在**, 只是 disabled, 想恢复官方弹琴猫就 `noctalia msg plugins enable noctalia/bongocat` 再重建 widget, 不要误以为上游已移除）, `noctalia config validate` 现为 0 警告且启动日志无 WRN/ERR
  - 收尾已完成（见下一条）: chezmoi 改管 state 版 settings.toml; greeter 切换脚本 `~/tmp/switch-greeter.sh` 待执行
  - 备份: `~/tmp/noctalia-backup-20261031/`（config / state / cache / 旧二进制 / 旧 share 资产 / `settings.toml.post-upgrade`）

- **noctalia 收尾: dotfiles 收纳 state 配置、polkit 代理缺失真相与 147 包更新积压 (2026-10-31, 部分待执行)**:
  - **dotfiles 改造已完成并推送**: `chezmoi add ~/.local/state/noctalia/settings.toml`（落在源端 `dot_local/private_state/noctalia/settings.toml`, chezmoi 自动识别 state 为私有目录）, 并从源里删掉失效的 `dot_config/noctalia/settings.json`(924 行) 与 `plugins.json`(65 行); 判别依据是 `strings /usr/bin/noctalia` 里 `settings.json`/`plugins.json` 出现 **0 次**, 而 `settings.toml`/`config.toml`/`colors.json` 都有引用; 两份旧文件归档在 `~/tmp/noctalia-backup-20261031/legacy-config/`; 提交 `ec03aa0` 已推送成功（github 当时已恢复）
  - **polkit 认证代理根本没装（重要新发现）**: `~/.config/niri/cfg/autostart.kdl` 一直 spawn `/usr/lib/polkit-kde-authentication-agent-1`, 但该文件属于 `polkit-kde-agent` 包, **从未安装**（`pacman -Q polkit-kde-agent` 为空）, 所以会话内没有任何 polkit 认证代理; 实测 `pkexec` 直接报 `Error creating textual authentication agent`, 这就是 MEMORY 里「pkexec 卡死」的真正根因; 该包仅 82KB, 依赖（kcoreaddons/kcrash/ki18n/kirigami/knotifications/kwindowsystem/polkit-qt6/qt6-*）全已就位
  - noctalia 二进制里确实有自带 polkit 面板（`PolkitAgent` / `org.noctalia.PolkitAuthenticationAgent` / `auth.polkit.*` 文案）, 但 5.4.0 上未注册, `noctalia msg plugins list`（316 条）里也没有 polkit 插件; 官方 registry 里 `polkit-agent` 标 official 但 shell 未收录, 所以暂时只能靠 polkit-kde-agent
  - **greeter 替换可行性与安全垫**: 官方 `noctalia-greeter 1.7.0` 与已装 git 版 1.0.0.r168 的 `setup_greeter_system.sh` / `setup_greetd_pam.sh` **逐行相同**（不需要重跑系统级配置）, 文件布局一致且多一个 `noctalia-greeter-xsession`; 状态目录 `/var/lib/noctalia-greeter`(greeter:greeter 0750) 需先备份; `getty@tty2` 默认 **disabled**（登录层翻车没有本地文本通道）, `sshd` 已 enabled+active 可远程兜底; greetd 的 `[default_session] command` 仍指向 `/usr/bin/noctalia-greeter-session` 不变
  - **系统更新积压 147 个包**: 重点 nvidia-580xx 580.178.04→580.196.07（DKMS 需重建并重启）、KDE Plasma 6.8.1→6.8.2 全家桶（kwin/breeze/powerdevil/xdg-desktop-portal-kde）、hyprland 0.57.0、ghostty 1.3.1→1.4.0、harfbuzz 14.6→15.0.0（大字版本通常伴随重建）、gcc/clang/llvm 工具链、limine 12.9.4（引导器）、zed 1.26.2、reaper 7.83、wine 11.21、tailscale 1.104.4、shelly 3.1.10; 建议一次 `paru -Syu` 后重启
  - 备份: 同上 `~/tmp/noctalia-backup-20261031/`（另含 `greeter-git/` 5 个旧二进制 + share 资产, 回滚直接 `sudo cp -a ... /usr/bin/`）

- **Steam 大屏幕模式卡顿根因: niri 全局模糊规则把 Steam 客户端本体也圈进去了 (2026-10-31, 已修复)**:
  - 现象: Steam 大屏幕模式操作发滞, 翻页与选中不跟手
  - 根因: niri 全局窗口规则 `match app-id=".*"` 带 `opacity 0.98` + `blur true`, 而游戏窗口规则只覆盖 `^steam_app_.*` 与 `^pbz[.]exe$`, **Steam 客户端本体的 app-id 恰好就是 `steam`** 于是掉进全局规则, 大屏界面每帧整屏高斯模糊压在核显上
  - 关键发现: niri 窗口规则是**先匹配先生效**, 后在下面补一条 `match app-id="steam"` 的专属规则**不会**覆盖前面的全局规则 (实测合成器 CPU 纹丝不动, 仍是 17.5%); 正确做法是在全局规则里加 `exclude app-id="steam"` 把 Steam 踢出去, 让它落到专属规则
  - 实测 A/B (niri 合成器 CPU, 大屏界面可见): 改动前 17.5% → 全局关掉 blur 的理论下限 12.0% → exclude + 专属规则 12.4% (已贴到下限), 合成器负载降约 29%
  - 落地: `dot_config/niri/config.kdl` 全局规则加 `exclude app-id="steam"`, 并新增 steam 专属 window-rule (opacity 1.0 / geometry-corner-radius 0 / clip-to-geometry false / blur false), 已 chezmoi apply + 热重载生效, dotfiles 提交 d2b2a01
  - 踩坑: 本版 niri **没有** `niri msg action reload-config` 子命令, 正确命令是 `niri msg action load-config-file`; 且 `niri validate -c <chezmoi源文件>` 会因 `include "./cfg/*.kdl"` 的相对路径解析失败, 必须校验**目标文件** `~/.config/niri/config.kdl`
  - 备份: `~/tmp/niri-config.kdl.bak-20261031-191129`, `~/tmp/niri-pre-exclude.kdl`

- **盖世小鸡 启明星2 的 2.4G 接收器会跟随手柄平台模式切换 USB 身份, Xbox 身份在 Linux 枚举失败而 PS4 身份秒通 (2026-10-31, 已解决)**:
  - 硬件身份: VID `0x3537` (Zikway/GameSir), 2.4G 接收器枚举为 `3537:1098` "2.4G XBOX 360 For Windows" (制造商串 "2.4G", 全速 12Mbps), 三接口 —— iface0 为 `ff/5d/01` 厂商类, 被 xpad 按类别别名接管并起名 "Generic X-Box pad"; iface1 为 HID 键盘; iface2 为厂商 hidraw
  - 真正根因: 这类接收器是"跟随手柄平台模式"的伪装型 dongle, 会按手柄当前平台模式换一套 USB 身份 —— Xbox 平台冒充 `045e:028e` 并带备用身份 `3537:1098` (三接口: ff/5d/01 厂商类 + HID 键盘 + 厂商 hidraw), Switch 平台冒充 `057E:2009`, PS4 平台冒充 `054c:09cc` DualShock 4; Linux 上**只有 Xbox 那条路死掉**: `045e:028e` 每次插入连续 3 次 `-110` 超时 (每次卡 6 秒), 内核触发 `usb usb3-port9: attempt power cycle`, 累计 14 次枚举失败后才退回 `3537:1098`, 而 xpad 接管 3537:1098 后射频侧从不投递数据 (evdev 探针 180 秒 0 事件, 同期 `EVIOCGRAB` 可成功证明无人独占抓取)
  - 排查误判教训: 有线时同样先尝试 `045e:028e` 失败 (-71 / -110) 再落到 `054c:09cc`, 一度被误读成"有线能用 / 无线坏了"; 实际两次跑的都是同一套 PS4 平台身份, 与插线还是插 dongle 无关 —— 判断依据必须是 dongle 当前呈现的 VID/PID, 而不是接线方式
  - 手柄自身组合键 (官方 n2lite 文档): 【X+HOME】= 2.4G 接收器模式 (绿灯), 【B+HOME】= 蓝牙 (蓝灯), 【A+HOME】= 安卓 (黄灯), 短按 Home 1 秒开机并可组合 A/B/X/Y 指定模式, 长按 Home 5 秒关机, 长按【Home+截图键】3 秒强制进配对, 长按【菜单键+视图键】可把通道灯切回绿灯
  - 关键排查手法: Steam 的 `logs/controller.txt` 是最可靠的交叉验证点, 里面会打印 SDL 对 VID/PID 的完整按键轴映射, 能直接判断"驱动层通了但游戏层没映射"还是"驱动层就没数据"
  - 解决方案与铁证: 把手柄切到 PS4 平台模式后 dongle 立刻以 `054c:09cc` DualShock 4 正常工作, 只剩单接口 `3-9:1.0` (class 03) 由 usbhid + hid-playstation 接管, 输入节点 `event257` + `js1` 正常; 决定性证据是 `/sys/class/power_supply/ps-controller-battery-00:01:6c:ee:95:de` 稳定报 `capacity=100 / status=Full`, 该电量由 hid-playstation 从手柄真实 HID 报文解析而来, 能读出来就说明无线链路完全打通
  - 备选与注意: 若日后要回到 Xbox 平台模式, 需注意该身份在本机 xHCI 口 (`3-9`) 上枚举不稳, 可换 USB 2.0 口试 (集线器 `3-6` 为 Huasheng USB2.0 HUB) 或到 Windows 上交叉验证; 蓝牙方案为 `xpadneo-dkms 0.10.5-1` (在 cachyos 官方源, 非 AUR 无需审 PKGBUILD)
  - 调试脚本: `~/tmp/pad-watch.sh` 与 `~/tmp/pad_probe.py`, 前者按 by-id 自动解析当前手柄节点并实时打印 KEY/ABS 事件

- **影之刃零 (Phantom Blade Zero, Steam AppID 4115450) 卡顿根因与实时优化 (2026-10-31, 桌面侧已落地, 游戏内设置待重启)**:
  - 硬件链路: COLORFUL X15 XS 22, i5-12450H (4P+4E / 12 线程) + RTX 3050 Laptop 4GB (GA107M, 功耗上限 70W / 核心上限 2100MHz), eDP-1 1920x1080@144 且 EDID 支持 VRR, 内屏与 niri 合成都在核显 i915 上, 独显帧经 dma-buf 跨 GPU 交给核显合帧, 无 MUX
  - 根因一 (权重最大): 系统 CPU 严重超卖, load average 20-21 对 12 线程, 游戏本体 GameThread 独吃 700-780%, 而 `/opt/Antigravity/resources/bin/language_server` 单进程吃 166% CPU + 5.5GB RSS 且被 ananicy-cpp 提到 nice=-8, 另有两个 DSH 构建遗留守护进程 (Gradle java 17741 / Kotlin java 18108) 占 3GB 内存与 4.8GB zram
  - 根因二: niri 的全局 window-rule `match app-id=".*"` 把 opacity 0.98 + blur true 套到了游戏窗口上, 每帧 1080p 画面被整屏高斯模糊后才呈现, 合成器 CPU 41-48%, 144Hz 帧预算 6.94ms 被吃穿
  - 根因三: 显存长期贴顶 3735-3807 / 4096 MiB (仅余 240MB), UE5 流送必然溢出到共享内存走 PCIe
  - 根因四: 独显 86-87°C 触发 SW Thermal Slowdown (累计 2.6s), 核心在 1740-1837MHz 之间来回抖 (上限 2100), CPU 包 93°C, 散热是硬件瓶颈
  - 处置与效果: kill 构建守护进程 (内存 21499→18539MB, zram 14.3→9.9G); 语言服务器 renice 19 + ionice idle 后 SIGSTOP; 新增 niri 游戏窗口规则 (`^steam_app_.*` / `^pbz[.]exe$`, opacity 1.0, blur false, corner-radius 0, clip-to-geometry false, open-fullscreen true, variable-refresh-rate 标记) 并把 eDP-1 开 VRR; `niri msg action fullscreen-window` 让游戏进独占全屏 → 合成器 CPU 41-48% 降到 20%, Xwayland 14% → 6%, 非游戏 CPU 总量 ~500% → ~140%
  - 新增工具: `~/.local/bin/game-mode.sh on|off|status`, 用 SIGSTOP/SIGCONT 冻结 Antigravity 语言服务器 / slugcatpet / Bettbox, 状态落 `$XDG_RUNTIME_DIR/game-mode.frozen`, 故意不含 Zen 浏览器与 Steam (前者是对话界面, 后者是游戏父进程)
  - 待做 (都需退出游戏): GameUserSettings.ini 的 `FrameRateLimit` 0 → 60 与 `sg.ResolutionQuality` 100 → 70 (或在游戏内开 DLSS 质量档并锁 60 帧), 关 Steam 内嵌覆盖, 装 mangohud 看帧时间, 长期方案是清灰换硅脂
  - 超分能力核实 (2026-10-31): 游戏随包带完整 NVIDIA 链路 —— `Engine/Plugins/Runtime/Nvidia/DLSS/Binaries/ThirdParty/Win64/nvngx_dlss.dll` (58.9MB) 与 `nvngx_dlssd.dll`, `StreamlineCore` 里还有 `nvngx_dlssg.dll` / `sl.reflex.dll` / `sl.common.dll`, 且游戏进程 maps 里已加载它们, 前缀内 Proton 生成 `nvapi64.dll` + `_nvngx.dll`, 宿主 `/usr/lib/libnvidia-ngx.so.580.178.04` 在位, 说明 NVAPI/NGX 链路本来就通, 不需要额外启动参数; 主程序里有 `UpScaleMode` / `DLSSMode` / `DLSSPreset` / `DLSSRRPreset` / `DLSSGMode` / `XeSSMode` 等枚举, 菜单确实暴露 DLSS; 但 RTX 3050 是 Ampere, 没有 Ada 的硬件光流加速器, DLSS 帧生成不可用 (菜单灰掉属正常), 光追关着时 DLSS RR 也用不上, 能开的就是 DLSS 超分 + Reflex
  - 踩坑: niri 26.04 的 output 段 `variable-refresh-rate` 只能写裸标志 (带 true / false / "on-demand" 都会被判 unexpected argument), 但 window-rule 里却要写 `variable-refresh-rate true`; KDL 1.0 字符串里 `\.` 是非法转义, 正则要写 `^pbz[.]exe$`; 开 VRR 后 niri 会打 `early VBlank` 帧时钟告警 (实测 2 条 / 30 秒, 关掉即 0), 属诊断噪音
  - 备份: `~/tmp/niri-test`, `~/tmp/verify-niri` 为本次校验用配置副本

- **桌面鼠标卡顿根因: 全局 PRIME offload 叠加全屏桌宠与全窗口模糊吃满 144Hz 帧预算 (2026-10-29, 已改配置待重登验证)**:
  - 现象: 鼠标移动明显卡顿, 但鼠标本体健康 (MCHOSE G3 V2 2.4G, 端点 bInterval=1ms 即 1000Hz, dmesg 无 USB 复位/断连/HID 错误)
  - 硬证据: 面板 eDP-1 挂在 card1=i915 核显且 niri 合成在 renderD128 核显, 但整个用户会话被 `~/.config/environment.d/nvidia.conf` 与 niri config.kdl 双重注入 `__NV_PRIME_RENDER_OFFLOAD=1` / `__GLX_VENDOR_LIBRARY_NAME=nvidia` / `__VK_LAYER_NV_optimus=NVIDIA_only` / `DRI_PRIME=pci-0000:01:00.0`, 于是 zen/steam/Bettbox/ghostty/noctalia 全部持有 card0(10de) 图形上下文, 独显长期停在 P5 / 472-607MHz
  - 负载实测: 鼠标静止 niri 23% CPU / iGPU render 65%, 一移动光标 niri 48-52% CPU / iGPU 114-117% (超实时线即掉帧), 144Hz 每帧预算只有 6.94ms
  - 放大器二: slugcatpet 的 GTK3 桥每 16ms 整屏清零并重绘 1920x1080 透明 TOP 层 (8.3MB/帧 wl_shm) 常驻 46% CPU, 合成器被迫每帧整屏重混合
  - 放大器三: niri 全窗口 `opacity 0.98` + `blur true` 使任何窗口都无法直出扫描 (禁用 blur 单此项 iGPU 就从 65% 掉到 47%)
  - 处置: nvidia.conf 只保留 QT_X11_NO_MITSHM=1; niri config.kdl 删掉两条注入; Zen 的 flatpak override 用 `--unset-env` 去掉三个 NVIDIA 变量; Krita/DaVinci 新增 `~/.local/share/applications` 覆盖改 `prime-run` 前缀 (Blender/LunarClient 早已如此); 桌宠改按 Qt 侧脏矩形 `queue_draw_area` 局部重绘
  - 效果 (桌宠部分已即时生效): 桌宠 CPU 41.5-46.5% → 10-18%, niri 空闲 23% → 12.6-17%, 移动光标时 niri 48-52% → 16.3%, iGPU 114-117% → 59.5%, 移动光标不再放大合成器负载
  - 待验证: environment.d 与 niri environment 段需重登生效, 重登后 `nvidia-smi` 不应再出现 zen/steam 的图形上下文; Zen 的 `layers.dmabuf.disable=true` 留作下一步实验 (核显路径下大概率不再需要, 去掉可再省一笔合成开销)
  - 回滚备份: `~/tmp/zen-flatpak-override.bak`, `~/tmp/niri-config.kdl.chezmoi.bak`, 桌宠原文件 `~/tmp/gtk3_bridge.py.orig`, 桌宠也可用 `SLUGCATPET_LEGACY_FULL_REDRAW=1` 退回整屏重绘
  - 次要嫌疑 (未处理): WiFi 在 ch1 (2412MHz 20MHz) 且蓝牙常开, 与 2.4G 鼠标接收器同频, 只会造成偶发跳帧而非持续卡顿

### 归档索引

2026-10-26 及更早的条目已整段移入 `~/MEMORY-archive.md`（原文未删减，要回溯历史改动时去那里查）
- 2026-10-26 平板通信共享掉线与看门狗 v3 出口排除法、Tailscale 双端自愈、kde-material-you-colors 单元风暴清理
- 2026-10-18 ~ 10-25 ReveriePaint-native 六项（本地化规范、KRA 导入、撤销滑杆、MotionPredictor 清理、手写笔侧键、面板越界）与 K60 ColorOS 16.1 脏刷
- 2026-10-19 ~ 10-23 NyanoMuse 四十余项（情绪系统、多气泡、跨端同步、长期记忆与冲突消解、grill-me 原生工具化）
- 2026-10-18 ~ 10-19 nanoMuse 全端部署、UU 远程被控端、CodeBuddy、DSH 升级、WorkBuddy 卡顿、IDEA 配色
- 2026-09-12 ~ 10-02 设备刷机与备份、MicYou 迁移、Bettbox 切换、Dufs+Cloudflare、ReveriePaint v1.4.0

## 设备

### Redmi K60 (mondrian / ed3fdd92)
- 系统：ColorOS 16.1 / Android 16（ROM: ClearSkys 移植版，基底 OnePlus Ace 6，内核 5.10.246-AetherKernel），SukiSU Boot root
- 底层备份：位于 `~/刷机/k60/原厂备份/`（EFS/基带 `modemst1/2`、`fsg/fsc`，校准 `persist/persistbak`，`devinfo`，HyperOS 4 双槽位全套原厂镜像）
- 模块链：YABP、Zygisk Next (匿名内存模式，enforce-denylist 保持 0)、Vector (service.sh 修正为 unshare -m)、Tricky Store + TS Enhancer Extreme (内置 keybox)、HMA-OSS Zygisk、Material You for ColorOS、magic_mount_rs
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）、WeType-Kaomoji、WeTypeHook、couiexpressive、soulfrog
- 授权机制：轻量主板 ID 验证（本机 ID `0x0000043bfce1db8a`），授权凭据位于 `/mi_ext/product/etc/security/verificationlist.bin`（SHA-256 Token）；补丁包采用 Zip 伪加密，消除中心目录标志位后卡刷成功
- adb 要点：操作前核对 `dumpsys window mCurrentFocus`；用户使用手机时切勿抢占操作

### 一加平板2 Pro (OPD2413 / c84b9192)
- 硬件规格：骁龙 8 至尊版 (SM8750P / sun 平台)，Wi-Fi 版开发者选项 OEM 解锁后 Fastboot 物理音量键确认秒解
- 系统内核：ColorOS 16 (Android 16 / SDK 36)，SpiderDroid GKI 6.6.118 (sun 定制)，KowSU Pro v3.3.0 (35700-2 / UAPI=2) + 内核内置 SuSFS 2.3.0
- 原厂备份：位于 `~/刷机/一加平板2Pro/原厂备份/`（`stock_boot.img` 96MB、`stock_init_boot.img` 8MB）
- 模块链：YABP、Zygisk Next (匿名内存)、Vector (API 102)、Tricky Store + TS Enhancer Extreme、HMA-OSS Zygisk (JamesDSP 因 Android 16 AIDL 架构不兼容已移除)
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、fuckbiliads、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）
- 游戏防检测 (三角洲行动 com.tencent.tmgp.dfm)：
  - 内核层：KernelSU `kernel_umount`、`selinux_hide`、`avc_spoof` 特性全开并持久化保存
  - 属性伪装：TS Enhancer Extreme 伪装 `green` 与锁 bootloader；Tricky Store `target.txt` 纳入名单；Vector Xposed 白名单机制对游戏零注入
  - 应用列表隐藏：HMA-OSS 直写双路径配置（`/data/misc/hide_my_applist_aimdadlejpdcwkeh/config.json` 属主 `system:system` 600 与 `/data/user/0/org.frknkrc44.hma_oss/files/config.json` 属主 `u0_a346:u0_a346` 600），屏蔽 KowSU Pro、Vector、LuckyTool、CorePatch、fuckbiliads、HMA-OSS
  - 运维脚本：`~/.local/bin/android-hide-app`（`android-hide-app [-l] [-r] <包名>`），自动维护双路径与 Tricky Store 名单，全静默执行无触摸交互
- 禁忌红线：严禁刷入第三方 Recovery；严禁跨版本/降级刷机触发 ARB 熔断；严禁使用手机端防误触或手写笔旁路模块（`patch-trackmotion`、`disable-stylus-blocker`）以保护平板原生防误触与手写笔功能

### 盖世小鸡 启明星2 (GameSir Nova 2 Lite)
- 识别特征：VID `3537` (Zikway/GameSir)，接收器按手柄平台模式换身份 —— Xbox 平台 `045e:028e`(本机枚举失败)+ 备用 `3537:1098`，Switch 平台 `057E:2009`，PS4 平台 `054c:09cc` DualShock 4
- 组合键：【X+HOME】2.4G 接收器（绿灯）·【B+HOME】蓝牙（蓝灯）·【A+HOME】安卓（黄灯）· 长按 Home 5 秒关机 ·【Home+截图键】3 秒强制配对 ·【菜单键+视图键】切回绿灯
- 现状：**PS4 平台模式 + 2.4G 接收器** 为已验证可用配置（USB 呈现为 `054c:09cc`，hid-playstation 接管，`ps-controller-battery-*` 电量可读）；Xbox 平台模式下 dongle 的 `045e:028e` 身份在本机 xHCI 口上会枚举超时，无线不可用
- 官方文档：`https://doc.xiaoji.com/zh/n2lite/`（手柄）与 `https://doc.xiaoji.com/zh/n2litedongle/`（接收器）

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`，壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now；`/etc/greetd/config.toml` 的 default_session 为 `/usr/bin/noctalia-greeter-session`（user greeter），initial_session 为 `niri-session`
- 提权通道：`polkit-kde-agent`（提供 `/usr/lib/polkit-kde-authentication-agent-1`，niri autostart 里有 spawn 行）；该包此前一直未安装导致 pkexec 无代理可用，已列入 `~/tmp/switch-greeter.sh` 一并补装；`sshd` 常开可作远程兜底，`getty@tty2` 默认关闭
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（含 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku/write_hyprland/write_idea）；新应用主题化必须扩展此脚本，严禁直改应用配置；Wine 应用与 Krita 不走主题引擎
- Niri：动画 stiffness 180-220 / damping-ratio 0.8 弹性轻柔滑行（cfg/animation.kdl）；窗口间距 8px（cfg/layout.kdl）；全局 opacity 0.98 + blur true（`draw-border-with-background false` 必设防聚焦实心边框）；全局规则排除 Krita/Loupe/Kando/SPlayer/cs2/gamescope/steam 与全部游戏窗口类（`steam_app_.*`、`pbz[.]exe`、`OLGame.*`、`.*[Oo]utlast.*`），**排除必须在全局规则里写 exclude，补专属规则不生效**；游戏专属规则给 `open-fullscreen true` + `variable-refresh-rate true` + 关模糊
- Ghostty：输入法修复依赖 wrapper `~/.local/bin/ghostty`（`env -u GTK_IM_MODULE` 解决不转发 key release 导致 fcitx5 状态机异常）；term_bg 公式 `max(l_b+0, 4)`；集成 Master GLSL 光标着色器与连字支持
- Fcitx5：bamboo-dark 皮肤（morandi-gen 注入），竖排候选，rime_ice（雾凇拼音）；支持 niri ext-background-effect 候选框模糊
- Fastfetch：write_fastfetch 全量生成 config.jsonc；源码中 ≥U+F0000 码点必须使用 8 位 `\U000FXXXX` 转义
- Noctalia 重启：先 `pkill -P $(pgrep -x noctalia)` 清掉 runStream 子进程, 再 `pkill -x noctalia`, 然后 `setsid nohup noctalia > ~/tmp/noctalia-restart.log 2>&1 < /dev/null & disown`；运行期配置在 `~/.local/state/noctalia/settings.toml`, `~/.config/noctalia/settings.json` 已失效
- OBS：屏幕采集依赖 mesa EGL 核显渲染（强制覆盖 desktop Exec：`env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json obs`）；编码器使用核显 QSV（`obs_qsv11_v2`）；B 站推流插件位于 `~/.config/obs-studio/plugins/bilibili-stream-for-obs/`（含 PR #27 扫码登录补丁）
- Caelestia KDE Shell：KWin 6.7.4 + caelestia-shell 2.4.0 精简安装，配置位于 `~/.config/quickshell/caelestia/`，会话 `~/.local/bin/start-kwin-caelestia.sh`；缩略图依赖 PipeWire，nvidia.conf 严禁设全局 PRIME offload 变量防黑屏
- 显卡策略：默认全部走核显，严禁在 `environment.d/nvidia.conf` 或 niri `environment` 段设全局 PRIME offload（面板与合成器都在核显，全局强制独显会让每帧跨 GPU 拷贝并吃掉 144Hz 帧预算）；需要独显用 `prime-run` 前缀，桌面项覆盖见 `~/.local/share/applications/` 下的 blender / org.kde.krita / DaVinciResolve / com.lunarclient.LunarClient
- Zen 浏览器 (Flatpak)：2026-10-29 已用 `flatpak override --user --unset-env` 去掉 `__NV_PRIME_RENDER_OFFLOAD` / `__GLX_VENDOR_LIBRARY_NAME` / `VK_ICD_FILENAMES`，改走 Mesa 核显；user.js 仍启用 `layers.dmabuf.disable=true` 防止 2D canvas 合成失效；D-Bus portal 授权只读访问 fcitx5 目录
- SPlayer-Next：AUR `splayer-next-bin`，二进制 `/opt/SPlayer-Next/SPlayer-Next`，命令 `/usr/bin/splayer-next`
- slugcatpet 桌宠：`~/Projects/slugcatpet`，GTK3 窗口必须设为 Layer.TOP；GTK3 桥按 Qt 侧 `_dirty_rect` 算好的脏矩形做 `queue_draw_area` 局部重绘，禁止退回每帧整屏 `queue_draw`（全屏透明面整屏重绘会把合成器整屏混合负载拉满）

## 项目

### MiuiCamera-Fix — `~/Projects/MiuiCamera-Fix`
- 小米澎湃OS移植包相机机型与版本校验不匹配强退修复 Xposed 模块（Java + Xposed API 82，目标包 `com.android.camera`，测试机 ed3fdd92）
- 包名：`io.github.lanrhyme.camerafix`
- 机制：Hook `G6.c.w()` 返回 `false`，Hook `G6.e.g()` 修正 `f2302a = Boolean.FALSE`，Hook `ActivityBase` Handler 丢弃 Message 11 退出消息
- 仓库：`https://github.com/LanRhyme/MiuiCamera-Fix`（Release Tag: `v1.0.0`）
- 构建：`./gradlew assembleRelease` + `adb install -r app/build/outputs/apk/release/app-release.apk`

### WeType-Kaomoji — `~/Projects/WeType-Kaomoji`
- 微信键盘表情面板颜文字注入与分类增强 Xposed 模块（Kotlin + LibXposed API 102，目标包 `com.tencent.wetype` 3.5.3，测试机 ed3fdd92）
- 包名：`io.github.lanrhyme.wetypekaomoji`
- 机制：`w.C` 注入分列数据，`a1.b0`/`a1.a0` 移除推荐表情并将颜文字置首；`x.getItemViewType` 隔离独立复用池类型 88；`ImeEmojiBoardView` 注入胶囊分类栏；内置 250+ 萌系颜文字
- 仓库：`https://github.com/LanRhyme/WeType-Kaomoji` 与官方模块源 `Xposed-Modules-Repo/io.github.lanrhyme.wetypekaomoji`（Release Tag: `1-1.0.0`）
- 构建：`./gradlew assembleRelease` + `adb install -r app/build/outputs/apk/release/app-release.apk` + `adb shell pkill -9 -f com.tencent.wetype`

### pi-web / pi-neostudio — `~/Projects/pi-web`
- 基于 agegr/pi-web 的 pi agent Web UI（Next.js 16 + React 19 + Tailwind 4，端口 30141），独立语义化版本发布（npm 包 `pi-neostudio` + GitHub Release）
- 上游同步：选择性移植（带 postinstall 空 bgColors 守卫）；`npm run dev` 运行；构建需注意生产环境变量覆盖，发布走 GitHub Actions matrix
- 发布鉴权：npm 需使用 Granular Access Token（绕过 2FA 进行发布）

### ReveriePaint-native — `~/Projects/ReveriePaint-native`
- 笔刷与手势引擎绘画软件（Kotlin + C++/Krita 核心，包名 `com.reverie.paint`，测试机 ed3fdd92）
- 笔刷：KisBrushOp::paintLine + KisFakeRunnableStrokeJobsExecutor 同步驱动异步管线；静态注册 kritadefaultpaintops_static 防 DSO 段错误；ScratchpadCanvas 试画栏改用 awaitEachGesture 零延迟捕获单击打点与笔画起点并读取 historical 高频采样点，按弧长均匀插值步进 dabs，解决线条断裂成点阵虚线问题
- 图层架构：手势消费仲裁与 combinedClickable 共存；列表级长按接管拖拽；松手冻结 pendingOrder 存层名防索引错位；向下合并解除源层剪裁通道限制并原子化事务与图层移除
- 快捷键与外接键盘：StylusDriver 与手写笔 Adapter 增加 isStylusKeyEvent 判定；keyEventToString 兼容 Meta 与 Ctrl 统一映射；handleKeyEvent 引入长按连发节流与单次触发限制
- 手势与拾色：解除 canEyedrop 对 !penOnlyMode 的限制，单指长按画布吸色与手写笔吸色并存；ACTION_MOVE 增加长按容差检测；双指捏合平移触发时立即执行 cancelPendingShapeGesture 回滚首指误落节点
- 渲染引擎与投影管线：renderToBuffer 在后台异步调度器活跃时强制 waitForDone 阻塞等待合并完成，空闲时才由 compositeLayersRange 毫秒级同步合成笔画与预览脏区，杜绝多线程并发读写 projection 瓦片导致的 KisTiledExtentManager SIGABRT 闪退
- 崩溃诊断引擎：接入 ReverieCrashHandler (C++) 信号安全拦截器 (SIGSEGV/SIGABRT/SIGBUS/SIGFPE/SIGILL) 与 128KB 独立信号备用栈，捕获 48 帧 Native 符号栈与寄存器状态；Java 层集成 Thread.UncaughtExceptionHandler；双端搭载容量 25 条的 Breadcrumbs 环形操作轨迹；启动阶段弹出 Morandi 诊断弹窗
- 构建：`scripts/build_native.sh`（QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a，纯 Kotlin 改动直接 assembleDebug）

### Horizon — `~/Projects/Horizon`
- 现代化 Android 平板浏览器（GeckoView + Mozilla Android Components + Rust Firefox Sync，前台 Jetpack Compose，针对一加平板 2 Pro 定制）
- 应用名：`Horizon`，包名：`top.lanrhyme.horizon`
- 架构特色：Zen / Arc 风格三态可折叠侧边栏、多工作区（Spaces）、同屏双开分屏（Split View）、WebExtensions 插件生态、全量 Firefox 跨端同步、Morandi 与 Material You 双轨动态色彩

### Krita 插件套件
- 源码位于 `~/.local/share/krita/pykrita/`（FolioLayers v1.2.1、AdvancedColorPicker v1.1.0、SimpleHSVSliders v1.0.1、MorandiUI、InfiniteCanvas v1.0.0、GmicFilters）
- 关键规范：打包 zip 根目录必须含 `<name>.desktop`（`ServiceTypes=Krita/PythonPlugin` 且 `X-Python-2-Compatible=false`）；Docker 必须继承 KisMainWindow 的 DockWidget；G'MIC 面板滤镜参数必须带显式参数并用 `-o[0]` 指定输出

### 其他项目
- **threejs-dragon-flight**：`~/Projects/Tests/threejs-dragon-flight`，3D 巨龙空域自由翱翔飞行模拟器，Three.js + 骨骼动画 + 云海粒子与音效
- **threejs-pistol-disassembly**：`~/Projects/Tests/threejs-pistol-disassembly`，3D 手枪机械结构拆解与精密爆炸图交互系统，Three.js + 机械声效 + 分步教学
- **voxel-jrpg-village**：`~/Projects/Tests/voxel-jrpg-village`，日式幻想体素村落 JRPG 网页，Three.js + Web Audio API 原生程序化和弦合成
- **Pi Codex GUI**：`~/Project/pi-codex-gui`，Tauri 2 + bridge.js（RPC 模式下事件转发格式必须为 `{ ...ev, type: 'ui_request' }`）
- **bilibili-pixel-danmaku**：`~/Projects/bilibili-pixel-danmaku`，PySide6 弹幕助手，莫兰迪配色经 morandi_colors.json 热更新，启动项由 chezmoi 托管
- **Pi Agent TUI**：`~/.pi/agent`，zentui/open-tui 扩展，morandi-gen 的 write_pi 同步配色
- **Krita-MobileUI**：`~/Projects/Krita-MobileUI`（暂停中）

## 安装与服务

- **nanoMuse**：v1.0.5 跨设备 Agent；桌面端 AppImage 部署于 `~/.local/opt/nanomuse/nanoMuse.AppImage`，CLI 链接 `~/.local/bin/nanomuse`，桌面项 `nanomuse.desktop`；手机与平板端均通过 ADB 部署 `io.github.nanomuse.app` 并注入电池优化白名单
- **网易 UU 远程被控端 (uu-remote-linux)**：社区原生 Rust 被控端（`/usr/bin/uuremote-server`，集成 `--features wayland,portal`）；用户服务 `uu-remote-native.service`（自启常驻，支持 Wayland 活跃 Socket 自动探测与重载自愈）；依赖 `/dev/uinput` 与 `xdg-desktop-portal`；凭据存储于 `~/.config/uuremote/config.json`；支持官方客户端扫码登录绑定
- **Bettbox & FlClash**：AUR 包 `bettbox-bin 1.19.3-1` 与 `flclash-bin 0.8.93-1`；数据位于 `~/.local/share/com.appshub.bettbox/`；BettboxCore 内置 SUID root 免密启动 TUN；保留双客户端共存
- **Xiaomi MiMo Desktop**：AUR 包 `mimo-desktop 26.909.91205-2`；官方 Linux deb 打包，命令 `mimo-desktop`；针对官方包漏打 `node-machine-id` 导致登录缺失 `deviceId` 报错，已在 PKGBUILD 中补丁直接读取 `/etc/machine-id` 修复 `app.asar`
- **Dufs (WebDAV) & Cloudflare Tunnel**：AUR 包 `dufs-bin 0.46.0-2`；数据根目录 `~/WebDAV`（含 `reader/`、`backup/`）；监听本地 `5000/tcp`（全私有 Basic 认证，用户 `lanrhyme`）；配置文件 `~/.config/dufs/config.yaml`（权限 600）；搭配 Cloudflare Tunnel（`cloudflared-webdav.service`）绑定公网域名 `https://webdav.lanrhyme.top/`；systemd user 服务常驻自启（开启 linger）
- **MicYou**：本地包 `micyou 2.0.0.alpha.1-1`；Noctalia 插件开源于 `lanrhyme/micyou`；手机端安装于 K60；ufw 放行 8554/tcp、8555/udp、8443/tcp、5353/udp
- **企业微信**：deepin Wine 版 `com.qq.weixin.work.deepin`，容器位于 `~/.deepinwine/Deepin-WXWork`，启动脚本 `/opt/apps/com.qq.weixin.work.deepin/files/run.sh`
- **Waydroid**：Android 16 (LineageOS 23.2)，开启 Intel iGPU/GBM 加速；依赖 UFW 规则 `sudo ufw allow in on waydroid0`；脚本位于 `~/tmp/a16/`
- **DeepSeek Harness**：AUR 包 `deepseek-harness-bin 0.2.0rc.2-1`（`/usr/bin/dsh`）；Superpower 预设位于 `~/.dsh/.agent-presets/superpower/`；LLM 路由配置在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers`（密钥只存 `~/.dsh/.credentials.yaml`）；接入 WFClub 中转 `https://api.wfclub.fun/v1`（route `openai`，默认模型 `deepseek-ai/DeepSeek-V4.1-Flash`，显式添加 `input: [text, image]` 开启识图）
- **Antigravity**：AUR 包滞后需手动维护（本地 2.9.1，构建于 `~/tmp/antigravity-pkgbuild/`）；网络直连易超时，依赖 FlClash TUN 透明代理正常连通；CLI 为 `~/.local/bin/agy`
- **CodeBuddy IDE**：AUR 包 `codebuddy-ide-cn 4.12.0.37847260-1`，腾讯云代码助手独立桌面客户端，命令 `codebuddy-ide-cn`
- **WorkBuddy**：Electron 44 架构，`~/.workbuddy/app/gpu-crash-info.json` 软链接至 `/dev/null` 切断 GPU 降级死锁；`electron44-flags.conf` 配置 Ozone Wayland 原生 GPU 合成
- **OnlyOffice**：cachyos 官方源 `onlyoffice-bin`
- **Hyprland**：`hyprland 0.56.2-1` + `hyprexpo`（Super+Z 概览，Alt+Tab 窗口切换）；莫兰迪配色经 `write_hyprland` 注入
- **mark-shot**：AUR `mark-shot 0.1.49-1`（`/usr/bin/mark-shot`），快捷键 `Mod+Print`；系统 FFmpeg soname 升级时需重新源码构建

## 已弃用/已删除

- **Sunshine 串流服务**：`app-dev.lizardbyte.app.Sunshine.service` 已停止并禁用，释放端口与 GPU 编解码资源，全面由原生网易 UU 远程取代
- **PiDeck**：已完全卸载
- **COSMIC Desktop**：试用后已完全卸载清理
- **Denial**：Flutter + Rust Wayland 合成器，因 Impeller 渲染微卡顿与 CJK 候选生态不完善已清理
- **lpigui**：已弃用，由 pi-web 取代
- **Krita-MorandiTimeline**：已删除，备份于 `~/tmp/Krita-MorandiTimeline-backup-20260803.tar.gz`
- **Alacritty**：已全面弃用并由 Ghostty 替代
- **kde-material-you-colors**：用户单元已停止并禁用，unit 文件与遗留配置目录一并删除（备份 `~/tmp/disabled-units/`），KDE 配色统一由 `morandi-gen.py` 提供；日后若重装该 AUR 包需先确认不会与 morandi-gen 争抢同一批配色写入

## 踩坑速查

- **Steam 游戏掉帧三件套**：先 `nvidia-smi --query-compute-apps` 看游戏进程有没有图形上下文，再 `grep -c -i nvidia /proc/<pid>/maps` 判断到底跑在哪块 GPU（原生 Linux 移植版窗口类不是 `steam_app_*`，是 exe 名本身），`journalctl --user | grep xwayland-satellite` 能直接打出窗口类；最后核对 niri 全局规则有没有把游戏窗口圈进 blur（规则先匹配先生效，必须 `exclude`）。Proton/DXVK 会把 DISCRETE_GPU 排到最前，切 Proton 往往同时解决独显与中文（汉化补丁都只针对 Windows 的 `CookedPCConsole`）
- **第三方汉化补丁跑法**：用 `bwrap --unshare-net` 加独立 `WINEPREFIX` 关笼子，只 `--bind` 游戏目录其余全只读，汉化器多数会自动完成不需要点按钮；Steam「验证游戏文件完整性」是通用回滚手段，自动更新也会把汉化冲掉；手工 `--ro-bind` 把 exe 挂进游戏目录会在卸载后留下 0 字节同名文件，记得删
- **Wayland 合成器掉帧与鼠标卡顿排查**：先 `niri msg outputs` 确认刷新率与 VRR，再 `nvidia-smi` 看有没有不该出现的图形上下文（若面板挂在核显却有一堆…G 进程在独显即为全局 PRIME offload 作祟）；判据用「鼠标静止 vs `ydotool mousemove` 高频注入移动」两种状态下 niri 的 CPU 与 `/proc/<niri>/fdinfo/*` 里 `drm-engine-render` 的增量，移动时翻倍即帧预算已满；常见放大器是全屏透明 layer 面按固定间隔整屏重绘、全窗口 `blur true` 与 `opacity` < 1（两者都让窗口无法直出扫描）、跨 GPU 渲染（独显绘制 + 核显合成）；`libinput list-devices` 要 root，直接读 `/proc/bus/input/devices` 与 `/sys/bus/usb/devices/<dev>:1.0/ep_*/interval` 更快
- **网络（FlClash fake-ip 间歇性 TLS 失败）**：curl/git/gh 可用 `--resolve` 直连真实 IP（github.com=20.205.243.166, api.github.com=20.205.243.168, uploads.github.com=20.205.243.161）+ `http.version=HTTP/1.1`；AUR 遇到网络超时改下载 snapshot tarball 手动 makepkg；TUN 静默掉线时在 FlClash 界面开关一次网卡重启
- **提权**：pkexec 在 niri 下因 polkit 弹窗缺失卡死，需由用户在交互终端直接执行 sudo；`pkexec pacman -U` 必须使用绝对路径
- **Git**：`git tag -f` 重打注释 tag 必须带 `-m` 或 `-F` 防 vi 卡死；覆盖发布采用删远程 tag 重新 push 并重建 GitHub Release
- **adb 与多层 shell**：`su -c` 内嵌复杂变量与转义时写成本地脚本 push 后执行；抓取日志前必须 `logcat -c` 清除缓冲区防止历史日志干扰
- **Hindsight 残留处理**：`uvx daemon start` 异常退出会遗留孤儿进程锁定 `.cache/uv/.lock`，kill 后需手动删除 lock 文件
- **systemd 用户单元失控重启与沙箱内驱动**：默认 `StartLimitIntervalSec=10s` / `StartLimitBurst=5`，`RestartSec=3` 永远凑不满 5 次/10 秒，限流不会触发，坏单元会通宵重启，必须手动 `disable` 收口；DSH 的 bwrap 沙箱里 `systemctl --user` 连 `/run/user/1000/systemd/private` 会在 AUTHENTICATING 阶段报 ENODATA，改用 `busctl --user call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager <方法>`，`StopUnit` 签名 `ss`（单元名 + `replace`）、`DisableUnitFiles` 签名 `asb`、`ResetFailedUnit` 签名 `s`
- **Android 17 (SDK 37) 与 KernelSU-Next / Zygisk Next / Vector 保留 Root 更新要点**：
  - 1. **Root 镜像注入**：OTA 后若 LKM 签名不匹配或被 Seccomp 拦截，需从官方底包提取 `boot_a.img`，利用 `android12-5.10` KMI 与当前内核版本号注入 KernelSU-Next LKM 驱动与专属签名后 Fastboot 直刷
  - 2. **Zygisk Next 黑名单排查**：若应用无法加载模块，核对 `/data/adb/ksu/bin/znctl status` 中的 `enforce_denylist`，必须执行 `znctl enforce-denylist disabled`（置 0）以防应用被跳过注入
  - 3. **Vector 守护进程**：若 `cli status` 报 Socket Failure，检查 `service.sh` 中是否残留 toybox 不支持的 `unshare --propagation slave`，统一修正为 `unshare -m`
  - 4. **Xposed 模块兼容性**：旧模块若写死判断 `SDK_INT <= 36` 会抛出 NPE（如 Thanox），需停用或反编译 smali 将 SDK 版本识别限制在 36 并做判空保护；相机等 OEM 应用小版本更新可能会变更混淆字段名，需同步反编译更新 Hook 点
