# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 归档索引 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用/已删除 → 踩坑速查
维护约定：最近动态只留近一周与仍在进行中的条目，滚出窗口的整段原文搬进当年卷 `~/MEMORY-archive-<年份>.md`（分卷索引见 `~/MEMORY-archive.md`）

## 最近动态

- **Tailscale PC 侧掉线根因与自愈看门狗 (2026-11-17, 已完成)**:
  - 现象: 本机在控台显示 offline、控台同步失败，journal 里 `controlhttp: failed dialing` 约 195 次/小时且持续 2 小时不自愈，当天 12:36 与 15:18 各掉一次
  - 根因: `/etc/systemd/system/tailscaled.service.d/proxy.conf` 把 tailscaled 钉在 `127.0.0.1:7890`，而 Tailscale 受限 DNS 解析器拒绝 IP 字面量代理地址（`dnscache: unexpected hostname "127.0.0.1" doesn't match expected "controlplane.tailscale.com"`），DialPlan 拨号路径永远失败只剩回退路径，FlClash 换节点或重载配置切断长连接后即长期退避
  - 修复: `tailscale down && tailscale up`，operator 权限即可完成，重注册返回 `machineAuthorized=true` 不需重新登录，netmap 立刻恢复
  - `proxy.conf` 不能删: 直连实测 TCP 能握手但 TLS 被切断，属 GFW 特征，控制面与 DERP 必须走 7890 代理
  - 链路现状: 两端只能走 DERP 中继（K60→hkg、平板→nue），RTT 650-900ms，原因是 Clash TUN 代理了 tailscaled 的 UDP 使 P2P 打洞失败
  - 看门狗: `~/.local/bin/tailscale-watchdog.sh` + `tailscale-watchdog.service`（enabled），每 60s 判一次、连续 2 次命中才动手，动手前先验 7890 与 controlplane 可达，600s 冷却，`BackendState` 非 Running 一律不干预，空跑用 `TS_WATCHDOG_ONCE=1`
  - serve 现状: `:443 → 127.0.0.1:8787`、`:5000 → dufs(127.0.0.1:5000)`，访问用 `https://cachyos.tail1d48f3.ts.net:5000/`
  - **11-18 二次故障: 代理没开机自启 (已修)**: 10:26 重启后 FlClash 没起，tailscaled 全程 `proxyconnect ... connection refused`（225 次），控台连不上一直卡到 10:40 手动打开代理；根因是 `~/.local/share/com.follow.clash/shared_preferences.json` 里 `autoLaunch:false` 而 `autoRun:true`，已加 `~/.config/autostart/flclash.desktop`（systemd 的 xdg-autostart generator 已生成 `app-flclash@autostart.service`），开机自动拉起并自动连 TUN
  - **看门狗 v2（11-18 升级）**: 同类日志 600s 节流（原来 24 小时刷了 270 行）、自愈后改为每 5s 轮询最多 45s 才判定成败（原来只等 5s，17 号两次「自愈后仍失联」都是误报，实际两分钟内就恢复了）、代理不通与机场不可达时发桌面通知说明原因

- **DSH 与插件升级 (2026-11-17, 打包已完成、安装待执行)**:
  - `deepseek-harness-bin 0.2.2rc.1-1` 已审查 PKGBUILD 并构建打包（来源官方 npm `@deepseek-ai/dsh@0.2.2-rc.1`），归档于 `~/tmp/deepseek-harness-bin/` 与 `~/.cache/paru/clone/deepseek-harness-bin/`，**当前系统里装的仍是 0.2.0rc.2-1**，升级命令 `sudo pacman -U ~/.cache/paru/clone/deepseek-harness-bin/deepseek-harness-bin-0.2.2rc.1-1-x86_64.pkg.tar.zst`
  - 新装 `ds-harness-remote@0.6.5`（P2P/WebRTC 端到端加密远程接入），写入 `~/.dsh/profiles/web/package.json` 的 dependencies 与 bundles，移除旧 `dsh-remote`
  - 修复 `dsh-dream-skin` 切 npm 官方包 `^11.16.0`、`dsh-opencode-zen` 补 `cordis.patch.yml`、`dsh-better-sidebar` 升 0.31.1 并保留 0.2.0-rc.2 兼容豁免；同轮升级 modlens 3.27.5 / modsearch 5.10.14 / agy-link 0.6.29 / turn-fold 0.7.3 / pocket 2.13.1 / context 0.85.1 等
  - 清理 `cordis.patch.yml` 里 18 项废弃插件补丁，禁用未安装的 codex/cursor/acp 告警消除红色刷屏；`~/.local/bin/dsh` 包装脚本无参默认走 `web` profile，已入 chezmoi
  - 配置备份 `~/tmp/dsh-web-backup-20261117081034/`

- **完美主义打分器交付并线上化 (2026-11-12, 已交付)**:
  - 代码 `~/Projects/perfectionism-scorer`，零 npm 依赖无构建；完整 v2-v13 迭代细节、DO 钉死旧代码的坑、反引号 heredoc 事故都在 `~/MEMORY-archive.md` 同名条目
  - 大陆生产 `http://47.95.242.43:8890/`（阿里云，systemd 单元 `perfectionism-scorer`，运行用户 `scorer`，`THINK_SCALE=0.8`），Cloudflare 独立版 `https://scorer.lanrhyme.top/`，两套数据不互通，现场用大陆（e2e p50 582ms 对 CF 的 1131ms）
  - 现场放映走 `/present` 一页到底 14 页放映稿，空格翻页，揭底 15 步约 30 秒；`/admin` 揭底与导出、`/board` 大屏、`/ppt` 旧版
  - v13 压测: 大陆 80 并发 714 次提交 100% 成功（p95 663ms）、120 并发 1077 次成功（p95 658ms），CF 60 并发 534 次成功（p95 1062ms），双端数据均已清零
  - 这台机器上 `wrangler` 早就 OAuth 登录过（`~/.config/.wrangler/config/default.toml`），部署直接 `npx wrangler deploy`

- **K60 桌面拦截第三方 app 钉小组件 (2026-11-10, 处理中)**:
  - 真因是 OplusLauncher 自己的白名单不是权限: `AddItemActivity.isAllowedAddWidget()` 只放行系统应用、可卸载预装、持 `oplus.permission.OPLUS_COMPONENT_SAFE`、`WidgetControlHelper.isInWhiteList`，否则弹「请长按桌面后到卡片-插件添加」并 finish
  - 白名单来自 RUS 云配置 `app_nebula_fwk_widget_wl`，本机该 provider 不存在且 APK 里没有同名 asset → 白名单恒空；总开关 `FeatureOption.isSupportWhiteListControl()` 国内机型恒 true
  - 绕行方案按代价排序: LuckyTool 已启用的「移除组件添加请求白名单」/ 自写 LSPosed hook `WidgetControlHelper.isInWhiteList` 返回 true / 系统化到 `/system_ext/priv-app` 走 isSystemApp 分支（副作用是该 app 不能正常更新）
  - 排查备忘: 桌面布局在 `/data/user_de/0/com.android.launcher/databases/launcher.db` 的 `singledesktopitems_draw` 表（widget itemType=5、卡片 itemType=100），**没有 favorites 表**；中间产物在 `~/tmp/k60-launcher/`

### 归档索引

`~/MEMORY-archive.md` 是索引，条目原文按年份分卷存放（当前只有 `MEMORY-archive-2026.md`，93 条，2026-09-12 ~ 2026-11-12），最近一次整理 2026-11-17
- 2026-11（5 条）：打分器 v2-v13 完整迭代、QQNT 琉璃主题、Zen 拿不到代理、逃生汉化与星语猫娘桌宠
- 2026-10（85 条）：noctalia 5.4 切换与 v5 配置分层、polkit 缺失、Steam 大屏模糊、盖世小鸡手柄、影之刃零优化、鼠标卡顿 PRIME offload、10-26 平板通信共享掉线与 Tailscale 双端自愈、10-18~10-25 ReveriePaint-native 六项与 K60 ColorOS 16.1 脏刷、10-19~10-23 NyanoMuse 四十余项、10-18~10-19 nanoMuse 全端部署与 UU 远程被控端
- 2026-09（3 条）：设备刷机与备份、MicYou 迁移、Bettbox 切换、Dufs+Cloudflare、ReveriePaint v1.4.0

## 设备

### Redmi K60 (mondrian / ed3fdd92)
- 系统：ColorOS 16.1 / Android 16（ROM: ClearSkys 移植版，基底 OnePlus Ace 6，内核 5.10.246-AetherKernel），SukiSU Boot root
- 底层备份：位于 `~/刷机/k60/原厂备份/`（EFS/基带 `modemst1/2`、`fsg/fsc`，校准 `persist/persistbak`，`devinfo`，HyperOS 4 双槽位全套原厂镜像）
- 模块链：YABP、Zygisk Next (匿名内存模式，enforce-denylist 保持 0)、Vector (service.sh 修正为 unshare -m)、Tricky Store + TS Enhancer Extreme (内置 keybox)、HMA-OSS Zygisk、Material You for ColorOS、magic_mount_rs
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）、WeType-Kaomoji、WeTypeHook、couiexpressive、soulfrog
- 授权机制：轻量主板 ID 验证（本机 ID `0x0000043bfce1db8a`），授权凭据位于 `/mi_ext/product/etc/security/verificationlist.bin`（SHA-256 Token）；补丁包采用 Zip 伪加密，消除中心目录标志位后卡刷成功
- adb 要点：操作前核对 `dumpsys window mCurrentFocus`；用户使用手机时切勿抢占操作
- 远程接入链（root 守护，不走 Tailscale App）：二进制与状态在 `/data/adb/tailscale/`（`tailscaled --state=... --socket=... --tun=tailscale0 --netfilter-mode=off`），开机由 `/data/adb/service.d/tailscaled.sh` 拉起并自带 30s watchdog（uidrange 0-0 出口规则 + 控制面连续不可达自愈），`/data/adb/service.d/adbd-tcp.sh` 设 `service.adb.tcp.port=5555`，PC 侧 `~/.local/bin/adb-autoconnect.sh` 每 10s 自动 `adb connect`
- 血泪坑 (2026-11-10)：KernelSU 只执行 `/data/adb/service.d/` 下带 +x 的脚本，文件被重新落盘掉执行位后开机静默跳过（日志 `ksud::module: /data/adb/service.d/xxx.sh is not executable, skip`），表现为 tailnet 里 lastseen 停在数天前且 5555 不通；排查顺序 `logcat -d -b events | grep KernelSU` → `ls -la /data/adb/service.d/` → 修复 `chmod 755` 后手动 `sh /data/adb/service.d/tailscaled.sh`，平板侧同款脚本未掉位则照常运行

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
- 联网拓扑（关键）：Wi-Fi 版无蜂窝，日常靠手机的「通信共享」取网 —— 平板侧 `ovnet1 192.168.250.254/24` + `bt-vnet 192.168.199.1/24`，默认路由经 `bt-vnet` 链路本地网关指向手机（手机侧对应 `bt-vnet 192.168.199.2/24`）；共享链路一断平板立刻整机断网，表现为 tailnet 里先 `offline`（控制面 long-poll 超时）再彻底 ping 不通，而手机自身始终在线

### 盖世小鸡 启明星2 (GameSir Nova 2 Lite)
- 识别特征：VID `3537` (Zikway/GameSir)，接收器按手柄平台模式换身份 —— Xbox 平台 `045e:028e`(本机枚举失败)+ 备用 `3537:1098`，Switch 平台 `057E:2009`，PS4 平台 `054c:09cc` DualShock 4
- 组合键：【X+HOME】2.4G 接收器（绿灯）·【B+HOME】蓝牙（蓝灯）·【A+HOME】安卓（黄灯）· 长按 Home 5 秒关机 ·【Home+截图键】3 秒强制配对 ·【菜单键+视图键】切回绿灯
- 现状：**PS4 平台模式 + 2.4G 接收器** 为已验证可用配置（USB 呈现为 `054c:09cc`，hid-playstation 接管，`ps-controller-battery-*` 电量可读）；Xbox 平台模式下 dongle 的 `045e:028e` 身份在本机 xHCI 口上会枚举超时，无线不可用
- 官方文档：`https://doc.xiaoji.com/zh/n2lite/`（手柄）与 `https://doc.xiaoji.com/zh/n2litedongle/`（接收器）

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`，壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now；`/etc/greetd/config.toml` 的 default_session 为 `/usr/bin/noctalia-greeter-session`（user greeter），initial_session 为 `niri-session`
- 提权通道：`polkit-kde-agent` **至今未安装**（`pacman -Q` 为空），niri autostart 里 spawn 的 `/usr/lib/polkit-kde-authentication-agent-1` 因此不存在，`pkexec` 直接报 `Error creating textual authentication agent`；需要时装 `sudo pacman -S polkit-kde-agent`（依赖基本就位），在此之前提权只能由用户在交互终端执行 sudo，旧记录里的 `~/tmp/switch-greeter.sh` 已随 tmp 清理不复存在，greeter 仍是 `noctalia-greeter-git 1.0.0.r168` 未替换；`sshd` 常开可作远程兜底，`getty@tty2` 默认关闭
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（含 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku/write_hyprland/write_idea/write_antigravity_ide）；新应用主题化必须扩展此脚本，严禁直改应用配置；Wine 应用与 Krita 不走主题引擎
- Noctalia：官方源 `5.4.1-1.1`，运行期实际读写 `~/.local/state/noctalia/settings.toml`（chezmoi 托管），`~/.config/noctalia/settings.json` 是 v4 遗留、运行时不读；5.4 起调色板键名 `surface_variant`→`surface_container`、`outline`→`outline_variant` 但主题生成时新旧双写，`morandi-gen.py` 无需改；Luau 沙箱**不提供 `io` 库**，读文件用 `noctalia.readFile(path)`；重启顺序必须先 `pkill -P $(pgrep -x noctalia)` 清 runStream 子进程再杀主进程，否则复制通知会重复
- Niri：动画 stiffness 180-220 / damping-ratio 0.8 弹性轻柔滑行（cfg/animation.kdl）；窗口间距 8px（cfg/layout.kdl）；全局 opacity 0.98 + blur true（`draw-border-with-background false` 必设防聚焦实心边框）；全局规则排除 Krita/Loupe/Kando/SPlayer/cs2/gamescope/steam 与全部游戏窗口类（`steam_app_.*`、`pbz[.]exe`、`OLGame.*`、`.*[Oo]utlast.*`），**排除必须在全局规则里写 exclude，补专属规则不生效**；游戏专属规则给 `open-fullscreen true` + `variable-refresh-rate true` + 关模糊
- Ghostty：输入法修复依赖 wrapper `~/.local/bin/ghostty`（`env -u GTK_IM_MODULE` 解决不转发 key release 导致 fcitx5 状态机异常）；term_bg 公式 `max(l_b+0, 4)`；集成 Master GLSL 光标着色器与连字支持
- Fcitx5：bamboo-dark 皮肤（morandi-gen 注入），竖排候选，rime_ice（雾凇拼音）；支持 niri ext-background-effect 候选框模糊
- Fastfetch：write_fastfetch 全量生成 config.jsonc；源码中 ≥U+F0000 码点必须使用 8 位 `\U000FXXXX` 转义
- OBS：屏幕采集依赖 mesa EGL 核显渲染（强制覆盖 desktop Exec：`env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json obs`）；编码器使用核显 QSV（`obs_qsv11_v2`）；B 站推流插件位于 `~/.config/obs-studio/plugins/bilibili-stream-for-obs/`（含 PR #27 扫码登录补丁）
- Caelestia KDE Shell：KWin 6.7.4 + caelestia-shell 2.4.0 精简安装，配置位于 `~/.config/quickshell/caelestia/`，会话 `~/.local/bin/start-kwin-caelestia.sh`；缩略图依赖 PipeWire，nvidia.conf 严禁设全局 PRIME offload 变量防黑屏
- 显卡策略：默认全部走核显，严禁在 `environment.d/nvidia.conf` 或 niri `environment` 段设全局 PRIME offload（面板与合成器都在核显，全局强制独显会让每帧跨 GPU 拷贝并吃掉 144Hz 帧预算）；需要独显用 `prime-run` 前缀，桌面项覆盖见 `~/.local/share/applications/` 下的 blender / org.kde.krita / DaVinciResolve / com.lunarclient.LunarClient
- Zen 浏览器 (Flatpak)：已用 `flatpak override --user --unset-env` 去掉三个 NVIDIA 变量改走 Mesa 核显；user.js 仍启用 `layers.dmabuf.disable=true` 防止 2D canvas 合成失效；D-Bus portal 授权只读访问 fcitx5 目录；**代理必须写死在 user.js（手动 127.0.0.1:7890）**，沙箱内没有 dconf 模块，系统代理对它有等于无
- SPlayer-Next：AUR `splayer-next-bin`，二进制 `/opt/SPlayer-Next/SPlayer-Next`，命令 `/usr/bin/splayer-next`
- slugcatpet 桌宠：`~/Projects/slugcatpet`，GTK3 窗口必须设为 Layer.TOP；GTK3 桥按 Qt 侧 `_dirty_rect` 算好的脏矩形做 `queue_draw_area` 局部重绘，禁止退回每帧整屏 `queue_draw`（全屏透明面整屏重绘会把合成器整屏混合负载拉满）

## 项目

### perfectionism-scorer 打分器 — `~/Projects/perfectionism-scorer`
- 心理汇报《完美主义》开场游戏：扫码后 120 秒内反复改一句话拿分，结尾揭穿「分数有刻度，只是它量错了东西」
- 零依赖 Node 服务（无 npm 依赖无构建）+ SSE 实时推送 + 每 400ms 原子写 `data/state.json`；状态机抽在 `lib/game.mjs` 纯函数，Node 与 Durable Object 共用一份
- 分数模型：基准 72..88（单次可掉 4 涨 3）+ 个人偏移 ±3 + 内容项 0/2/5 → 全场 69..96；内容项只认字数/标点种类/分句数；同句同分靠「文本 FNV 哈希 → 分数」memo，否则改回旧版本分数会变、两次就被试穿
- 二维码 `lib/qr.mjs` 自研（v1-10 字节模式、掩码按惩罚分择优），`npm run check:qr` 用 zbarimg 验证
- 路由：`/`→play、`/board` 大屏、`/admin` 揭底与 CSV 导出、`/present` 放映稿、`/ppt` 旧版
- 工具：`tools/seed.mjs` 造数、`tools/stress.mjs` 压测、`tools/shot.mjs` CDP 截图（复用 playwright 缓存里的 chromium，服务与截图必须在同一次 bash 调用里起）

### MoClock 墨钟 — `~/Projects/MoClock`
- Material 3 风格安卓桌面时钟小部件（Compose 主界面 + Jetpack Glance 小部件，包名 `io.github.lanrhyme.moclock`），5 种版式（数字/表盘/文字/双城/日历）+ 30 余项配置 + 7 套预设
- 工具链：AGP 8.7.3 / Gradle 8.11.1 / Kotlin 2.1.0 / Compose BOM 2024.12.01 / Glance 1.1.1，compileSdk 35、minSdk 26；依赖解析需阿里云镜像兜底（mavenCentral 的 repo1 会 403）
- 配置双写：DataStore `moclock_settings`（app 内列表用）+ Glance Preferences 状态（小部件渲染真实来源，写入即触发重组，顺带解决时间不刷新）；state 里 cfg/dark/dynamic/seed/tick 五键
- 排版纯函数在 `design/`（Metrics 尺寸、ClockText 文案、Palette 取色、AnalogFace 画表盘、MonthGrid），Glance 渲染器与 Compose 预览共用同一份，保证预览≈桌面
- Glance 1 没有 rotate/Canvas：表盘用 android.graphics 画成 Bitmap 再交给 `Image(ImageProvider(bitmap))`
- 刷新：AlarmManager 整分对齐，开秒且亮屏时 1s 一次，息屏降回整分；TIME_SET/TIMEZONE/DATE/BOOT/MY_PACKAGE_REPLACED 均重排
- 构建：`./gradlew :app:assembleDebug`（release 走 R8，2.1MB）；验证机 emulator-5554 与平板 100.107.36.2:5555
- **视觉口径**：Pixel 排版——大数字 sans-serif-light、冒号与数字同色、日期紧跟时间下方（`dateSize=0.26*timeSize` clamp 12–18）、内边距 18dp、时间上限 96dp；表盘为 `DialStyle.PIXEL` 素盘（12 短刻度 alpha195 + 圆头锥形指针 + 中心双点），默认关秒针
- 装机：K60 `100.127.72.106:5555` 已装 release APK（versionName 0.1.0）；注意 Tailscale 上 `adb install` 会卡死（stream install 挂住），可靠做法是 `adb push` 到 /data/local/tmp 再 `pm install -r`，`adb kill-server` 后需要 `adb connect` 重连
- **未完成验证**：桌面侧无法自动化加小部件（Pixel Launcher 上 `requestPinAppWidget` 返回 false，根因见最近动态的 OplusLauncher 白名单条目），真实 Glance 渲染尚未在真机确认；`app/src/debug` 里有 `DebugHostActivity` 可用 AppWidgetHost 直连渲染，需先拿到 BIND_APPWIDGET
- 副作用记录：曾为跑截图用 `emulator -avd Medium_Phone_API_36.1 -wipe-data`，该 AVD 原有数据已被清空

### MiuiCamera-Fix — `~/Projects/MiuiCamera-Fix`
- 小米澎湃OS移植包相机机型与版本校验不匹配强退修复 Xposed 模块（Java + Xposed API 82，目标包 `com.android.camera`，测试机 ed3fdd92）
- 包名：`io.github.lanrhyme.camerafix`
- 机制：Hook `G6.c.w()` 返回 `false`，Hook `G6.e.g()` 修正 `f2302a = Boolean.FALSE`，Hook `ActivityBase` Handler 丢弃 Message 11 退出消息
- 仓库：`https://github.com/LanRhyme/MiuiCamera-Fix`（Release Tag `v1.0.0`）
- 构建：`./gradlew assembleRelease` + `adb install -r app/build/outputs/apk/release/app-release.apk`

### WeType-Kaomoji — `~/Projects/WeType-Kaomoji`
- 微信键盘表情面板颜文字注入与分类增强 Xposed 模块（Kotlin + LibXposed API 102，目标包 `com.tencent.wetype` 3.5.3，测试机 ed3fdd92）
- 包名：`io.github.lanrhyme.wetypekaomoji`
- 机制：`w.C` 注入分列数据，`a1.b0`/`a1.a0` 移除推荐表情并将颜文字置首；`x.getItemViewType` 隔离独立复用池类型 88；`ImeEmojiBoardView` 注入胶囊分类栏；内置 250+ 萌系颜文字
- 仓库：`https://github.com/LanRhyme/WeType-Kaomoji` 与官方模块源 `Xposed-Modules-Repo/io.github.lanrhyme.wetypekaomoji`（Release Tag `1-1.0.0`）
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
- 崩溃诊断引擎：接入 ReverieCrashHandler (C++) 信号安全拦截器与 128KB 独立信号备用栈，捕获 48 帧 Native 符号栈与寄存器状态；Java 层集成 Thread.UncaughtExceptionHandler；双端搭载容量 25 条的 Breadcrumbs 环形操作轨迹；启动阶段弹出 Morandi 诊断弹窗
- 构建：`scripts/build_native.sh`（QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a，纯 Kotlin 改动直接 assembleDebug）

### Horizon — `~/Projects/Horizon`
- 现代化 Android 平板浏览器（GeckoView + Mozilla Android Components + Rust Firefox Sync，前台 Jetpack Compose，针对一加平板 2 Pro 定制）
- 应用名 `Horizon`，包名 `top.lanrhyme.horizon`
- 架构特色：Zen / Arc 风格三态可折叠侧边栏、多工作区（Spaces）、同屏双开分屏（Split View）、WebExtensions 插件生态、全量 Firefox 跨端同步、Morandi 与 Material You 双轨动态色彩

### Krita 插件套件
- 源码位于 `~/.local/share/krita/pykrita/`（FolioLayers v1.2.1、AdvancedColorPicker v1.1.0、SimpleHSVSliders v1.0.1、MorandiUI、InfiniteCanvas v1.0.0、GmicFilters）
- 关键规范：打包 zip 根目录必须含 `<name>.desktop`（`ServiceTypes=Krita/PythonPlugin` 且 `X-Python-2-Compatible=false`）；Docker 必须继承 KisMainWindow 的 DockWidget；G'MIC 面板滤镜参数必须带显式参数并用 `-o[0]` 指定输出

### 其他项目
- **threejs-dragon-flight**：`~/Projects/Tests/threejs-dragon-flight`，3D 巨龙空域自由翱翔飞行模拟器，Three.js + 骨骼动画 + 云海粒子与音效
- **threejs-pistol-disassembly**：`~/Projects/Tests/threejs-pistol-disassembly`，3D 手枪机械结构拆解与精密爆炸图交互系统
- **voxel-jrpg-village**：`~/Projects/Tests/voxel-jrpg-village`，日式幻想体素村落 JRPG 网页，Three.js + Web Audio 程序化和弦合成
- **Pi Codex GUI**：`~/Project/pi-codex-gui`，Tauri 2 + bridge.js（RPC 模式下事件转发格式必须为 `{ ...ev, type: 'ui_request' }`）
- **bilibili-pixel-danmaku**：`~/Projects/bilibili-pixel-danmaku`，PySide6 弹幕助手，莫兰迪配色经 morandi_colors.json 热更新，启动项由 chezmoi 托管
- **Pi Agent TUI**：`~/.pi/agent`，zentui/open-tui 扩展，morandi-gen 的 write_pi 同步配色
- **Krita-MobileUI**：`~/Projects/Krita-MobileUI`（暂停中）

## 安装与服务

- **Tailscale (PC)**：`tailscale 1.104.5-1.1`，系统服务 `tailscaled`（drop-in `proxy.conf` 强制走 7890 代理，不可删）；`OperatorUser=lanrhyme`，常规操作免 root；自愈看门狗 `tailscale-watchdog.service`（enabled）；出网依赖 FlClash，已配 `~/.config/autostart/flclash.desktop` 开机自启；serve 配置见最近动态
- **nanoMuse**：v1.0.5 跨设备 Agent；桌面端 AppImage 部署于 `~/.local/opt/nanomuse/nanoMuse.AppImage`，CLI 链接 `~/.local/bin/nanomuse`，桌面项 `nanomuse.desktop`；手机与平板端均通过 ADB 部署 `io.github.nanomuse.app` 并注入电池优化白名单
- **网易 UU 远程被控端 (uu-remote-linux)**：社区原生 Rust 被控端（`/usr/bin/uuremote-server`，集成 `--features wayland,portal`）；用户服务 `uu-remote-native.service`（自启常驻，支持 Wayland 活跃 Socket 自动探测与重载自愈）；依赖 `/dev/uinput` 与 `xdg-desktop-portal`；凭据在 `~/.config/uuremote/config.json`
- **Antigravity 星语猫娘桌宠**：插件位于 `~/.gemini/config/plugins/star-pet/`（main.mjs 编排 + layer.mjs Shadow DOM 图层），控制入口 `~/.local/bin/star-pet status|on|off|scale|state|log`，改的是插件数据目录的 `settings.json`（sidecar 每 2 秒重读）；皮肤只铺当前壁纸不覆盖主题变量，遮罩取宿主 `var(--background)` 默认 0.4；宿主重拉 sidecar 约 45 秒，识别新代码看 `pet.log` 里是否有新的 `injected layer`
- **QQNT 琉璃主题**：启动链 `~/.local/share/applications/qq.desktop` → `~/.local/bin/linuxqq`（bwrap 免 root 覆盖 /opt）→ `/usr/bin/linuxqq`；LiteLoaderQQNT 1.4.1 在 `~/.local/share/LiteLoaderQQNT`，主题插件 `plugins/liuli-dsh-theme`；QQ 升级或补丁丢失后跑 `~/.local/bin/qqnt-liteli-setup` 重建（幂等），回滚删 qq.desktop 即可
- **Bettbox & FlClash**：AUR 包 `bettbox-bin 1.19.3-1` 与 `flclash-bin 0.8.93-1`；数据位于 `~/.local/share/com.appshub.bettbox/` 与 `~/.local/share/com.follow.clash/`；两者 mixed-port 都定到 7890，谁先起谁占；BettboxCore 内置 SUID root 免密启动 TUN
- **Xiaomi MiMo Desktop**：AUR 包 `mimo-desktop 26.909.91205-2`；官方包漏打 `node-machine-id` 导致登录缺 `deviceId`，已在 PKGBUILD 里补丁改读 `/etc/machine-id` 修复 `app.asar`
- **Dufs (WebDAV) & Cloudflare Tunnel**：AUR 包 `dufs-bin 0.46.0-2`；数据根目录 `~/WebDAV`（含 `reader/`、`backup/`）；监听 `127.0.0.1:5000`（全私有 Basic 认证，用户 `lanrhyme`，绑定必须留在 loopback 否则会抢 tailscale serve 的 5000）；配置 `~/.config/dufs/config.yaml`（权限 600）；搭配 `cloudflared-webdav.service` 绑定 `https://webdav.lanrhyme.top/`；systemd user 服务常驻自启（开启 linger）
- **MicYou**：本地包 `micyou 2.0.0.alpha.1-1`；Noctalia 插件开源于 `lanrhyme/micyou`；手机端安装于 K60；ufw 放行 8554/tcp、8555/udp、8443/tcp、5353/udp
- **企业微信**：deepin Wine 版 `com.qq.weixin.work.deepin`，容器位于 `~/.deepinwine/Deepin-WXWork`，启动脚本 `/opt/apps/com.qq.weixin.work.deepin/files/run.sh`
- **Waydroid**：Android 16 (LineageOS 23.2)，开启 Intel iGPU/GBM 加速；依赖 UFW 规则 `sudo ufw allow in on waydroid0`；脚本位于 `~/tmp/a16/`
- **DeepSeek Harness**：已装 `deepseek-harness-bin 0.2.0rc.2-1`（`/usr/bin/dsh`），`0.2.2rc.1` 已打包待装；Superpower 预设位于 `~/.dsh/.agent-presets/superpower/`；LLM 路由在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers`（密钥只存 `~/.dsh/.credentials.yaml`）；接入 WFClub 中转 `https://api.wfclub.fun/v1`（route `openai`，默认模型 `deepseek-ai/DeepSeek-V4.1-Flash`，须显式加 `input: [text, image]` 才开识图）
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

- **Tailscale 卡死不可自愈**：开机后就掉线先 `nc -z 127.0.0.1 7890` 查代理在不在（FlClash 自启已配，但代理本身没连上时 tailscaled 完全出不去，日志为 `proxyconnect ... connection refused`）；确认代理正常后判据是本机在 `tailscale status` 里显示 offline 且 `journalctl -u tailscaled` 里 `controlhttp: failed dialing` 持续出现（≥6 次/3 分钟），处理一律 `tailscale down && tailscale up`（operator 权限即可，不需要 root）；不要因此删 `proxy.conf`，直连 TLS 是被切断的；根因是 Tailscale 受限 DNS 解析器拒绝 IP 字面量代理地址
- **布尔判定的 jq 陷阱**：`jq '.X // true'` 在 `.X` 为 `false` 时会返回 `true`（`//` 把 false 当空值），判布尔一律直接取 `.X` 再与字符串 `"false"` 比较
- **Steam 游戏掉帧三件套**：先 `nvidia-smi --query-compute-apps` 看游戏进程有没有图形上下文，再 `grep -c -i nvidia /proc/<pid>/maps` 判断到底跑在哪块 GPU（原生 Linux 移植版窗口类不是 `steam_app_*`，是 exe 名本身），`journalctl --user | grep xwayland-satellite` 能直接打出窗口类；最后核对 niri 全局规则有没有把游戏窗口圈进 blur（规则先匹配先生效，必须 `exclude`），Proton/DXVK 会把 DISCRETE_GPU 排到最前，切 Proton 往往同时解决独显与中文
- **第三方汉化补丁跑法**：用 `bwrap --unshare-net` 加独立 `WINEPREFIX` 关笼子，只 bind 游戏目录其余全只读，汉化器多数会自动完成；Steam「验证游戏文件完整性」是通用回滚手段，自动更新也会把汉化冲掉；手工把 exe 挂进游戏目录会在卸载后留下 0 字节同名文件
- **Wayland 合成器掉帧与鼠标卡顿排查**：先 `niri msg outputs` 确认刷新率与 VRR，再 `nvidia-smi` 看有没有不该出现的图形上下文；判据用「鼠标静止 vs `ydotool mousemove` 高频注入移动」两种状态下 niri 的 CPU 与 `/proc/<niri>/fdinfo/*` 里 `drm-engine-render` 的增量，移动时翻倍即帧预算已满；常见放大器是全屏透明 layer 面按固定间隔整屏重绘、全窗口 `blur true` 与 `opacity` < 1
- **网络（FlClash fake-ip 间歇性 TLS 失败）**：curl/git/gh 可用 `--resolve` 直连真实 IP（github.com=20.205.243.166, api.github.com=20.205.243.168, uploads.github.com=20.205.243.161）+ `http.version=HTTP/1.1`；AUR 遇网络超时改下载 snapshot tarball 手动 makepkg；TUN 静默掉线时在 FlClash 界面开关一次网卡重启
- **提权**：pkexec 在 niri 下因 polkit 弹窗缺失卡死（polkit-kde-agent 未装），需由用户在交互终端直接执行 sudo；`pkexec pacman -U` 必须使用绝对路径
- **Git**：`git tag -f` 重打注释 tag 必须带 `-m` 或 `-F` 防 vi 卡死；覆盖发布采用删远程 tag 重新 push 并重建 GitHub Release
- **adb 与多层 shell**：`su -c` 内嵌复杂变量与转义时写成本地脚本 push 后执行；抓取日志前必须 `logcat -c` 清除缓冲区防历史日志干扰
- **Hindsight 残留处理**：`uvx daemon start` 异常退出会遗留孤儿进程锁定 `.cache/uv/.lock`，kill 后需手动删 lock 文件
- **systemd 用户单元失控重启与沙箱内驱动**：默认 `StartLimitIntervalSec=10s` / `StartLimitBurst=5`，`RestartSec=3` 永远凑不满 5 次/10 秒，限流不会触发，坏单元会通宵重启，必须手动 `disable` 收口；DSH 的 bwrap 沙箱里 `systemctl --user` 连 `/run/user/1000/systemd/private` 会在 AUTHENTICATING 阶段报 ENODATA，改用 `busctl --user call`，`StopUnit` 签名 `ss`、`DisableUnitFiles` 签名 `asb`、`ResetFailedUnit` 签名 `s`；需要真正联动用户单元时申请 danger-full-access 跑 `systemctl --user`
- **Android 17 (SDK 37) 与 KernelSU-Next / Zygisk Next / Vector 保留 Root 更新要点**：
  - 1. **Root 镜像注入**：OTA 后若 LKM 签名不匹配或被 Seccomp 拦截，需从官方底包提取 `boot_a.img`，利用 `android12-5.10` KMI 与当前内核版本号注入 KernelSU-Next LKM 驱动与专属签名后 Fastboot 直刷
  - 2. **Zygisk Next 黑名单排查**：若应用无法加载模块，核对 `/data/adb/ksu/bin/znctl status` 中的 `enforce_denylist`，必须执行 `znctl enforce-denylist disabled`（置 0）防跳过注入
  - 3. **Vector 守护进程**：若 `cli status` 报 Socket Failure，检查 `service.sh` 中是否残留 toybox 不支持的 `unshare --propagation slave`，统一修正为 `unshare -m`
  - 4. **Xposed 模块兼容性**：旧模块若写死 `SDK_INT <= 36` 会抛 NPE（如 Thanox），需停用或改 smali 限制在 36 并做判空保护；相机等 OEM 应用小版本更新可能变更混淆字段名，需同步反编译更新 Hook 点
