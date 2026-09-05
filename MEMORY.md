# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **Fcitx5-Rime 输入法调频优化、Emoji 移除、词库更新与汉英释义精简瘦身 (2026-09-05, 成功)**:
  - 根因：建筑物标绘工作致使「号」（552次）与「钟」（93次）等词频异常膨胀，挤压常用词「好」与「中」；Rime-ice 默认挂载 simplifier@emoji 滤镜致候选词混入大量表情；初始引入朗道全量词典（48.4万词）导致生僻词、化学及生化拉丁术语冗余；纯学术字典缺失日常口语/方位/代词/开发短语
  - 修复：全量备份词库后清理 rime_ice.userdb 及 sync 用户词库中的标绘高频条目（号、钟、空房、罗岭），使「好」与「中」回归候选首位；在 rime_ice.custom.yaml 覆写 engine/filters 移除 simplifier@emoji 并在 switches 移除 emoji 开关；全量同步上游 rime-ice 最新 HEAD（2026-09 提交 fbb516b）；通过 CC-CEDICT 规范现代词库融合 Rime-ice 基础高频词（词频>=500），两轮累计专项扩充 730+ 条高频日常口语、代词系表、人际协作与开发短语（如不大行、还可以、在这、我的、这是、帮我看看、跑测试、修bug、踩坑等），构建 140,957 条高质量实用汉英对照库并彻底剔除 34 万条冷僻生化/机械术语（载入仅 0.22s，F4 可按需切换 `[译关/译开]`）；修改已同步提交至 chezmoi 并平滑重载生效

- **Minecraft (Lunar Client) 独显启动与 Flatpak NVIDIA 驱动修复 (2026-08-31, 成功)**:
  - 根因：配置 KDE 时移除了 `environment.d/nvidia.conf` 中的全局 PRIME offload 变量致 Flatpak 沙盒不再继承独显环境变量，同时 Flatpak 运行时 NVIDIA 驱动（580.173.02）落后于宿主机（580.178.04）
  - 修复：安装 Flatpak `org.freedesktop.Platform.GL.nvidia-580-178-04` 与 32 位运行库，并通过 `flatpak override --user` 为 Lunar Client 注入 `__NV_PRIME_RENDER_OFFLOAD=1`、`__GLX_VENDOR_LIBRARY_NAME=nvidia` 与 `__VK_LAYER_NV_optimus=NVIDIA_only`

- **Noctalia 桌面外壳升级至最新 Git 构建 (2026-08-31, 成功)**:
  - 经 PKGBUILD 安全审查后从源码构建升级至 `noctalia-git 5.0.0.r5361.gf840b01ba-1`（v5.0.0-beta.10-17-gf840b01baf16）
  - 平滑重载运行（PID 102049），左侧状态栏、莫兰迪配色与全部插件正常运作

- **桌面外壳恢复为 Noctalia 与 DMS 清理 (2026-08-31, 成功)**:
  - 卸载 `dms-shell`、`dms-shell-niri` 与 `dgop` 软件包
  - 清理 `~/.config/DankMaterialShell`、`~/.local/state/DankMaterialShell` 与相关缓存
  - 重启并全面恢复 Noctalia 桌面外壳（左侧状态栏、莫兰迪配色、插件全套就绪）

- **Caelestia KDE Shell 窗口缩略图黑屏修复 (2026-08-31, 进行中)**:
  - 根因：`~/.config/environment.d/nvidia.conf` 全局设置 `__NV_PRIME_RENDER_OFFLOAD=1` + `__GLX_VENDOR_LIBRARY_NAME=nvidia`，导致 quickshell 使用 NVIDIA GPU 渲染，而 KWin 在 Intel GPU 上运行，PipeWire DMA-BUF 共享失败致缩略图全黑
  - 修复：移除 nvidia.conf 中的 PRIME offload 变量，保留 `QT_X11_NO_MITSHM=1`；需注销重新登录生效
  - 保留 `LIBVA_DRIVER_NAME=nvidia`（硬件视频解码）

- **Caelestia KDE Shell 完整安装 (2026-08-30~31)**:
  - 安装 plasma-desktop 6.7.4-1.1 + plasmazones 3.4.2-1（替代 krohnkite）
  - 克隆 caelestia-dots-kde 仓库到 ~/tmp/caelestia-dots-kde/
  - 从源码编译 caelestia-shell 2.4.0（依赖 networkmanager-qt + aubio），手动修复 cmake install 路径问题（/usr/usr/ → /usr/）
  - 部署 caelestia 配置：自启动、快捷键（Meta+Return 终端、Meta+Print 截图）、Fcitx5、cliphist
  - 截图从 spectacle 改为 mark-shot（tray 模式运行）
  - 安装 hdcy 中文翻译字典（523 处翻译）
  - 自定义会话：~/.local/bin/start-kwin-caelestia.sh + ~/.config/wayland-sessions/kwin-caelestia.desktop
  - 精简 KDE：卸载 plasma-desktop、baloo、powerdevil 等节省约 75MB（保留 kwin、plasma-workspace、plasmazones、caelestia-shell）
  - Noctalia greeter 已可发现 Plasma 会话（plasma.desktop 在 /usr/share/wayland-sessions/）

- **mark-shot 截图工具 FFmpeg 兼容性修复 (2026-08-30, 成功)**:
  - 旧手动安装的 `~/.local/bin/mark-shot`（8月9日编译）链接 FFmpeg 7.x (libavformat.so.62)，系统已升级至 FFmpeg 9.0 (libavformat.so.63) 致动态库加载失败；
  - 通过 AUR `mark-shot 0.1.49-1` 源码构建安装至 `/usr/bin/mark-shot`，并清理 `~/.local/bin/` 下残留旧副本；

- **Noctalia 桌面外壳升级至最新 Git 构建 (2026-08-28, 成功)**:
  - 通过 AUR 源码经 PKGBUILD 安全审查后构建安装 `noctalia-git 5.0.0.r5346.g5f90d2efd-1`（v5.0.0-beta.10-2-g5f90d2efd52d）；
  - 进程平滑重载运行，保留原有莫兰迪全局配色、自定义快捷键与插件生态支持。

- **K60 柔光玻璃材质与控制中心高斯模糊修复 (2026-08-27, 成功)**:
  - **项目清理**：自研 `MaterialCenter` 实验项目已完整从工作区删除并从手机彻底卸载清理；
  - **柔光玻璃与高斯模糊修复**：重置 `use_control_center=1` 并开启 `background_blur_enable`、`is_bionics_enabled`、`window_blur_enabled`、`persist.sys.background_blur_supported=true`、`persist.sys.high_end_gfx=true`；已重新激活 `HyperBackground` 与 `HyperCeiler` 模块，真机截图核验高斯模糊与柔光玻璃材质已恢复正常渲染。

- **K60 功耗诊断：min_refresh_rate 锁 120 是主因 (2026-08-26)**: B站统计 5W 实为屏幕背锅——解码正常走 c2.qti.hevc.low_latency 硬解，但 `system min_refresh_rate=120` 强制全程 1440p+120Hz 不降档（scene-daemon 在跑，疑似 Scene 所设）；次因=B站播放管线反复 flush 抖帧（ijkservice 瞬时 139% CPU）、SystemUI RenderThread 瞬时 73%（与 NotificationShade 卡顿旧疾同源，复测已回落非持续）；电池 784 循环、充电 44°C，容量估计余 85%；处理顺序：还原 min_refresh_rate=60 观察 → 必要时 LSPosed 停 freEnhance 隔离验证 → 仍差再考虑换电池；结论为功耗主因不在 Infinity-X ROM，暂缓刷澎湃 OS4

- **微信输入法去魔改保数据升级 (2026-08-25)**: 原装 3.2.0 实为 LSPatch 壳（AOSP testkey 重签，`assets/lspatch/origin.apk` 内嵌原版）；已走 root 路径：tar 备份（排缓存）→ 卸载 → 装 **官方 3.5.3/56201**（来源=应用自更新器下载到外部 data 目录的包，真签 `CN=(Tencent)` sha256 `9C:FF:5C:72:F6:23:19:CA:D7:A0:B8:51:5F:6D:78:8B`）→ 还原数据 chown 新 uid u0_a531 + restorecon -R → ime enable/set 恢复选中；进程冒烟通过 MicroMsg 词库账号数据完好；备份留存设备 `/data/local/tmp/wetype_data.tgz`(362M)/wetype_ext.tgz 与电脑 `~/tmp/wetype-update/`，用户确认键盘正常后可清；坑：**应用宝渠道包是 QZone Team 渠道重签，与官方自更新签名不一致勿用**

- **三角洲行动环境隐藏配置 (2026-08-24)**: `com.tencent.tmgp.dfm` 已加入 HMA-OSS Root-Hide scope（第 18 个，照抄微信条目）并追加进 `/data/adb/tricky_store/target.txt`；改前审计 props 全绿（locked/green/user/debuggable=0）、Vector 未 hook 该包、`/data/local/tmp` 771 外部应用不可枚举无需清理；已 force-stop 游戏待重启验证。Hunter/Momo(`io.github.vvb2060.mahoshojo`)/春秋 三检测器当前未安装（TrickyStore 里 mahoshojo/nativetest 是旧测试残留），实测需先装；若 ACE 仍检出，下一步是换 SUSFS 内核或 APatch
- **Web-Personal 雨丝消失诊断：桌面 Zen 加速 2D canvas 合成失效 (2026-08-24, 已验证修复)**: Antigravity cascade `d15a66ba-f206-4a31-9c68-bcc7f63a4a51`（任务链：CSR 图标页脚→性能优化）调试雨丝消失到一半流中断，由 DSH 接管定案——**代码无罪**（手机 Firefox 看生产站正常；最小复现页 `~/tmp/rain-canvas-test.html` 在桌面 Zen 里连静态红叉都不显示，而 canvas 的 CSS 背景可见），根因是 Flatpak Zen 强制 NVIDIA offload + `widget.dmabuf.force-enabled` + `WEBGL_DMABUF_AUTO_IMPORT` 链路上加速 2D canvas 位图不上屏的合成失效；修复为 profile user.js（`~/.var/app/app.zen_browser.zen/.zen/rlujjvm3.Default (release)/user.js`，非 chezmoi 管理）追加 `layers.dmabuf.disable=true`，用户重启 Zen 后确认雨恢复；若未来复发依次降级：`gfx.canvas.accelerated=false` → 删 flatpak override 里 WEBGL_DMABUF_* 两条 env
- **Antigravity 2.9.1 升级与启动失败双重根因修复 (2026-08-23)**: PKGBUILD 已更新至 2.9.1（build 4871453687021568）并构建安装于 `~/tmp/antigravity-pkgbuild/`；启动失败有两层根因——① `ERR_NETWORK_CHANGED`：wlan0 旧前缀（cd4）IPv6 地址 preferred↔deprecated 每 ~3 秒震荡（上游双 RA 源冲突），netlink 变更事件触发 Chromium 取消加载，该地址已自然过期自愈，复发时监控 `ip monitor address` 并删除震荡地址；② `ERR_TIMED_OUT`：language_server 无代理环境变量直连 generativelanguage/daily-cloudcode-pa.googleapis.com 被墙 → LS 初始化阻塞 → HTTPS accept 循环卡死（ss 显示 backlog 堆积），已实验证实加 https_proxy 后端口瞬间 200；**此前 2.8.1 可用是因 FlClash TUN 开着透明代理，重开 TUN 后验证通过**；若不想常开 TUN，备用方案为 wrapper 注入代理 env 或 Electron main.js 补 env。**复发案例（同日晚）**：TUN 设备会静默掉线（UI 仍显示开启、7890 端口正常），症状为 ERR_TIMED_OUT；处理：FlClash 里关/开 TUN 开关重建设备即可；注意 TUN 网卡名是 `FlClash`（不含 "tun" 字样），用 `ip -br link` 全量检查而非 grep tun
- **K60 距离传感器误触发与蓝牙连接修复 (2026-08-22)**: Redmi K60 (`mondrian`，Infinity-X 3.12 非官方社区构建，Android 16）① **距离传感器**：通话黑屏不恢复/误触口袋模式，根因是 SLPI 侧 SSC 自动校准把 stk3bcx 虚拟 prox 阈值压到噪声区（far=611/near=829，出厂为 far=1000/near=2000），修复方式为 root 改回 `/mnt/vendor/persist/sensors/registry/registry/stk3bcx_0_platform.ps.fac_cal` 出厂阈值并完整重启手机（仅重启 sensors HAL 进程不够，SLPI 固件必须整机重启才重读注册表）；修复后自动化摆动测试（logcat -c → 灭屏/亮屏循环 → 抓 `prox_recurrent_event` near_far 值）10 周期零误触发；注意 K60 的 `Proximity Sensor XiaoMi(V1.1)` 是虚拟方案（Goodix 触摸固件 + xiaomi_touch 模块融合上报，stk3bcx 仅光感），改阈值只影响 SSC 上报判定；备份：设备 `/data/local/tmp/prox_backup/` 与本地 `~/tmp/k60-prox/`；修复脚本 `/data/local/tmp/fix_prox.sh`（sed 替换 data 值 + chown system:system + chmod 600）② **蓝牙**：EDIFIER BLE 无法连接，根因是此前连着电脑时配对产生的残留配对记录损坏，重新配对即愈，非 ROM 问题 ③ 若 SSC 未来再次自动下调阈值导致复发，重跑 fix_prox.sh 后重启即可
- **ReveriePaint-native 触控引擎变换与移动工具支持及撤销修复 (2026-08-22)**: ① **变换与移动工具原生触控响应补全**：新架构 `CanvasTouchView` 原生触控层此前漏接了 `TRANSFORM` 与 `MOVE` 工具的控制手势（包括单指/手写笔拖拽变换控制点、旋转、缩放、自由形变、透视以及平移），同时解除了 `penOnlyMode` 在非笔刷绘图工具下对单指操作的误拦截，已完整移植并补全；② **笔画撤销刷新时序修复**：修复绘制笔画后点击撤销无法消除笔画的问题，显式标记图层设备 `setDirty()`，裁切时序移入 Undo 事务。Native C++ 编译部署通过并推送到远程
- **QQ 踢线复发根因修复 (2026-08-21)**: QQ 再次无提示掉线，Xposed 模块/Thanox/Vector 均已排除，真正根因是 HMA-OSS Root-Hide scope 16 个应用唯独漏了 `com.tencent.mobileqq`（内核无 SUSFS，防检测全靠 HMA，QQ 裸奔被 QSec 检出）；照抄微信条目加入 scope 并修正 config.json 属主权限后强停待验证；若仍踢线后备方案为加装 Zygisk-Assistant 类自隐藏模块
- **GitHub 个人主页状态卡片修复 (2026-08-20)**: `LanRhyme/LanRhyme` 修复失效卡片：统计/语言卡片切换至 `github-readme-stats-eight-theta.vercel.app`，连续打卡切换至 `github-readme-streak-stats-eight-theta.vercel.app`，Android Studio 徽标链接修正，折叠图路径改为相对路径 `./github-metrics.svg`
- **Android 手机环境隐藏与模块优化 (2026-08-20)**: ① `freEnhance` 重构剥离虚拟小窗代码，仅保留全局导航栏沉浸/Niagara 图标动效/多任务卡片三钩子；② QQ 踢线第一轮修复（禁用 NTQQ 耗电优化并加白名单，后被 08-21 根因修复取代）；③ `HMA-OSS Zygisk 166` 替代闭源 HMA；④ 安装 `Yet Another Bootloop Protector 8.138` 与 `Thanox 8.6`

## 设备 Redmi K60 (mondrian / ed3fdd92)

- 系统：Android 16 / SDK 36，ROM 为 Infinity-X 社区非官方构建（官方 mondrian 约 v3.6 停更，由 Telegram MondrianDevelopment 组续维），底包 HyperOS 3.0.5.0 全球版，Kernel 5.10 Weil+ 定制内核，KernelSU Next root
- 隐匿链：内核无 SUSFS，防检测全靠 HMA-OSS (`org.frknkrc44.hma_oss`) Root-Hide scope——**新增敏感应用必须加入 scope**（照抄 `com.tencent.mm` 条目：aggressiveFilter=false, useWhitelist=false, excludeSystemApps=false, applyTemplates=["Root-Hide"]），config.json 位于 `/data/user/0/org.frknkrc44.hma_oss/files/`（修改后需 chown u0_a518 + chmod 600 + restorecon）；另有 YABP 自动救砖 + Thanox 后台管理
- freEnhance 自研模块 (`io.github.lanrhyme.freenhance`)：ImmersiveHook 导航沉浸 / NiagaraHook 图标弹簧动效 / LauncherHook 多任务卡片居中过渡模糊
- 距离传感器：XiaoMi(V1.1) 虚拟 prox = Goodix 触摸固件 + xiaomi_touch 模块融合（stk3bcx 实为光感，sx933x 注册表条目为模板残留）；SSC 会自动下调阈值致误触发，复发时 `su -c sh /data/local/tmp/fix_prox.sh` 后整机重启；无 CIT 工厂菜单（*#*#6464#*#* 无效）、无 /proc/touchpanel、无 debugfs see
- adb 要点：手机易锁屏且 NotificationShade 卡住需用户手动解锁（cmd statusbar collapse 无效）；操作前查 `dumpsys window mCurrentFocus`；用户正在使用手机时勿抢操作

## 桌面环境

- 显示管理器：`greetd` + `noctalia-greeter`（Noctalia 官方原生图形化 Greeter，经 greetd.service 运行），主题壁纸与多显示器布局依赖 Noctalia 设置 → Shell → 安全 → Sync Now
- 主题引擎：`~/.config/noctalia/morandi-gen.py` 统一生成莫兰迪配色（已有 write_ghostty/write_fastfetch/write_fcitx5/write_pi/write_bilibili_danmaku 等函数）；**新应用主题化必须扩展此脚本**（添加 write_<app> 并在 main() 调用），不得直改应用配置；wine 应用与 krita 不走它
- Niri：动画 stiffness 180-220 / damping-ratio 0.8 弹性轻柔滑行（cfg/animation.kdl）；窗口间距 8px（cfg/layout.kdl）；全局 opacity 0.98 + blur true（**draw-border-with-background false 必设**否则聚焦显实心边框；Krita/Loupe/Kando/SPlayer 歌词排除）
- Ghostty：已全面替代 Alacritty（旧配置与 dotfiles 已全量清理）；输入法修复靠 wrapper `~/.local/bin/ghostty`（`env -u GTK_IM_MODULE`，chezmoi `dot_local/bin/executable_ghostty`，覆盖 niri 快捷键/launcher/mango 全部入口；根因 ghostty 不转发 key release 使 fcitx5-gtk 模块状态机异常）；term_bg 公式 `max(l_b+0, 4)` 当前 #171b17；集成 Master GLSL 光标着色器 + scrollbar system + calt/liga 连字
- Fcitx5：bamboo-dark 皮肤（morandi-gen 动态注入）、竖排候选；方案为 rime_ice（雾凇拼音），已移除 emoji 滤镜与标绘残留高频词；5.1.21 起支持 niri ext-background-effect 候选框模糊
- Fastfetch：write_fastfetch 全量生成 config.jsonc（标题三色分区 + 模块三组 + 8 圆形色点）；**源码中 ≥U+F0000 的码点必须写 8 位 `\U000FXXXX` 转义**（`\U0000FXXXX` 9 位会被 Python 截断）
- Noctalia 重启方法：`pkill -f noctalia` 后 `setsid nohup noctalia > ~/tmp/noctalia-restart.log 2>&1 < /dev/null & disown`（kill 后 niri spawn-sh-at-startup 不重拉）
- OBS：屏幕采集修复 = 覆盖 `/usr/share/applications/com.obsproject.Studio.desktop` Exec 强制 mesa EGL 核显渲染：`env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json obs`（根因 Optimus 下 niri 核显 linear buffer 只能 EGL_EXTERNAL 导入而 OBS 要 GL_TEXTURE_2D）；代价 NVENC 不可用改核显 QSV（iHD + vpl-gpu-rt 已装）；grim 截图走 wlr-screencopy 不受影响；**2026-08-25 推流失败修复**：obs-studio-browser 升到 32.2.1-3 后 NVENC 检测直接 `outdated_driver`（nvidia-580xx 580.173 legacy 分支过旧）模块不加载，但配置残留 `obs_nvenc_h264_tex` 致 rtmp_output 找不到编码器启动失败（日志特征：启动时 Encoder ID not found ×2 → 开始推流时 rtmp_output failed），B 站插件侧正常；已把 basic.ini [AdvOut] 直播/录像编码器改为 `obs_qsv11_v2`（chezmoi 已同步），若 QSV 异常备选 VAAPI H.264（ffmpeg_vaapi_tex 可用）
- obs-bilibili-stream：手动编译装于 `~/.config/obs-studio/plugins/bilibili-stream-for-obs/bin/64bit/`，已应用上游未合并 PR #27（B 站 2026-08 改版扫码登录 crossDomain ticket 解析 + Set-Cookie 大小写 strncasecmp）；**升级插件后需重新打补丁**（源码 `~/tmp/obs-bilibili-stream/`，cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DENABLE_FRONTEND_API=ON -DENABLE_QT=ON）
- Caelestia KDE Shell：KWin 6.7.4 合成器 + caelestia-shell 2.4.0（Quickshell），精简安装（无 plasmashell/systemsettings），配置于 ~/.config/quickshell/caelestia/；自定义会话 ~/.local/bin/start-kwin-caelestia.sh（noctalia greeter 可选）；窗口缩略图依赖 PipeWire + zkde_screencast_unstable_v1，**全局 NVIDIA PRIME offload 环境变量会导致黑屏**（已从 nvidia.conf 移除）
- Zen 浏览器 (Flatpak)：flatpak override 注入 NVIDIA PRIME 渲染变量实现 GPU 加速；user.js 强制 WebRender/DMA-BUF/硬件视频解码；fcitx5 主题经 D-Bus portal 权限 + 只读访问 fcitx5 目录
- SPlayer-Next：AUR `splayer-next-bin`（K-Black 维护，repack 上游官方 .pacman，无钩子已审查），2026-08-25 升至 1.0.0-8；二进制 `/opt/SPlayer-Next/SPlayer-Next`（大写），命令软链 `/usr/bin/splayer-next` 已由包托管，desktop 文件自带正确路径无需手改；Electron 43.2.0；升级遇旧手动软链冲突用 `--overwrite "/usr/bin/splayer-next"` 接管；构建副本与源包在 `~/tmp/splayer-next-update/`
- slugcatpet 桌宠（`~/Projects/slugcatpet`）：GTK3 窗口必须用 Layer.TOP（Overlay 会盖住全屏内容故不可见性反转处理）；niri 26.x focused-window 输出的 window_size 嵌套于 layout 对象内（envwatch.py 已兼容）

## 项目

### pi-web / pi-neostudio — `~/Projects/pi-web`
- 基于 agegr/pi-web 的 pi agent Web UI（Next.js 16 + React 19 + Tailwind 4，端口 30141），版本自 v1.0.0 起独立语义化（与上游 0.8.x 脱钩），npm 包 `pi-neostudio` + GitHub Release 双发布
- 上游同步策略：fork 扁平根提交无共同历史且上游已大重构，全量 merge 不可行，采用选择性移植（pi SDK 升级随带回归补丁 + 按 issue 挑选移植，patch-pi-theme.mjs postinstall 空 bgColors 守卫）
- 运行开发：`npm run dev`（node >=22.19，本机 v26.4.0），依赖用 npm install（bun 有 integrity 错误）；npm install-scripts 安全策略需 approve sharp/unrs-resolver；**shell 有 NODE_ENV=production 时会跳过 devDependencies 致 next build module-not-found，需 --include=dev**
- 发布管线：electron-builder 三平台 matrix（只在 ubuntu 构建 .next 复用，排除 `.next/dev` + `.next/cache` 防 900M 膨胀，产物 AppImage 300M/deb 212M）；release published 事件的 workflow 要求 tag 指向含最新 workflow 的提交；重建 release 需 delete + recreate
- npm 登录：浏览器 OAuth 在本机 FlClash 代理下回调失败，改 token 方式；2FA 账号 classic token 报 E403，需 Granular Access Token（包 Read/write + Bypass 2FA for publishing）
- 已知：用户浏览器 Dark Reader 注入 style 致 hydration mismatch（layout body + AppShell 根 div 已加 suppressHydrationWarning 缓解，建议 Dark Reader 排除 localhost）

### ReveriePaint-native — `~/Projects/ReveriePaint-native`（Kotlin + C++/Krita 核心，包名 com.reverie.paint，测试机 ed3fdd92）
- 笔刷引擎：集成 Krita 真实笔刷，预设 .kpp 为自包含 PNG（内嵌 XML+笔刷数据）；op factory 注册进 kritadefaultpaintops_static（避免模板跨 DSO vtable 错位段错误）；渲染 = KisBrushOp::paintLine + KisPaintInformation 压感 + KisFakeRunnableStrokeJobsExecutor 同步驱动异步 dab 管线；APK 链接 kritalibpaintop + kritadefaultpaintops_static（AGP 自动收集 CMake NEEDED 依赖到 cxx obj，jniLibs 只补 AGP 漏的库；kritacolorsmudgepaintso 类 MODULE 库需 lib 前缀副本供 -l 链接）
- 图层面板手势最终架构（十余轮调试定论）：左滑 = 行上 `awaitFirstDown(requireUnconsumed=false)` 完整事件循环 + consume 仲裁与 combinedClickable 共存；点击/长按 = combinedClickable（**长按计时事件无关，按住不动也能触发——纯事件驱动超时检测在系统不发 move 时永不触发**）；拖拽 = 列表级 pointerInput 长按激活后接管 + 数学映射 `target=(fingerY-columnTop)/rowPx` 与 animateItem 让位动画天然同步；松手顺序冻结 pendingOrder 存**层名 List<String>** 而非索引（索引在移动落地后错位会引发幻影重排动画）
- C++ KisNode 语义：`add(newNode, aboveThis)` 插到 aboveThis 上面一格（idx=index(aboveThis)+1）；正确公式 `to=size-1-insert`，向上拖(to>from) aboveIdx=to，向下拖 aboveIdx=to-1；moveNode 的"上方"是 m_layers 小索引方向（视觉下方）；背景层保护 clamp target ≤ bgVisual-1
- 独显 solo：纯渲染端过滤（compositeSoloProjection 按 keep 集=目标+祖先+后代+背景合成），零触碰 node 状态，solo 引用用节点指针免疫 index 漂移
- 构建流程：`scripts/build_native.sh`（两次 assembleDebug -PbuildNative，先 CMake 编译 jni 再补 jniLibs）；环境 QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a + KRITA_SRC_DIR=~/Projects/krita-source；增量重编约 45s；**纯 Kotlin 改动直接 assembleDebug 即可**
- 近期已完成：画布极限缩放/悬停指针/吸色阈值（08-22）、多图层液化变换目标集统一（选中集∪当前层）、手势 release 移入抬起分支（修 touchEnd 泄漏与拾色残留）、长按取色延迟协程激活、取色偏移 -48dp 可关、双指撤销三指重做、滤镜面板系列
- 待办：图像增强其余滤镜；部分新功能未经真机验证
- 调试日志约定：Kotlin tag `ReverieLq` toggle 日志 + C++ `ReverieCore` tag（RPC_LOG 走 logcat）

### Krita-MobileUI — `~/Projects/Krita-MobileUI`（暂停）
- QML 移动端原型（基于官方 tablet UI MR 2417），Simple(手机)/Studio(平板) 双模式已桌面验证；Android 构建需 Qt for Android（未装）；路线图 docs/ROADMAP.md、设计规范 docs/DESIGN.md
- QML 坑备忘：qml 工具吞 console.log（需 QT_FORCE_STDERR_LOGGING=1 + console.warn）；MultiPointTouchArea 无 onTouchReleased；QtObject 不能直接含 Connections；layer.effect 需直接子级 GaussianBlur

### Krita 插件套件（均为 LanRhyme 仓库，安装于 `~/.local/share/krita/pykrita/`，chezmoi 不管理 pykrita）
- **FolioLayers** v1.2.1（tag 指向 7b41be1）：树形图层管理/docker 双行自适应 FlowLayout/右键导出 PNG·盖印可见·创建参考图像；数位笔拖拽最终方案 = Qt 合成鼠标事件转译（`_event_is_pen_synth` 判 MouseEventSynthesizedByQt，niri/Wayland 笔事件全走鼠标合成路径）+ app 级拦截自定义拖拽状态机；Qt5/6 兼容助手 mouse_x/mouse_point/mouse_global_point（position()/globalPosition() 均为 Qt6 API，Qt5 崩溃三连修）；主题刷新信号在 Window（KisMainWindow）而非 Notifier
- **AdvancedColorPicker** v1.1.0 / **SimpleHSVSliders** v1.0.1 / **MorandiUI**（时间轴偏移修复 = 对 KisAnimTimelineFramesView 豁免全局 QSS padding）/ **InfiniteCanvas** v1.0.0（stroke_dirty 单次联动撤销防画布重复扩展死循环）
- **GmicFilters**：G'MIC + 原生滤镜中文面板（18+9 滤镜）；gmic 关键坑：内置滤镜必须带完整显式参数且用 `-o[0]` 定点输出（`-o` 会被吞成滤镜参数）
- **G'MIC 官方包**：`krita-plugin-gmic 3.7.4.1-3.1`（extra 源自带 gmic 依赖，原生插件需设置→插件管理器启用）
- 打包铁律：zip 必须含 `<name>.desktop`（pykrita 根目录注册，`ServiceTypes=Krita/PythonPlugin` + X-Python-2-Compatible=false；放插件目录内则列表不显示）；Docker 类必须继承 krita 的 DockWidget 且 setWidget() 装内容；发布后下载回验 sha256
- 仓库统一头部格式：居中 `<div align="center">` 包裹标题 + for-the-badge 徽标组（QQ qm.qq.com/q/mtg1yNCi1q + 爱发电 afdian.com/a/LanRhyme）+ 简介 + 截图，正文 ## 起左对齐

### 其他项目
- **Pi Codex GUI**（已完成交付）：`~/Project/pi-codex-gui`，Tauri 2 桌面壳 + bridge.js 协议适配（spawn `pi --mode rpc`）；遗留两坑值得记：bridge 转发扩展 UI 事件必须 `{ ...ev, type: 'ui_request' }`（spread 顺序反了 type 被覆盖致前端全部对话框失效）；RPC 模式下 `ctx.ui.custom()` 返回 undefined 不可用
- **bilibili-pixel-danmaku**：`~/Projects/bilibili-pixel-danmaku`，PySide6 弹幕助手；莫兰迪主题经 `~/.config/bilibili-pixel-danmaku/morandi_colors.json` + QFileSystemWatcher 热更新；异步重连循环退避 3/5/10/15/20/30s + ws 半死检测（90s 无数据判失效）；aiohttp 的 `session.get/ws_connect` 返回 awaitable+contextmanager 双重对象，async with 不会自动 await coroutine；已创建桌面启动项 `~/.local/share/applications/bilibili-pixel-danmaku.desktop` 并交由 chezmoi 管理
- **Pi Agent TUI**：`~/.pi/agent` 已深度主题化（zentui/open-tui 扩展，OpenCode 风格 ASCII Logo），配色由 morandi-gen.py 的 write_pi 动态同步

## 安装与服务

- **MicYou**：桌面端本地包 `micyou 2.0.0.alpha.1-1`（PKGBUILD 在 `~/tmp/micyou-local/`，基于 deb 提取；升级先 `pacman -R micyou-bin` 防 conflicts 交互提示在 pkexec 下无法应答）；Noctalia 插件已独立开源 `lanrhyme/micyou`（plugin_api=3，`~/Projects/noctalia-plugin-micyou` 与 `~/.config/noctalia/plugins/micyou`，service/widget/panel/shortcut/translations 全套）；手机端 composeApp debug 包装于 K60；**Wi-Fi 连接依赖 ufw 已放行端口：8554/tcp 控制 + 8555/udp 音频 + 8443/tcp web + 5353/udp mDNS**（连接问题先查 ufw status、ss -tlnp、avahi-browse -rt _micyou._tcp）
- **企业微信**：deepin Wine 版 `com.qq.weixin.work.deepin`（星火商店 spark-dwine-helper + deepin-wine10/8），启动 `/opt/apps/com.qq.weixin.work.deepin/files/run.sh`；Wine 容器在 `~/.deepinwine/Deepin-WXWork`；构建产物与改后 PKGBUILD 在 `~/tmp/wecom-review/` 可复用升级；AUR 克隆走 git 协议 TLS 失败改 tarball 快照
- **Waydroid**：Android 16 (LineageOS 23.2 20260803 修复版，Issue #37 已验证在 Intel iGPU/niri 下正常)；默认已开启 Intel Mesa/GBM 硬件加速；**联网依赖 UFW 放行**：`sudo ufw allow in on waydroid0 && sudo ufw reload`；管理脚本位于 `~/tmp/a16/`（`install_a16.sh` / `rollback.sh`）
- **DeepSeek Harness**：`dsh 0.1.0rc.6-2` 已装（/usr/bin/dsh）；构建需 nohup 后台 + npm_config_registry 直连官方源（npmmirror 反而慢），全量 30-40 分钟易超时；pkexec 不保留 cwd 必须绝对路径
- **DSH Superpower 预设**：`~/.dsh/.agent-presets/superpower/`（基于 shipped standard 复制，勿动 shipped 安装）；obra/superpowers 全库 14 技能内嵌于 `vendor/superpowers/`，经 agent.cordis.yml 的 skill-filesystem `customSkillDirs` 追加挂载；平时会话不加载，需要时选择器选「Superpower 模式」；更新技能库 = curl 经 clash-verge 代理端口 7897 下 codeload tarball 解压覆盖 vendor/（git clone 对 github.com TLS 不稳）；组合校验用临时动态插件注册 preset_check 工具调 standingKeyFor
- **Antigravity**：AUR 包滞后需手动维护（本地已至 2.9.1，git clone AUR 仓库改 pkgver/_build + updpkgsums + makepkg -f，本地副本 `~/tmp/antigravity-pkgbuild/`，下载 URL 形如 storage.googleapis.com/antigravity-public/antigravity-hub/<ver>-<build>/linux-x64/Antigravity.tar.gz）；agy CLI 独立 ELF（~/.local/bin/agy，agy update 自管理不随 pacman）；`antigravity --version` 输出的是内置 node 版本非应用版本
- **Sunshine + Moonlight**：`sunshine 2026.724` + `moonlight-qt 6.1.0` 已装并配置；KMS 抓屏权限 `cap_sys_admin+ep` 已赋权给 `/usr/bin/sunshine`；服务为 systemd 用户服务 `app-dev.lizardbyte.app.Sunshine.service`（已设开机自启并启动）；**ufw 放行端口**：47984/47989/47990/48010 tcp 与 47998/47999/48000/48002/48010 udp；Web 控制台在 `https://localhost:47990`
- **OnlyOffice**：cachyos 官方源 onlyoffice-bin（非 AUR 无需审查）；未主题化，如需按规则扩展 write_onlyoffice
- **Hyprland**：`hyprland 0.56.2-1` + `xdg-desktop-portal-hyprland` + `hyprlock` + `hypridle`；模块化配置于 `~/.config/hypr/`，莫兰迪配色经 `morandi-gen.py` 的 `write_hyprland` 动态注入 `colors.conf`；已编译并启用官方全景工作区概览插件 `hyprexpo`（Super+Z 触发 3x3 Expo 概览，Alt+Tab 触发 Noctalia 窗口切换器）；支持 144Hz 弹性流体贝塞尔动画与焦点透明度平滑过渡
- **PiDeck**：已完全卸载勿重装（若将来重装：下载 --resolve 直连 US IP + `-C -` 续传；启动必须 PIDECK_LINUX_DISPLAY_BACKEND=wayland；ELECTRON_RUN_AS_NODE=1 上下文会让其二进制静默退出）
- **mark-shot**：AUR `mark-shot 0.1.49-1` 源码构建（`/usr/bin/mark-shot`），截图+标注+OCR+滚动截图+录屏工具；niri 快捷键 `Mod+Print`；配置 `~/.config/mark-shot/config.json`（windowDetection 用 niri DMS、OCR 走 rapidocr-onnxruntime venv）；GNOME Shell 扩展 `mark-shot-scroll-helper@snemc.org` 用于滚动截图预览面板；**FFmpeg soname 升级时需重编译**（依赖 libavformat/libavcodec 等 .so）

## 已弃用/已删除

- **COSMIC Desktop**：System76 桌面环境，试用后已完全卸载清理
- **Denial**：Flutter + Rust Wayland 合成器，因早期 Linux Impeller 渲染微卡顿与 CJK 候选框生态不完善，已完全卸载清理
- **lpigui**（`~/Project/lpigui`）：pichamber 改造的 Vue GUI，已弃用被 pi-web 取代
- **Krita-MorandiTimeline**：已删除，备份 `~/tmp/Krita-MorandiTimeline-backup-20260803.tar.gz`
- **Alacritty**：已被 Ghostty 全面替代，配置与 dotfiles 已清除

## 踩坑速查（跨场景）

- **网络（FlClash fake-ip 间歇性 TLS 失败）**：curl/git/gh 用 `--resolve`/`-c http.curloptResolve=host:443:IP` 直连真实 IP（github.com=20.205.243.166, api.github.com=20.205.243.168, uploads.github.com=20.205.243.161）+ `http.version=HTTP/1.1` 重试循环成功率大增；gh 上传报 EOF 可能实际生效需二次确认；AUR 改 tarball 快照直连 `https://aur.archlinux.org/cgit/aur.git/snapshot/<pkg>.tar.gz` 手动 makepkg；SourceForge 走 /download 页解析 zenlayer 签名 URL + 代理 `-C -` 续传；预编译包优先 archlinuxcn/USTC 镜像
- **提权**：pkexec 在 niri 下卡死（polkit-kde-authentication-agent 不弹窗，`pkexec true` 也超时），root 操作让用户在交互终端 sudo；`pkexec pacman -U` 可用但必须绝对路径（不保留 cwd）
- **Git**：`git tag -f` 重打注释 tag 必须带 -m/-F 否则触发 vi 卡死；checkout 恢复会丢弃未提交修改；替换 release = 删远程 tag 再 push 新 tag + gh release delete/create
- **Hindsight 记忆插件（2026-08-25 试用后移除）**：用户嫌重改用轻量方案；踩坑存档——daemon 模式需 uv + 抽取 LLM（llamacpp 首跑拉 3.5G Gemma GGUF，HF 必须 `HF_ENDPOINT=https://hf-mirror.com`，PyPI 用 tuna 镜像 `UV_DEFAULT_INDEX`，两者可经 `profile create --merge --env` 固化进 `~/.hindsight/profiles/<name>.env`）；`uvx daemon start` 180s 超时杀不掉子进程，会留孤儿 hindsight-api 占住 uv cache 锁（kill 后删 `.cache/uv/.lock`）；已卸载 web profile bundle、清空 `~/.hindsight` 与 uv 缓存。Noema（全局长期记忆）保留
- **adb/多层 shell 引号**：`su -c 'VAR=x; cmd'` 变量赋值经多层引号会丢，写本地脚本 push 后 `su -c sh /path/script.sh`；`pkill -f` 模式匹配到自己命令行会杀掉自身会话，后台进程用 $! 记 PID 再 kill；grep 复杂转义经多层 shell 会假阴性，用 cat 直接验证；logcat 抓取前必 `logcat -c` 清缓冲防旧事件回放误读
