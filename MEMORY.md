# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **Redmi K60 (mondrian) Android 17 (SDK 37) 系统更新后 Zygisk / Vector 框架及 Xposed 模块故障排查与修复 (2026-09-12, 成功)**:
  - 现象：系统小版本更新至 Android 17 / SDK 37 后，Thanox 闪退、普通应用（微信输入法、B站、相机等）未能成功加载 Xposed 模块
  - 根因分析：
    - Thanox 崩溃：代码写死最高适配至 SDK 36，遇到 SDK 37 时 `getXposedHookZygoteInitForSdk` 返回 null 触发 NPE，已彻底卸载并停用 Thanox
    - Vector 自启失败：官方模块包 `service.sh` 包含 Android toybox `unshare` 不支持的 `--propagation slave` 参数，导致守护进程开机无法拉起；修正为 `unshare -m` 后自启恢复
    - 模块未注入普通应用：Zygisk Next 默认开启了 `enforce_denylist`（值为 1），导致 Zygote 在 fork 普通应用进程时直接跳过 Zygisk 注入
  - 修复与重刷：
    - 从 GitHub 下载最新纯净版 `Zygisk-Next-1.5.0-843-5217106-release.zip` 与 `Vector-v2.2-3080-Release.zip`，通过 `ksud module install` 纯净重刷并清除字节修改
    - 修复 `service.sh` 为 `unshare -m "$MODDIR/daemon" ...`
    - 执行 `/data/adb/ksu/bin/znctl enforce-denylist disabled`，永久写入 `/data/adb/zygisksu/denylist_enforce`（置 0）关闭黑名单排除
    - 现场实测验证 SystemUI、微信输入法（WeTypeHook + WeTypeKaomoji）、B 站（fuckbiliads）、相机（MiuiCamera-Fix）、系统服务（CorePatch + HyperCeiler + InxLocker）均已成功注入运行

- **Redmi K60 (mondrian) 系统更新后 KernelSU-Next (v3.3.0) 镜像提取与 Root 恢复 (2026-09-12, 成功)**:
  - 根因：刷入底包 `P-mondrian-ota_images-v4.0.12-OS4.0.0.7.XMNCNXM-user-17.0.zip` 内置 `boot_a.img` 携带旧版官方 KernelSU LKM（v3.2.6/32601），硬编码官方签名导致 KernelSU-Next 管理器（v3.3.0/33214）被 Seccomp 拦截报未安装且版本低于 33188
  - 修复：官方底包提取 `images/boot_a.img`，利用 `android12-5.10` KMI 与 `5.10.252-dirty` 注入 KernelSU-Next v3.3.0 LKM 驱动与专属签名，生成 `boot_ksunext_v3.3.0.img`
  - 部署：Fastboot 直刷 `boot_ab` 分区，更新 `/data/adb/ksud` 为 3.3.0，手机重启后 KernelSU-Next 管理器全面识别（工作中 LKM GKI2，已恢复全部 11 个授权与 9 个激活模块，Zygisk/Vector 正常运作）
  - 备份：产物存档于电脑 `~/tmp/k60_root/boot_ksunext_v3.3.0.img` 与手机 `/sdcard/Download/boot_ksunext_v3.3.0.img`

- **一加平板2 Pro (OPD2508) 解锁、升级与 KowSU Pro Root 环境就绪 (2026-09-11, 就绪)**:
  - 资产准备：已在 `~/刷机/一加平板2Pro/` 完成全量资产筹备
    - `镜像准备/boot_kowsu_pro.img`：借用 K60 注入 KPM 内核补丁，合成搭载 SuSFS 2.3.0 + KSU 3.3.0 (UAPI=2) 的 GKI 6.6.118 定制 Boot 镜像，Fastboot 一键直刷
    - `镜像准备/boot_stock_A33.img` 与 `init_boot_stock_A33.img`：官方 A.33 纯净提取备份，用于保底救砖
    - `镜像准备/KowSU_Pro_v3.3.0-99.apk`：已提取适配 UAPI=2 的专用管理器
    - `必备模块合集/`：已归档 Vector (v2.2 3080)、Vector Manager、Zygisk Next、Tricky Store、TS Enhancer Extreme、HMA-OSS、YABP 防砖模块、LuckyTool (v1.3.4)、CorePatch (v4.9)、fuckbiliads 与 JamesDSP (v6.0)
  - 核心机制：ColorOS 15 开启 OEM 解锁后直接 `fastboot flashing unlock` 秒解；升级 ColorOS 16 A.33 后严禁降级防止 ARB 硬件熔断；不刷第三方 Recovery，靠 Fastboot 直刷与 YABP 自愈

- **B站人脸验证风控处置与环境配置收敛 (2026-09-10, 归档)**:
  - 决策：针对金融级活体/人脸风控（蚂蚁金服 APSE 深度综合云端风控），转由原生纯净设备（一加平板）完成认证
  - 配置恢复：Vector 重新将 B 站（`tv.danmaku.bili`）加入 `fuckbiliads` 作用域；开发者选项与 USB 调试保持常开
  - 安全保留：Zygisk Next 保留 `memory-type anonymous` 与 `enforce-denylist enabled`；`/data/local/tmp` 保留 771 权限；Tricky Store 目标列表保留 B 站与支付宝伪装

- **Redmi K60 (mondrian) 系统升级至 NexusHyper v4.0.12 及相机强退修复模块发布 (2026-09-10, 成功)**:
  - 升级：刷入 `P-mondrian-ota_images-v4.0.12-OS4.0.0.7.XMNCNXM-user-17.0.zip`（Android 17 / HyperOS 4 移植版，内核 5.10.237-Fuutao-Qn_miao / 5.10.252-dirty），保留数据与激活模块
  - 相机修复：开发 Xposed 模块 `MiuiCamera-Fix`（`io.github.lanrhyme.camerafix`），拦截 `G6.c.w()` 返回 `false` 并修正 `f2302a = Boolean.FALSE`，丢弃 Message 11 退出消息，解决移植包机型校验失败强退问题
  - 开源发布：项目位于 `~/Projects/MiuiCamera-Fix`，源码已推送到 `LanRhyme/MiuiCamera-Fix` 并发布 `v1.0.0` Release

- **微信键盘表情面板颜文字增强与复用池隔离修复 (2026-09-09, 成功)**:
  - 修复：开发 `WeType-Kaomoji`（`io.github.lanrhyme.wetypekaomoji`），Hook `getItemViewType` 分配独立 `VIEW_TYPE_KAOMOJI`（88）根除与 Emoji 复用池污染；顶栏注入滑动胶囊分类栏；扩充 250+ 萌系颜文字
  - 发布：通过 Xposed 官方审核，发布至 `Xposed-Modules-Repo/io.github.lanrhyme.wetypekaomoji`（Tag: 1-1.0.0）与源码仓库 `LanRhyme/WeType-Kaomoji`（Tag: v1.0.0）

- **Fcitx5-Rime 输入法调频优化与词库精简瘦身 (2026-09-05, 成功)**:
  - 修复：清理 userdb 标绘异常高频条目；覆写 engine/filters 移除 emoji 滤镜；基于 CC-CEDICT 规范库与 Rime-ice 高频词融合扩充 730+ 条口语与开发短语，剔除 34 万生僻术语，汉英对照词库瘦身至 14 万条（载入 0.22s）

## 设备

### Redmi K60 (mondrian / ed3fdd92)
- 系统：Android 17 / HyperOS 4 移植版（ROM: NexusHyper v4.0.12，底包 OS4.0.0.7.XMNCNXM，内核 5.10.252-dirty），KernelSU-Next v3.3.0 (LKM GKI2) root
- 隐匿链：内核无 SUSFS，防检测依赖 HMA-OSS (`org.frknkrc44.hma_oss`) Root-Hide scope；敏感应用必须加入 scope（照抄 `com.tencent.mm` 配置）；配置位于 `/data/user/0/org.frknkrc44.hma_oss/files/config.json`（权限 u0_a518 + 600）；搭配 YABP 自动救砖；Thanox 已弃用卸载；Zygisk Next 必须保持 `enforce-denylist disabled`（防止普通应用被隔离无法注入 Vector）；Vector 的 `service.sh` 需使用 `unshare -m`（不可用 `--propagation slave`）
- 自研模块：`MiuiCamera-Fix`（修复相机机型校验闪退）、`freEnhance`（导航沉浸、Niagara 图标弹簧、多任务居中模糊）
- 距离传感器：XiaoMi(V1.1) 虚拟 prox = Goodix 触摸固件 + xiaomi_touch 模块融合；SSC 自动降阈值导致误触发时，执行 `su -c sh /data/local/tmp/fix_prox.sh` 后整机重启
- adb 要点：易锁屏且 NotificationShade 卡住需手动解锁；操作前核对 `dumpsys window mCurrentFocus`；用户使用手机时切勿抢占操作

### 一加平板2 Pro (OPD2508)
- 系统：ColorOS 15 / 16 (A.33)，内核 GKI 6.6.118，Root 方案 KowSU Pro v3.3.0 (UAPI=2) + SuSFS 2.3.0
- 刷机资产：位于 `~/刷机/一加平板2Pro/`（`boot_kowsu_pro.img` 定制镜像、`boot_stock_A33.img` 官方原包、`KowSU_Pro_v3.3.0-99.apk` 管理器、必备模块合集）
- 机制铁律：ColorOS 15 直接 `fastboot flashing unlock` 秒解（ColorOS 16 需深度测试）；升级 ColorOS 16 A.33 后严禁降级防止 ARB e-fuse 熔断变砖；不刷第三方 Recovery，靠 Fastboot 直刷与 YABP 防砖自愈

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`，壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（含 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku/write_hyprland）；新应用主题化必须扩展此脚本，严禁直改应用配置；Wine 应用与 Krita 不走主题引擎
- Niri：动画 stiffness 180-220 / damping-ratio 0.8 弹性轻柔滑行（cfg/animation.kdl）；窗口间距 8px（cfg/layout.kdl）；全局 opacity 0.98 + blur true（`draw-border-with-background false` 必设防聚焦实心边框；Krita/Loupe/Kando/SPlayer 排除）
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
- 笔刷：KisBrushOp::paintLine + KisFakeRunnableStrokeJobsExecutor 同步驱动异步管线；静态注册 kritadefaultpaintops_static 防 DSO 段错误
- 图层架构：手势消费仲裁与 combinedClickable 共存；列表级长按接管拖拽；松手冻结 pendingOrder 存层名 List<String> 防索引错位；KisNode 语义向上拖 insert 上方，向下拖 insert 下方
- 构建：`scripts/build_native.sh`（QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a，增量编译约 45s；纯 Kotlin 改动直接 assembleDebug）

### Krita 插件套件
- 源码位于 `~/.local/share/krita/pykrita/`（FolioLayers v1.2.1、AdvancedColorPicker v1.1.0、SimpleHSVSliders v1.0.1、MorandiUI、InfiniteCanvas v1.0.0、GmicFilters）
- 关键规范：打包 zip 根目录必须含 `<name>.desktop`（`ServiceTypes=Krita/PythonPlugin` 且 `X-Python-2-Compatible=false`）；Docker 必须继承 KisMainWindow 的 DockWidget；G'MIC 面板滤镜参数必须带显式参数并用 `-o[0]` 指定输出

### 其他项目
- **Pi Codex GUI**：`~/Project/pi-codex-gui`，Tauri 2 + bridge.js（RPC 模式下事件转发格式必须为 `{ ...ev, type: 'ui_request' }`）
- **bilibili-pixel-danmaku**：`~/Projects/bilibili-pixel-danmaku`，PySide6 弹幕助手，莫兰迪配色经 morandi_colors.json 热更新，启动项由 chezmoi 托管
- **Pi Agent TUI**：`~/.pi/agent`，zentui/open-tui 扩展，morandi-gen 的 write_pi 同步配色
- **Krita-MobileUI**：`~/Projects/Krita-MobileUI`（暂停中）

## 安装与服务

- **MicYou**：本地包 `micyou 2.0.0.alpha.1-1`；Noctalia 插件开源于 `lanrhyme/micyou`；手机端安装于 K60；ufw 放行 8554/tcp、8555/udp、8443/tcp、5353/udp
- **企业微信**：deepin Wine 版 `com.qq.weixin.work.deepin`，容器位于 `~/.deepinwine/Deepin-WXWork`，启动脚本 `/opt/apps/com.qq.weixin.work.deepin/files/run.sh`
- **Waydroid**：Android 16 (LineageOS 23.2)，开启 Intel iGPU/GBM 加速；依赖 UFW 规则 `sudo ufw allow in on waydroid0`；脚本位于 `~/tmp/a16/`
- **DeepSeek Harness**：`dsh 0.1.0rc.6-2`（/usr/bin/dsh）；Superpower 预设位于 `~/.dsh/.agent-presets/superpower/`
- **Antigravity**：AUR 包滞后需手动维护（本地 2.9.1，构建于 `~/tmp/antigravity-pkgbuild/`）；网络直连易超时，依赖 FlClash TUN 透明代理正常连通；CLI 为 `~/.local/bin/agy`
- **Sunshine + Moonlight**：`sunshine 2026.724`（赋权 `cap_sys_admin+ep`，systemd 服务开机自启）+ `moonlight-qt 6.1.0`；ufw 放行 47984/47989/47990/48010 tcp 与 47998/47999/48000/48002/48010 udp；控制台 `https://localhost:47990`
- **OnlyOffice**：cachyos 官方源 `onlyoffice-bin`
- **Hyprland**：`hyprland 0.56.2-1` + `hyprexpo`（Super+Z 概览，Alt+Tab 窗口切换）；莫兰迪配色经 `write_hyprland` 注入
- **mark-shot**：AUR `mark-shot 0.1.49-1`（`/usr/bin/mark-shot`），快捷键 `Mod+Print`；系统 FFmpeg soname 升级时需重新源码构建

## 已弃用/已删除

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
