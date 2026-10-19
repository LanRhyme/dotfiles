# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **NyanoMuse (Fork 自 nanoMuse) 独立项目创立、Cloud Relay 自建与 Android Root 解除沙箱架构 (2026-10-19, 全端就绪)**:
  - 架构与仓库：针对官方 nanoMuse 云端同步简陋与移动端强制隔离在 Alpine PRoot 沙箱内的痛点，Fork 官方仓库至 `LanRhyme/NyanoMuse` 并本地克隆至 `~/Projects/NyanoMuse`
  - 自建中继服务：基于 Python 虚拟环境与 uv 部署 `~/Projects/NyanoMuse/cloud`，编写 systemd 用户服务 `nyanomuse-cloud.service`（自启常驻），服务监听 `127.0.0.1:8787`；代码级支持 `REVIEW_ADDRESSES=*` 通配免验证码模式，任何邮箱配合专属通行码 `123456` 秒登
  - 公网与隧道穿透：在 `~/.cloudflared/config.yml` 配置 ingress 路由将 `nyanomuse.lanrhyme.top` 转发至 `http://127.0.0.1:8787`；将 tunnel 协议修正为 `quic` 解决 Clash 伪 IP 环境下的 TLS 握手异常；Cloudflare CNAME 自动解析绑定成功
  - 资料固化：初始化新账号并将黑猫 5 状态手绘立绘与资料写入新中继（Rev 1），电脑端 `cordis.patch.yml` 已指向新中继地址
  - Android Root 与沙箱解除：
    - 三档执行模式：新增 `ExecutionMode`（`ROOT`、`HOST_SHELL`、`PROOT_SANDBOX`），默认启用 `ROOT`；`PersistentShell` 根据模式自动直启 `/system/bin/su` 或 `/system/bin/sh`；非沙箱模式直接挂载 `/storage/emulated/0` 且不启动 PRoot 内核
    - 全系统文件读写直通：重构 `PRootKernel` 路径解析，直通真实 Android 宿主路径；`FileReadTool`、`FileWriteTool`、`FileEditTool` 统一增加 Root 模式容错直通（普通 I/O 权限不足时无缝无感回退至 `su` 读写）
    - 智能安全门控降噪：重构 `ShellGuard` 与 `RiskGate`，在 Root 模式下豁免 `reboot`、`shutdown`、`pm`、`am`、`dumpsys`、`iptables`、`setprop` 等系统运维指令，仅严格拦截全盘格式化与块设备直接覆写等毁灭级风险操作
    - 动态 Prompt 与设置界面：`AgentTools` 与 `SoulStore` 根据当前模式动态调整身份宣称与 `shell_execute` 描述；在设置页新增「终端执行环境与权限」配置弹窗，支持可视化无缝切换模式
    - 编译与测试：生成符合 gomobile 约定的 `rclone.aar` 依赖存根；修复 Gradle 镜像源兼容性；Android 全量 Kotlin 源码编译通过且全部单元测试 100% 绿色通过，改动已推送至 GitHub
  - 待办：手机与平板端安装打包 APK 并登录至自建服务；在 NyanoMuse 源码中开发 `SOUL.md` 与 `rooms.json` 的真正多端云端漫游扩展

- **nanoMuse 跨设备 AI Agent 全端部署、Niri 静默自启与黑猫灵魂/AGENTS.md 双轨联动 (2026-10-18, 完成)**:
  - 架构：开源跨设备自主 Agent（v1.0.5）；手机端（K60）与平板端（一加平板 2 Pro）均安装 `io.github.nanomuse.app` 并配置电池白名单，电脑端安装 AppImage 至 `~/.local/opt/nanomuse/nanoMuse.AppImage` 并创建 CLI 链接 `~/.local/bin/nanomuse`
  - 桌面与自启：提取官方图标生成 `nanomuse.desktop`；配置 `~/.nanomuse/desktop/desktop.json` 启用常驻托盘；在 Niri `autostart.kdl` 添加自启并在 `rules.kdl` 配置规则隔离至后台工作区 `bg` 且不抢占焦点，变更已纳入 Chezmoi
  - 自定义立绘与云端固化：生成全套 5 状态黑猫立绘，调用 `PUT /v1/me/profile` 固化至云端账号（Rev 11 / `4c82dd34732c`），三端完全继承
  - 角色灵魂与 AGENTS.md 链接：排查定位此前 AGENTS.md 中写死「对话回复保持简洁直接和专业」导致模型压制猫猫人设；重构 AGENTS.md 第 4 节确立双轨制（日常助手交流全面放开软萌撒娇小黑猫性格、称呼老大、穿插动作拟声与萌系颜文字；工程执行严守安全红线与格式约束）；变更已提交 Chezmoi 并同步推送至平板
  - 状态：手机与平板均已静默部署；电脑端后台常驻与多端灵魂守则就绪

- **网易 UU 远程 Linux 被控端部署、Wayland 适配、输入法防吞字与黑屏自愈 (2026-10-18, 优化完成)**:
  - 架构与安装：AUR `uu-remote-bin` 基础环境；拉取官方源码 (v0.1.22) 启用 `--features wayland,portal` 编译部署于 `/usr/bin/uuremote-server`，解决官方预编译包不支持 Wayland 桌面串流问题
  - 权限与输入：部署 `/usr/lib/udev/rules.d/60-uu-remote-linux-uinput.rules` 赋予 `/dev/uinput` 用户级访问权限，内核级注入虚拟键鼠，绕过 Wayland 输入隔离限制
  - 移动端输入法吞字与回弹根治（混合输入终极方案）：排查定位手机端连续发词切分过碎导致剪贴板覆盖踩踏与冲突吞字；重构 CONTROL_DATA_CHANNEL 落地混合输入：1. 单字符（a-z、A-Z、0-9、空格、换行、Tab、退格）走 uinput 物理硬件扫描码直发，毫秒级即时上屏完全不经剪贴板；2. 复合/中文文本引入 45ms 滑动防抖合并，在写入前快照备份剪贴板，粘贴完成 100ms 后静默还原旧剪贴板，实现本地剪贴板历史零污染；配合 30ms selection 缓冲、30ms/40ms/25ms 稳健组合键注入与 40ms 冷却保护，杜绝连续输入踩踏；彻底剥离监听回调中的 6 处被动 Ctrl+V 注入，支持通过 niri 识别终端切为 Ctrl+Shift+V，并把回弹屏蔽窗口扩充至 5000ms
  - 串流画质与局域网直连：码率基准提升至 `UU_VIDEO_BITRATE=8000k`、峰值 `UU_VIDEO_MAX_KBPS=12000`、缓冲区 `UU_VIDEO_BUFSIZE=12000k`，解除 VBV 限制并在 3K 屏幕下画质提升 3 倍；UFW 放行局域网网段并过滤 Clash TUN 伪 IP（`198.18.0.1`），恢复 WebRTC P2P 低延迟直连
  - 远控活跃状态与 Noctalia 剪贴板防骚扰：在 `uuremote-server` 的 WebRTC desktop 会话生命周期中维护 `/tmp/uu_remote_active` 状态文件；在 Noctalia `clipboard-osd` 插件（`main.luau`）的 shell 触发条件与事件处理双层注入判断，远控期间全静音避免手机打字与快照恢复频繁触发复制桌面弹窗，远控结束后自动恢复正常通知
  - 开机自启常驻连入黑屏自愈：排查定位开启 linger 时服务随 `default.target` 较早启动，此时桌面尚未建立且缺乏 `WAYLAND_DISPLAY`（受原配置写死 `DISPLAY=:0` 误导），导致底层初始化为 X11 后端从 `:0` 抓取 Xwayland 空白根窗口（表现为仅显示客户端自绘光标而画面全黑），且登录桌面后原有进程无法感知后端变更；修复方案：1. 在 `desktop_backend.rs` 新增 `ensure_wayland_env` 自动扫描探测 `/run/user/<uid>/wayland-*` 活跃可连通 Socket 并动态补齐环境；2. 在 `main.rs` 的 Offer 接入流中增加后端变更自愈检测，一旦检测到 Wayland 就绪或与启动时绑定的后端不一致，立即重载重建 `ScreenCapture::new()`；3. 优化 `/usr/lib/systemd/user/uu-remote-native.service` 移除硬编码 `DISPLAY=:0` 并透传 Wayland 变量
  - 游戏按键映射与触控轮盘修复：逆向兼容 mobile 客户端下发的 input_keys 对象数组、内联 JSON 字符串及逗号分隔格式，将 keyboard 与 mouse 设备精准分发至虚拟按键与鼠标点击
  - 凭据与常驻：登录凭据存储于 `~/.config/uuremote/config.json`；启用 systemd 用户服务 `uu-remote-native.service` 实现开机自动登录并常驻连接网易远控网络

- **CodeBuddy IDE (腾讯云代码助手) 独立桌面端安装 (2026-10-18, 安装完成)**:
  - 架构与安装：通过 PKGBUILD 安全审查后从 AUR 安装 `codebuddy-ide-cn 4.12.0.37847260-1`，解包腾讯官方 DEB 并完成针对 Electron 37 缺失原生模块（node-pty、policy-watcher 等）的本地重编
  - 可执行程序与桌面图标：生成 `/usr/bin/codebuddy-ide-cn` 与 `/usr/share/applications/codebuddy-ide-cn.desktop`

- **DeepSeek Harness (DSH) 升级与全量插件更新 (2026-10-18, 完成)**:
  - 核心架构升级：AUR `deepseek-harness-bin` 升级至 `0.2.0rc.2-1`（dsh 0.2.0-rc.2），通过 PKGBUILD 安全审查
  - 插件全量升级：运行 `dsh plugin --profile web update --latest`，全量更新全部 18 个扩展插件至最新兼容版本
  - 兼容豁免与修复：针对 `dsh-opencode-zen` 授权版本兼容豁免（`allow-version`），补齐缺失的 patch 文件消除加载告警
  - 插件 Hub 同步：本地 `~/dsh-plugin-hub` 仓库快进拉取上游最新提交
  - 统计插件与代理报错修复：`dsh-token-usage-counter` 因 DSH 0.2 移除 `ctx.settings.register` 报错，更新至最新 GitHub 上游（v0.5.0，适配 `storageDomain` 持久化）；编写 `~/.local/bin/dsh` 启动包装脚本，自动过滤 SOCKS 协议的 `all_proxy` 避免启动告警，同时保留 HTTP 代理生效


- **WorkBuddy 前端卡顿根治与 Wayland 硬件加速解锁 (2026-10-18, 优化完成)**:
  - 根因定位：WorkBuddy 内置 GPU 降级保护机制，当检测到 `gpu-crash-info.json` 中崩溃计数 ≥1 时自动禁用硬件加速；在 Linux Wayland 下正常退出时 GPU 子进程被主进程杀死（SIGTERM），因非 clean-exit 误判为 GPU 崩溃并累加计数，导致应用永久陷入 CPU 软件栅格化与前端极度卡顿
  - 死锁切断：将 `~/.workbuddy/app/gpu-crash-info.json` 软链接至 `/dev/null`，使得配置读取永远返回 `{}`（不触发降级门控），写崩溃计数直接吸收入黑洞
  - 硬件加速配置：在 `~/.config/electron44-flags.conf` 配置 Wayland 原生 GPU 合成参数（`--enable-features=UseOzonePlatform,WaylandWindowDecorations`、`--ozone-platform=wayland`、`--enable-gpu-rasterization`、`--enable-zero-copy`、`--ignore-gpu-blocklist`），并纳入 Chezmoi 仓库管理

- **IntelliJ IDEA 莫兰迪配色与主题引擎集成 (2026-10-15, 配置完成)**:
  - 主题架构：在 `~/.config/noctalia/morandi-gen.py` 扩展 `write_idea(palette)`，生成独立的编辑器配色方案（`Morandi.icls`）与配套 UI 主题插件包（`morandi-theme.jar`）并在 `main()` 接入自动重载
  - 本地化配置：部署解除版本限制的官方中文语言包至 `~/.local/share/JetBrains/IdeaIC2026.2/zh/lib/zh.jar`，在 `ide.general.xml` 与 `idea64.vmoptions` 写入语言环境配置

- **ReveriePaint v1.4.0 版本发布与全量架构升级 (2026-10-02, 发布完成)**:
  - 版本号与构建体系：版本号自 1.3.10 (27) 升级至 1.4.0 (28)，打标签 `v1.4.0` 并推送至 GitHub 触发 Release 打包工作流
  - 核心功能升级集成：集成快捷笔刷悬浮面板、快捷操作悬浮面板、防崩溃快照恢复系统、Procreate 风格动态流动斑马纹选区与黑白相间矢量流动蚂蚁线系统、界面动效速度设置三档调节、边缘侧滑返回手势与起笔防误画优化
  - 核心崩溃与视觉修复：修复多步撤销 Swap 溢出崩溃（软限制调至 50% 与 maxSwapSize 8GB）、移除引发原生 Abort 的 MotionPredictor 回退调用；利用 ARM NEON 矢量加速直通 BGRA 预乘透明度并修复变换预览与缩略图过曝泛光；修复边缘侧滑手势排除与图层重命名冲突

- **MicYou 主仓库迁移至 MicYou-Dev 组织 (2026-10-01, 迁移完成)**:
  - 迁移目标：由 `LanRhyme/MicYou` 完整迁移至官方组织 `MicYou-Dev/MicYou`，保留应用包名及 Bundle Identifier `com.lanrhyme.micyou`，批量更新 Issue 模板、文档与客户端接口地址，更新本地 Git remote 并推送

- **代理客户端切换为 Bettbox (2026-10-01, 双客户端共存过渡)**:
  - 架构：安装 AUR `bettbox-bin 1.19.3-1`（Flutter + Mihomo 内核），迁移 profiles、数据库与 GEO 规则库；内核 `BettboxCore` 具 SUID root 支持免密 TUN；调整配置关闭开机自连避免与运行中的 FlClash 冲突，供前端平滑切换

- **Redmi K60 (mondrian) 底层完整备份与 ColorOS 16.1 全量刷入 (2026-09-14 ~ 2026-09-25, 成功)**:
  - 底层备份：提取基带校准（`modemst1/2`、`fsg/fsc`）、硬件校准（`persist`）、设备信息（`devinfo`）及原厂 HyperOS 4 引导恢复全套镜像归档至 `~/刷机/k60/原厂备份/`
  - 固件刷写与授权：运行原生 Fastboot 脚本全量写入双槽位固件与 SukiSU Boot 镜像；清除授权补丁伪加密标志位后卡刷成功，向 `/mi_ext/product/etc/security/verificationlist.bin` 写入授权 Token
  - 模块与生态修复：修复 `magic_mount_rs` 软链接递归缺陷恢复 28 个 Material You overlay 挂载；修复 Vector 守护进程服务脚本为 `unshare -m`；执行 `znctl enforce-denylist disabled`（0）关闭黑名单排除

- **一加平板2 Pro (OPD2413 / c84b9192) 解锁、KowSU Pro Root 与隐匿模块链全量部署 (2026-09-12, 成功)**:
  - 机型规格：骁龙 8 至尊版 (SM8750P / sun 平台)，Wi-Fi 版 OEM 解锁后 Fastboot 秒解；SpiderDroid GKI 6.6.118 定制内核 + KowSU Pro (35700-2 / UAPI=2) + SuSFS 2.3.0；`stock_boot.img` 归档至 `~/刷机/一加平板2Pro/原厂备份/`
  - 打包标准：必须使用 raw ARM64 Image 并由 `avbtool add_hash_footer` 注入 Hash Footer（分区尺寸严格设定为 96MB）
  - 游戏防检测 (三角洲行动)：KernelSU 内核隐匿特性全开；TS Enhancer Extreme 伪装 green 与锁 bootloader；Tricky Store 目标列表伪装；Vector Xposed 白名单隔离；HMA-OSS 直写双路径配置并经 `android-hide-app` 自动维护
  - 禁忌红线：严禁刷第三方 Recovery、严禁降级防 ARB 硬件熔断、严禁使用手机端防误触或触控旁路补丁

- **局域网 WebDAV 服务 (Dufs) 与 Cloudflare Tunnel 部署 (2026-09-14, 成功)**:
  - 架构：安装 AUR `dufs-bin 0.46.0-2`，数据根目录 `~/WebDAV`（预设 `reader` 与 `backup`），全私有 Basic 认证（配置 `~/.config/dufs/config.yaml` 权限 600 并加入 `.chezmoiignore`）
  - 服务与公网绑定：编写 systemd user 服务 `dufs.service`（开启 linger），配合 Cloudflare Tunnel（`cloudflared-webdav.service`）绑定 `https://webdav.lanrhyme.top/`，ufw 放行 5000/tcp

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

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`，壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（含 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku/write_hyprland/write_idea）；新应用主题化必须扩展此脚本，严禁直改应用配置；Wine 应用与 Krita 不走主题引擎
- Niri：动画 stiffness 180-220 / damping-ratio 0.8 弹性轻柔滑行（cfg/animation.kdl）；窗口间距 8px（cfg/layout.kdl）；全局 opacity 0.98 + blur true（`draw-border-with-background false` 必设防聚焦实心边框；Krita/Loupe/Kando/SPlayer/cs2/gamescope 排除）
- Ghostty：输入法修复依赖 wrapper `~/.local/bin/ghostty`（`env -u GTK_IM_MODULE` 解决不转发 key release 导致 fcitx5 状态机异常）；term_bg 公式 `max(l_b+0, 4)`；集成 Master GLSL 光标着色器与连字支持
- Fcitx5：bamboo-dark 皮肤（morandi-gen 注入），竖排候选，rime_ice（雾凇拼音）；支持 niri ext-background-effect 候选框模糊
- Fastfetch：write_fastfetch 全量生成 config.jsonc；源码中 ≥U+F0000 码点必须使用 8 位 `\U000FXXXX` 转义
- Noctalia 重启：`pkill -f noctalia` 后 `setsid nohup noctalia > ~/tmp/noctalia-restart.log 2>&1 < /dev/null & disown`
- OBS：屏幕采集依赖 mesa EGL 核显渲染（强制覆盖 desktop Exec：`env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json obs`）；编码器使用核显 QSV（`obs_qsv11_v2`）；B 站推流插件位于 `~/.config/obs-studio/plugins/bilibili-stream-for-obs/`（含 PR #27 扫码登录补丁）
- Caelestia KDE Shell：KWin 6.7.4 + caelestia-shell 2.4.0 精简安装，配置位于 `~/.config/quickshell/caelestia/`，会话 `~/.local/bin/start-kwin-caelestia.sh`；缩略图依赖 PipeWire，nvidia.conf 严禁设全局 PRIME offload 变量防黑屏
- Zen 浏览器 (Flatpak)：flatpak override 注入 NVIDIA PRIME 变量；user.js 启用 `layers.dmabuf.disable=true` 防止 2D canvas 合成失效；D-Bus portal 授权只读访问 fcitx5 目录
- SPlayer-Next：AUR `splayer-next-bin`，二进制 `/opt/SPlayer-Next/SPlayer-Next`，命令 `/usr/bin/splayer-next`
- slugcatpet 桌宠：`~/Projects/slugcatpet`，GTK3 窗口必须设为 Layer.TOP

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

## 踩坑速查

- **网络（FlClash fake-ip 间歇性 TLS 失败）**：curl/git/gh 可用 `--resolve` 直连真实 IP（github.com=20.205.243.166, api.github.com=20.205.243.168, uploads.github.com=20.205.243.161）+ `http.version=HTTP/1.1`；AUR 遇到网络超时改下载 snapshot tarball 手动 makepkg；TUN 静默掉线时在 FlClash 界面开关一次网卡重启
- **提权**：pkexec 在 niri 下因 polkit 弹窗缺失卡死，需由用户在交互终端直接执行 sudo；`pkexec pacman -U` 必须使用绝对路径
- **Git**：`git tag -f` 重打注释 tag 必须带 `-m` 或 `-F` 防 vi 卡死；覆盖发布采用删远程 tag 重新 push 并重建 GitHub Release
- **adb 与多层 shell**：`su -c` 内嵌复杂变量与转义时写成本地脚本 push 后执行；抓取日志前必须 `logcat -c` 清除缓冲区防止历史日志干扰
- **Hindsight 残留处理**：`uvx daemon start` 异常退出会遗留孤儿进程锁定 `.cache/uv/.lock`，kill 后需手动删除 lock 文件
- **Android 17 (SDK 37) 与 KernelSU-Next / Zygisk Next / Vector 保留 Root 更新要点**：
  - 1. **Root 镜像注入**：OTA 后若 LKM 签名不匹配或被 Seccomp 拦截，需从官方底包提取 `boot_a.img`，利用 `android12-5.10` KMI 与当前内核版本号注入 KernelSU-Next LKM 驱动与专属签名后 Fastboot 直刷
  - 2. **Zygisk Next 黑名单排查**：若应用无法加载模块，核对 `/data/adb/ksu/bin/znctl status` 中的 `enforce_denylist`，必须执行 `znctl enforce-denylist disabled`（置 0）以防应用被跳过注入
  - 3. **Vector 守护进程**：若 `cli status` 报 Socket Failure，检查 `service.sh` 中是否残留 toybox 不支持的 `unshare --propagation slave`，统一修正为 `unshare -m`
  - 4. **Xposed 模块兼容性**：旧模块若写死判断 `SDK_INT <= 36` 会抛出 NPE（如 Thanox），需停用或反编译 smali 将 SDK 版本识别限制在 36 并做判空保护；相机等 OEM 应用小版本更新可能会变更混淆字段名，需同步反编译更新 Hook 点
