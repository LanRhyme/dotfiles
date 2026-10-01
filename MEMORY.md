# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **MicYou 主仓库迁移至 MicYou-Dev 组织 (2026-10-01, 迁移完成)**:
  - 迁移目标：由 `LanRhyme/MicYou` 完整迁移至官方组织 `MicYou-Dev/MicYou`
  - 标识兼容：保留应用包名及 Bundle Identifier `com.lanrhyme.micyou` 不变，确保现有用户升级平滑、数据与权限不丢失
  - 代码与配置同步：批量更新 Issue 模板、README、FAQ、文档、示例插件及客户端检查更新/贡献者接口地址至 `MicYou-Dev/MicYou`
  - 本地与远程同步：本地 Git remote origin 地址更新为 `https://github.com/MicYou-Dev/MicYou.git`，改动已提交并推送至新仓库 master 分支


- **代理客户端切换为 Bettbox (2026-10-01, 双客户端共存过渡)**:
  - 架构：安装 AUR `bettbox-bin 1.19.3-1`（Flutter + Mihomo 内核，二进制 `/usr/share/Bettbox/Bettbox`，软链接 `/usr/bin/Bettbox`）
  - 数据迁移：全量同步 `~/.local/share/com.follow.clash/` 订阅（`profiles/`）、数据库（`database.sqlite`）与 GEO 规则库至 `~/.local/share/com.appshub.bettbox/`
  - 权限与提权：内核 `BettboxCore` 具备 SUID root 权限（`-rwsr-sr-x`），支持 Niri 下免密启用 TUN 模式
  - 共存策略：调整配置关闭 Bettbox 启动自动连接代理与 TUN（`autoRun=False`、`systemProxy=False`、`vpnProps.enable=False`），避免与当前运行的 FlClash 冲突，供随时在前端切换

- **Redmi K60 (mondrian) Material You for ColorOS 模块未生效排查与 MagicMount 目录结构修复 (2026-09-25, 修复完成)**:
  - 现象：安装 Material You for ColorOS 模块后系统界面无任何变化
  - 根因分析：
    - 模块文件均为静态 RRO（`isStatic=true`），目标路径为 `/product/overlay/`
    - KSU 默认安装器将 `system/product` 移动至模块根目录 `product` 并创建软链接 `system/product -> ../product`
    - 元模块 `magic_mount_rs` 仅扫描模块目录下的 `system` 树，在根挂载检查时捕获到 `product (Symlink)`，判定无法在 `/` 建立 tmpfs 抛出 `cannot create tmpfs on /, ignore: product`，导致 28 个覆盖层 APK 全部被跳过，实际挂载数为 0
  - 修复处置：
    - 移除模块内部 `system/product` 软链接，将 `product` 真实目录移回 `system/product/`
    - 补丁 `magic_mount_rs/metainstall.sh`，注释强制剥离 `system/$part` 的循环，避免后续模块安装再次破坏目录层级
    - 验证 `magic_mount_rs` 挂载逻辑，实测 28 个 overlay APK 已成功覆盖挂载至 `/product/overlay`，需设备重启使 PMS/OMS 重新载入静态覆盖层
    - 样式调整：已将配置切换为 `systemui_style="1"`（Monet 莫奈胶囊样式），并将覆盖层替换为 `SystemUI_dual_monet.apk`，重新挂载完毕

- **Captive Portal 自动检测与浏览器打开 (2026-09-18, 修复完成)**:
  - 需求：连接需要认证的网络时自动弹出登录页面，并在 Noctalia 状态栏/通知中心显示提醒
  - 根因排查：原 bash 脚本匹配小写输出（`portal`）失败（写死大写 `PORTAL`）、`dbus-monitor` 仅监听全局 `StateChanged` 错失异步连通性更新、缺少启动自检、`DOMAIN` 字段非法
  - 重构实现：改用 Python + `gi.repository.NM` 原生绑定，基于 GLib MainLoop 事件监听，无 CPU 轮询
  - 智能探测：捕获 HTTP 302/307 `Location` 跳转直达真实认证页，兼容 `PORTAL` 与误报 `LIMITED`
  - 防抖与自愈：单次网络连接仅弹窗一次，认证中（PORTAL）启动 5s 轻量轮询检测登录状态，认证成功（FULL）后弹通知并自动停止轮询
  - 服务管理：`captive-portal-monitor.service` 常驻后台，附带 `captive-portal-open` 便捷手动打开命令

- **Redmi K60 (mondrian) 底层完整备份与 ColorOS 16.1 (Android 16) 全量 Fastboot 刷入与授权补丁卡刷 (2026-09-14, 成功)**:
  - 底层备份：刷机前通过 ADB Root 提取基带校准（`modemst1/2`、`fsg/fsc`）、硬件与传感器校准（`persist`、`persistbak`）、设备信息（`devinfo`）及原厂 HyperOS 4 引导恢复全量镜像（`boot_a/b`、`vendor_boot_a/b`、`dtbo_a/b`、`recovery_a/b`、`vbmeta`），全量归档至 `~/刷机/k60/原厂备份/`
  - 固件刷写：解压 `super.img.zst`（8.5GB），编写并运行 Linux Fastboot 原生刷机脚本 `flash_coloros.sh`，向双槽位全量写入 VAB 底层固件、`dtbo`、定制 Recovery、`super` 核心镜像及修补了 KPM 的 SukiSU Boot 镜像，并清除 metadata 与 userdata
  - 授权补丁解密与刷入：分析发现 `VerificationPatchV2_20260914.zip` 采用了 Zip 伪加密技术（中心目录通用标记位第 0 位置 1 假报密码），清除标志位后恢复标准 Zip 格式，由 TWRP 成功刷入 `/tmp/patch.zip`，向 `/mi_ext/product/etc/security/verificationlist.bin` 写入授权 Token（`9a033082...`），并在 TWRP 中重建格式化 Data (f2fs) 与 Metadata (ext4)

- **局域网 WebDAV 服务 (Dufs) 部署与自启动 (2026-09-14, 成功)**:
  - 需求：搭建局域网 WebDAV 服务，用于手机端开源阅读（Legado）同步书架配置及多端日常备份
  - 架构：安装 AUR `dufs-bin 0.46.0-2`（已做 PKGBUILD 静态安全审查），数据根目录 `~/WebDAV`（预设 `reader` 与 `backup`）
  - 权限与安全：全私有 Basic 认证（用户 `lanrhyme`），密码配置位于 `~/.config/dufs/config.yaml`（权限 600，已加入 `.chezmoiignore` 杜绝泄露）
  - 服务与自启：编写 systemd user 服务 `dufs.service`，配合 `loginctl enable-linger lanrhyme` 保证开机无需登录即可常驻后台；ufw 放行 5000/tcp；服务配置纳入 chezmoi 托管

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

- **一加平板2 Pro (OPD2413 / c84b9192) 解锁、KowSU Pro Root 与隐匿模块链全量部署 (2026-09-12, 成功)**:
  - 机型纠偏：真机为骁龙 8 至尊版 (SM8750 / sun 平台)，设备代号 OPD2413 (OP615EL1)，非天玑版 OPD2508
  - 解锁流程：ColorOS 16 Wi-Fi 平板无需手机端深度测试 APK，开发者选项勾选 OEM 解锁后直接 `fastboot flashing unlock` 物理音量键确认秒解
  - 内核与 Root：
    - 采用古塵 SpiderDroid GKI 6.6.118 (sun 平台定制内核)，内置 KernelSU (35706) 与 SuSFS 2.3.0
    - 打包标准：骁龙 8 至尊版 ABL 强依赖标准 AVB 2.0 校验尾部，必须使用 raw ARM64 `Image` 并由 `avbtool add_hash_footer` 注入 Hash Footer（分区尺寸 96MB 100663296 字节）
    - 管理器：部署 KowSU Pro v3.3.0-99 (35700-2)，已启用 ADB Root、传统 SU 命令、隐藏 SELinux 与内核级卸载模块
  - 原厂备份：提权后完整提取 `boot_b` 与 `init_boot_b` 官方纯净底包镜像，存档于 `~/刷机/一加平板2Pro/原厂备份/`
  - 模块与隐匿环境：
    - 基础框架：YABP 防砖模块 + Zygisk Next 1.5.0（已配置匿名内存 anonymous memory 模式）
    - 隐匿与 Hook：Vector v2.2 (3080) + Tricky Store v1.4.1 + TS Enhancer Extreme + HMA-OSS Zygisk
    - 激活 Xposed 模块：LuckyTool v1.3.4、CorePatch v4.9、fuckbiliads
    - 音频引擎处置：JamesDSP v6.0 (2023-11) 仅适配旧版 Android 13/14 HIDL 音频架构，与 ColorOS 16 骁龙 8 至尊版 AIDL Audio Effect HAL 架构断代冲突，已彻底卸载模块与应用以保持系统音频纯净
    - 硬件防损防范：坚决杜绝手机端防误触/外挂触控板模块，平板原生防误触与手写笔压感完好保留

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
- 系统：ColorOS 16.1 / Android 16（ROM: ClearSkys 20260830 移植版，基底 OnePlus Ace 6，内核 5.10.246-AetherKernel），SukiSU Boot root
- 底层备份：位于 `~/刷机/k60/原厂备份/`（EFS/基带 `modemst1/2`、`fsg/fsc`，校准 `persist/persistbak`，`devinfo`，HyperOS 4 双槽位 `boot/vendor_boot/dtbo/recovery/vbmeta` 全套原厂镜像）
- 模块链：YABP、Zygisk Next (匿名内存模式，enforce-denylist 已置 0)、Vector (已修复 service.sh 为 unshare -m)、Tricky Store + TS Enhancer Extreme (内置 keybox)、HMA-OSS Zygisk
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）、fuckbiliads
- 授权机制：轻量主板 ID 验证（本机 ID `0x0000043bfce1db8a`），授权凭据位于 `/mi_ext/product/etc/security/verificationlist.bin`（SHA-256 token `9a033082...`）；补丁包采用 Zip 伪加密，消除中心目录标志位后卡刷成功
- 数据恢复：Data 分区已全新格式化为 f2fs，Metadata 格式化为 ext4，应用与数据恢复由 DataBackup 托管回传至 `/sdcard/DataBackup/`
- adb 要点：操作前核对 `dumpsys window mCurrentFocus`；用户使用手机时切勿抢占操作

### 一加平板2 Pro (OPD2413 / c84b9192)
- 硬件规格：骁龙 8 至尊版 (SM8750P / sun 平台)，Wi-Fi 版无需深度测试 APK，OEM 解锁后 Fastboot 秒解
- 系统内核：ColorOS 16 (Android 16 / SDK 36)，SpiderDroid GKI 6.6.118 (sun 定制)，KowSU Pro v3.3.0 (35700-2 / UAPI=2) + 内核内置 SuSFS 2.3.0
- 原厂备份：位于 `~/刷机/一加平板2Pro/原厂备份/`（`stock_boot.img` 96MB、`stock_init_boot.img` 8MB）
- 模块链：YABP、Zygisk Next (匿名内存)、Vector (API 102)、Tricky Store + TS Enhancer Extreme、HMA-OSS Zygisk (JamesDSP 因 Android 16 AIDL 架构不兼容已移除)
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、fuckbiliads、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）
- 游戏防检测 (三角洲行动 com.tencent.tmgp.dfm)：
  - 内核层：KernelSU `kernel_umount`、`selinux_hide`、`avc_spoof` 特性全开并持久化保存
  - 属性伪装：TS Enhancer Extreme 伪装 `green` 与锁 bootloader
  - 密钥认证：Tricky Store `target.txt` 纳入名单
  - 作用域隔离：Vector Xposed 白名单机制对游戏零注入
  - 应用列表隐藏：HMA-OSS 直写双路径配置（`/data/misc/hide_my_applist_aimdadlejpdcwkeh/config.json` 属主 `system:system` 600 与 `/data/user/0/org.frknkrc44.hma_oss/files/config.json` 属主 `u0_a346:u0_a346` 600），屏蔽 KowSU Pro、Vector、LuckyTool、CorePatch、fuckbiliads、HMA-OSS
  - 运维脚本：`~/.local/bin/android-hide-app`（`android-hide-app [-l] [-r] <包名>`），自动维护双路径与 Tricky Store 名单，全静默执行无触摸交互
- 禁忌红线：严禁刷入第三方 Recovery；严禁跨版本/降级刷机触发 ARB 熔断；严禁使用手机端防误触或手写笔旁路模块（`patch-trackmotion`、`disable-stylus-blocker`）以保护平板原生防误触与手写笔功能

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`，壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（含 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku/write_hyprland）；新应用主题化必须扩展此脚本，严禁直改应用配置；Wine 应用与 Krita 不走主题引擎
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
- 笔刷：KisBrushOp::paintLine + KisFakeRunnableStrokeJobsExecutor 同步驱动异步管线；静态注册 kritadefaultpaintops_static 防 DSO 段错误
- 图层架构：手势消费仲裁与 combinedClickable 共存；列表级长按接管拖拽；松手冻结 pendingOrder 存层名 List<String> 防索引错位；KisNode 语义向上拖 insert 上方，向下拖 insert 下方
- 构建：`scripts/build_native.sh`（QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a，增量编译约 45s；纯 Kotlin 改动直接 assembleDebug）

### Krita 插件套件
- 源码位于 `~/.local/share/krita/pykrita/`（FolioLayers v1.2.1、AdvancedColorPicker v1.1.0、SimpleHSVSliders v1.0.1、MorandiUI、InfiniteCanvas v1.0.0、GmicFilters）
- 关键规范：打包 zip 根目录必须含 `<name>.desktop`（`ServiceTypes=Krita/PythonPlugin` 且 `X-Python-2-Compatible=false`）；Docker 必须继承 KisMainWindow 的 DockWidget；G'MIC 面板滤镜参数必须带显式参数并用 `-o[0]` 指定输出

### 其他项目
- **threejs-dragon-flight**：`~/Projects/Tests/threejs-dragon-flight`，3D 巨龙空域自由翱翔飞行模拟器，Three.js + 气动扑翼骨骼动画 + 浮空群岛云海 + 烈焰龙息粒子与龙吼音效
- **threejs-pistol-disassembly**：`~/Projects/Tests/threejs-pistol-disassembly`，3D 手枪机械结构拆解与精密爆炸图交互系统，Three.js + Web Audio API 机械声效 + 分步教学与零件检视
- **voxel-jrpg-village**：`~/Projects/Tests/voxel-jrpg-village`，日式幻想体素村落 JRPG 网页，Three.js + Web Audio API 原生程序化和弦合成 + 角色漫游与对话系统
- **Pi Codex GUI**：`~/Project/pi-codex-gui`，Tauri 2 + bridge.js（RPC 模式下事件转发格式必须为 `{ ...ev, type: 'ui_request' }`）
- **bilibili-pixel-danmaku**：`~/Projects/bilibili-pixel-danmaku`，PySide6 弹幕助手，莫兰迪配色经 morandi_colors.json 热更新，启动项由 chezmoi 托管
- **Pi Agent TUI**：`~/.pi/agent`，zentui/open-tui 扩展，morandi-gen 的 write_pi 同步配色
- **Krita-MobileUI**：`~/Projects/Krita-MobileUI`（暂停中）

## 安装与服务

- **Bettbox & FlClash**：AUR 包 `bettbox-bin 1.19.3-1` 与 `flclash-bin 0.8.93-1`；数据位于 `~/.local/share/com.appshub.bettbox/`；BettboxCore 内置 SUID root 免密启动 TUN；当前保留双客户端共存，待完全习惯后可卸载 flclash-bin
- **Xiaomi MiMo Desktop**：AUR 包 `mimo-desktop 26.909.91205-2`；官方 Linux deb 打包，二进制 `/opt/Xiaomi MiMo/xiaomi-mimo-desktop`，命令 `mimo-desktop`；针对官方包漏打 `node-machine-id` 导致登录缺失 `deviceId` 报错「参数错误」的问题，已在 PKGBUILD 的 `package()` 中通过直接读取 `/etc/machine-id` 补丁修复 `app.asar`
- **Dufs (WebDAV) & Cloudflare Tunnel**：AUR 包 `dufs-bin 0.46.0-2`；数据根目录 `~/WebDAV`（含 `reader/`、`backup/`）；监听本地 `5000/tcp`（全私有 Basic 认证，用户 `lanrhyme`）；配置文件 `~/.config/dufs/config.yaml`（权限 600）；搭配 Cloudflare Tunnel（`cloudflared-webdav.service`）绑定公网域名 `https://webdav.lanrhyme.top/`；systemd user 服务常驻自启（开启 linger），全网络环境直连免改 IP
- **MicYou**：本地包 `micyou 2.0.0.alpha.1-1`；Noctalia 插件开源于 `lanrhyme/micyou`；手机端安装于 K60；ufw 放行 8554/tcp、8555/udp、8443/tcp、5353/udp
- **企业微信**：deepin Wine 版 `com.qq.weixin.work.deepin`，容器位于 `~/.deepinwine/Deepin-WXWork`，启动脚本 `/opt/apps/com.qq.weixin.work.deepin/files/run.sh`
- **Waydroid**：Android 16 (LineageOS 23.2)，开启 Intel iGPU/GBM 加速；依赖 UFW 规则 `sudo ufw allow in on waydroid0`；脚本位于 `~/tmp/a16/`
- **DeepSeek Harness**：`dsh 0.1.0rc.6-2`（/usr/bin/dsh）；Superpower 预设位于 `~/.dsh/.agent-presets/superpower/`；LLM 路由配置在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers`（密钥只存 `~/.dsh/.credentials.yaml`，配置里用 `apiKeyEnv` 引用）；已接入 WFClub 中转 `https://api.wfclub.fun/v1`（route `openai`，默认模型 `deepseek-ai/DeepSeek-V4.1-Flash`）
  - baseURL 必须写成不带 `/chat/completions` 的 `https://…/v1`：SDK 自行拼接该路径，且模型发现固定请求 `${baseURL}/models`
  - 模型 id 必须取中转站 `/v1/models` 返回的真实值，自造别名会 `model_not_found`
  - 模型默认 `input` 仅为 `["text"]`，要识图须在 model 条目显式加 `input: [text, image]`；已对 `deepseek-ai/DeepSeek-V4.1-Flash` 开启并实测可用
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
