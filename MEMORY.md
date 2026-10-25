# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

- **Tailscale 双端掉线根因排查与 Root 守护态自愈 (2026-10-26, 完成)**:
  - 现象与控制台基线: 电脑端 cachyos (100.73.79.77) 全程健康, 手机 k60 于 21:12 离线, 平板于 23:05 离线, 双端 KeyExpiry 均为 2027-04 未过期, 控制台状态为 online=no 而非 logged out
  - 根因定位: 双端均为 `/data/adb/tailscale/tailscaled` 原生 Root 守护 (非 App VpnService), 断网后日志卡死在 `Rebind; defIf=... rebind-no-localaddr` 与 `dial ... connect: network is unreachable` 死循环, 永远无法向 controlplane 轮询 netmap, 只有重启守护进程才能恢复
  - 触发时刻: 手机 21:11 移动数据重拨 (10.91.232.58/30 -> 10.239.213.179/29) 叠加热点与通信共享链路重整; 平板 23:04 从 192.168.250.254 切换至喵～ WiFi (10.85.125.91)
  - 平板附加故障: 开机脚本 `DEFAULT_IFACE=$(ip route show table 0 | awk ...)` 只排除 dummy/tailscale, 未排除 tun/vgate 虚拟网卡, 当前会命中 Clash 的 `default dev tun0`, 生成失效的 `ip rule pref 4800 lookup 1015` (表 1015 早已随旧网络删除), 需改为挑选物理出口
  - 处置: 手机执行 `sh /data/adb/service.d/tailscaled.sh` 重启, 平板手工 `killall -9 tailscaled` + nohup 重启 + `ip rule add iif lo uidrange 0-0 pref 4800 lookup wlan0`, `tailscale up --accept-dns=false --netfilter-mode=off`, 双端恢复 (平板经 10.85.125.91 直连电脑, 手机经 DERP hkg 中继)
  - 副作用: 手机 adbd 无线监听 (5555) 随守护重启短暂丢失后自行恢复, 现已稳定走 Tailscale 通道 100.127.72.106:5555 (局域网 10.85.125.98:5555 通道记为 stale offline)
  - 加固落地 (双端同版脚本): `/data/adb/service.d/tailscaled.sh` 重写为「启动 + 看门狗」单文件 (旧版备份 tailscaled.sh.bak-20261026), 出口改为动态解析 netd 的 `31000 fwmark 0x0/0xffff lookup <iface>` 规则 (只认 wlan*/rmnet_data*/eth*/p2p0, 显式排除 tun/vgate/dummy/ifb), 网卡变化立刻刷新 pref 4700 与 4800 规则; 看门狗每 30 秒读 `tailscale status --json --peers=false` 的 Health 数组, 命中 network map / coordination server / network is unreachable / logged out 连续 6 次 (3 分钟) 自动重启守护, 进程消失也自动拉起, 日志落 `/data/adb/tailscale/watchdog.log` (超 256KB 自截断)
  - 关键纠正 (覆盖 2026-10-24 结论): 手机端 pref 4800 规则不可删除. 实测 00:30 删除后 00:32 立即失联, 守护进程自身 socket 命中 Android mark 规则链的 `unreachable` 分支报 ENETUNREACH, 取不到 control key 显示 logged out, 重启守护也无效; 00:39 恢复 `pref 4800 lookup rmnet_data3` 后 3 秒内重新登录成功. `iif lo` 限定只匹配本机生成流量, 通信共享转发包 iif 非 lo 不会命中, 故双端统一 UID0_RULE=1
  - 自愈实测: 手机 00:34-00:37 因规则缺失进入 mapresponse-timeout, 看门狗第 6 次探测 (00:37:14) 自动重启守护, 恢复后 00:39:23 重新 active login; 平板 4800 出口由 wlan0 动态维持, 两观察窗内无任何误重启

- **ReveriePaint-native 添加繁体中文、日语与猫猫语本地化支持并确立大版本多语言维护规范 (2026-10-26, 完成)**:
  - 核心架构与多语言体系扩展:
    - LanguageManager 接入新语言枚举：扩展 AppLanguage 包含 JA（ja / 日本語）、ZH_TW（zh-TW / 繁體中文 (台灣)）与 CAT（cat / 猫猫语），在 getLocale 与 isChinese 中完成标准映射（CAT 映射为 Locale("cat") 并获 Android 原生兼容支持）
    - 设置界面动态联动：GeneralSettingsSubPage 通用设置页面语言选择器完整接入跟随系统、简体中文、English、日本語、繁體中文与猫猫语 6 项语言切换选项
  - 多语言资源全量覆盖与校验:
    - 繁体中文（values-zh-rTW）：基于 opencc (s2twp 台湾术语规范) 全量转换 2992 条字符串，涵盖图层、笔刷、滴管、色彩增值、復原与重做等标准设计术语
    - 猫猫语（values-cat）：采用「自然萌系轻猫化」策略，保留核心专业绘画名词（画布、图层、笔刷、选区、滤镜、混合模式），重点在操作交互按钮、提示弹窗与状态反馈上融入软萌猫咪动作（好喵！、算啦、倒退一爪、重新抓一爪、藏好啦、叼进来、叼出去、一爪拍飞、改个名、分身等），杜绝机械句尾加喵与冗余括号，全量 2992 条字符串 XML 校验通过
    - 日语（values-ja）：基于 Krita 官方翻译记忆（po/ja/krita.po）结合 8 路特工分队并行精细化校验，严格对齐 Clip Studio Paint / Photoshop / Krita 日本标准 UI 术语并保证 100% 格式占位符 (%s, %d) 精度，全量覆盖 2992 条字符串
  - 开发规范更新与真机部署验证:
    - 项目级 AGENTS.md 更新第 6 节（编码规范）与第 13 节（发版流程），确立日常开发仅维护简体中文与英文、扩展多语言仅在大版本发版前或用户明确指示时全量增量补全的维护原则
    - testDebugUnitTest 全量单元测试全绿通过，assembleDebug 编译打包成功并已通过 ADB 静默安装至一加平板 2 Pro（c84b9192）真机运行验证
    - 修复 Android Lint 检查拦截：针对 CI 中 `:app:lintDebug` 将 debug 目录专用的未翻译性能标尺（PerfHud）文案及扩展语种缺失作为致命错误拦截（42 项 MissingTranslation 报错）的问题，在 app/src/debug/res/values/strings.xml 中为 resources 根标签添加 tools:ignore="MissingTranslation"，并在 app/build.gradle.kts 的 lint 配置块中增加 disable += "MissingTranslation"，彻底保障日常开发中无需同步全部扩展语种即可畅通通过 CI 自检与自动化构建（commit: d8b49160）
    - 代码已提交并推送到 GitHub 远端 main 分支（commit: d8b49160）

- **ReveriePaint-native 修复导入 KRA 工程无法识别继承透明度与图层组穿透模式 (2026-10-25, 完成)**:
  - 核心架构与底层解析修复:
    - 根治继承透明度与透明度锁定丢失：Krita 原生保存 .kra 时使用 channelflags 与 channellockflags 掩码位标识通道启用与锁定状态，官方不输出 inherit-alpha 属性；在 ReverieCoreIO.cpp 的 loadKraNodesDom 中接入通道掩码解析，当检测到 alpha 位禁用时自动激活 l->disableAlphaChannel(true)，当检测到 alpha 锁定未置位时激活 pl->setAlphaLocked(true)，并在写出 .kra 时补齐 channellockflags 序列化
    - 补齐图层组穿透混合模式：解析 passthrough/pass_through 属性与 pass_through 复合模式，同步注入 g->setPassThroughMode，并在写出 .kra 与 REVP meta.json 时补齐图层组 passthrough 状态回写
  - 单元测试与代码推送:
    - ClippingMaskLogicTest 补齐 KRA 继承透明度通道位解析与图层组穿透判定单测，testDebugUnitTest 全量测试全绿通过，代码已推送至 GitHub main 分支（commit: 1b0f5b13，关联 Issue #119）

- **ReveriePaint-native 支持设置中关闭双指与三指长按连续撤销与重做 (2026-10-25, 完成)**:
  - 架构与防误触状态机重构:
    - 根除手掌误触触发连续撤销：针对三星 Galaxy Tab 等大屏设备手掌边缘搭屏误触发两指/三指长按连撤连做导致画作被快速清空的问题，在 CanvasTouchView 的 continuousUndoRunnable 与 continuousRedoRunnable 任务执行入口及调度前置判断处增加 gestureContinuousUndo 状态门禁，关闭后彻底阻断长按连撤连做循环，仅允许轻点单击触发单步撤销/重做
  - 配置持久化与界面呈现:
    - PaintViewModel 引入 gestureContinuousUndo 响应式状态与持久化配置项，并在手势设置面板「辅助与画布控制」卡片中提供「长按连续撤销与重做」开关（默认开启），支持恢复默认手势时统一重置
    - 补齐 values 与 values-en 多语言文案定义
  - 单元测试与代码推送:
    - GestureConfigTest 补齐门禁逻辑测试，全量单元测试全绿通过，代码已推送至 GitHub main 分支（commit: 00258a26，关联 Issue #124）

- **ReveriePaint-native 移除系统 MotionPredictor 崩溃源与手写笔硬件 SDK 算法残留 (2026-10-25, 完成)**:
  - 核心架构与闪退根治:
    - 根除 C++ 底层 SIGABRT 闪退：定位到用户落笔绘制首笔崩溃栈为 libinput.so 中 android::MotionPredictor::record 触发 LOG_ALWAYS_FATAL_IF 并调用 abort()；彻底剥离 CanvasTouchView 中对 androidx.input.motionprediction.MotionEventPredictor (系统级预测器) 的全部声明、初始化与调用，落笔预测完全收口至纯 Kotlin 实现的 4 阶卡尔曼前向预测器 universalPredictor，杜绝非兼容硬件与第三方 ROM 上的原生 abort 闪退（commit: dcb5af0a）
  - 界面与设置逻辑精简:
    - 移除硬件 SDK 预测算法单选项：手写笔设置子页面（StylusSettingsSubPage）移除已失效的「硬件SDK算法」与「APP软件算法」单选组，触控与笔画预测分组项数收敛为 3 项；PaintViewModel 中 stylusPredictionMasterEnabled 与 updateStylusPredictionMaster 直接收口至超低延迟前向预测开关 frontBufferPredictionEnabled，彻底清除 stylusPredictionAlgorithmType 假代码（commit: e9aefad2）
  - 编译构建与代码推送:
    - testDebugUnitTest 全量单元测试全绿通过，代码已推送至 GitHub main 分支

- **ReveriePaint-native 通用与 Ugee/XP-Pen 手写笔双侧键映射与临时橡皮冲突修复 (2026-10-25, 完成)**:
  - 核心架构与侧键状态机重构:
    - 按键通道位掩码重构：彻底剥离 GenericStylusAdapter 与 StylusDriver.isSideButtonEraseActive 中对 MotionEvent.BUTTON_PRIMARY (1) 的误判定，消除笔尖接触屏幕被误当侧键按压的问题；接入 BUTTON_STYLUS_PRIMARY (32) 与 BUTTON_STYLUS_SECONDARY (64) 标准键位，并向下兼容数位板/EMR 鼠标兼容键位（下侧键对应 BUTTON_SECONDARY = 2，上侧键对应 BUTTON_TERTIARY = 4 / BACK = 8 / FORWARD = 16），解决 Ugee UT2PRO 与 XP-Pen 上侧键完全未被识别、下侧键错位为副键的问题
    - 临时橡皮笔画抑制逻辑纠偏：重构 strokeHappened 判定，仅在运笔时真实带压感 (pressure > 0.01f) 且位移超过 24px 时判定为临时橡皮笔画；松键时仅在开启按住侧键橡皮 (genericSideButtonErase) 且确实画过笔画时抑制动作，开启按键映射时悬空单击或轻触单击 100% 正常触发动作映射
    - 悬空离开与按键边沿派发加固：onStylusHoverExited 补齐抬笔释放判定，笔尖离开感应场时自动结算释放动作；在 CanvasTouchView 的 onHoverEvent、onGenericMotionEvent 以及 MainActivity.dispatchGenericMotionEvent 中完整下发 ACTION_BUTTON_PRESS 与 ACTION_BUTTON_RELEASE，静止悬空按压与释放动作不再漏判
    - 物理按键扩展识别与防抖：GenericStylusAdapter.onStylusKeyEvent 与 StylusDriver.isStylusKeyEvent 补齐 KEYCODE_BUTTON_A (96)、KEYCODE_BUTTON_B (97)、KEYCODE_BUTTON_3 (190)、304、305、310、311，并在 MotionEvent 与 KeyEvent 双通道间设置 150ms 防抖，杜绝重复触发
  - 测试构建与代码推送:
    - StylusModelsTest 补齐位掩码与扩展按键单元测试，testDebugUnitTest 与 assembleDebug 编译打包全绿通过
    - 代码提交至 main 分支并推送到 GitHub 远端仓库（commit: 06841d2b，关联 Issue #133）

- **ReveriePaint-native 面板固定跳变越界修复与笔刷橡皮切换快捷操作纠偏 (2026-10-25, 完成)**:
  - 核心架构与面板固定/平移统一容器重构:
    - 消除坐标系硬断裂跳变：原实现在钉住面板时将 AnimatedVisibility 的 modifier 切换为硬编码对齐与偏移（PaintingPage 中写死 CenterStart / TopEnd / BottomStart），且将内部卡片脱离外层 fillMaxSize 容器，丢失了 floatingUiConfig 的 toolRailPosition / topBarPosition / sliderRailPosition 动态对齐与 inwardMargin 内缩外边距；重构为 AnimatedVisibility 统一使用 fillMaxSize，三大面板（BrushPanel、LayerPanel、ColorPanel）内部容器统一维持 Box(fillMaxSize)，钉住时仅移除 noRippleClickable(onClose) 遮罩并登记 PINNED_* 孔径，保留完全相同的 baseAlign、basePaddingModifier 与 offset，彻底消灭钉住瞬间卡片瞬移数千像素的跳变
    - 自由平移拖拽越界钳位：在 DragPillHandle 的 onDrag 处理中接入 LocalConfiguration 屏幕宽高，将 brushPanelOffset、layerPanelOffset 与 colorPanelOffset 严格限制在 ±85% 屏幕尺寸内（coerceIn），彻底杜绝面板卡片被拖拽至屏幕可视区域之外
    - 取消钉住与面板关闭状态重置：统一在取消固定与面板关闭回调中重置 offset 为 Offset.Zero，并在 updatePanelPinningEnabled 关闭全局开关时级联清理色板固定状态与偏移
  - 笔刷与橡皮切换快捷操作纠偏:
    - 逻辑纠偏：PaintViewModel.executeQuickAction 中 TOGGLE_ERASER 原先在 eraser 状态下 fallback 到 applyTool(lastToolId.ifEmpty { "brush" })，导致套索、涂抹等工具切入橡皮后再切回时回退到上个工具，沦为「当前所选工具与橡皮切换」；修正为 eraser 状态下强制切换为 brush，非 eraser 状态下切换为 eraser，严格履行「笔刷与橡皮切换」
    - 文案与快捷键定义校正：同步修正 PaintViewModelShortcuts、values/strings.xml 与 values-en/strings.xml 中 toggle_eraser 的名称定义（画笔与橡皮切换 / Toggle Brush / Eraser）
  - 测试构建与多端验证:
    - 执行 testDebugUnitTest 单元测试全绿通过
    - assembleDebug 成功打包并通过 ADB 推送到一加平板 2 Pro（c84b9192）真机安装验证
    - 代码提交至 main 分支并推送到 GitHub 远端仓库（commit: dfa562b9）

- **红米 K60 ColorOS 16.1 (Baklava/ac68c1a) 脏刷更新与 SukiSU/隐匿生态无损继承 (2026-10-25, 完成)**:
  - 核心架构与固件刷写:
    - 完整性校验与纯净备份：新版固件 `ColorOS16.1_REDMIK60_ac68c1a_20261012.zip` MD5（`ac68c1a...`）校验无误，提取纯净原厂 `boot.img` 归档至 `~/刷机/k60/原厂备份/boot_20261012_clean.img`
    - 授权补丁脱壳：对 `VerificationPatchV2_20260914.zip` 清除中心目录伪加密标志位（0x0009 -> 0x0008），生成 `VerificationPatchV2_fixed.zip` 并推送至手机
    - TWRP 全自动刷写：手机重启至 TWRP，通过 ADB CLI 触发安装，自动模拟硬件按键 `VOLUMEUP` 确认 MD5、SukiSU Ultra 及定制 Recovery 部署，流式解压写入 `super.img.zst`，随后无缝安装授权验证补丁
  - 模块与防检测继承校验:
    - 系统成功进入 ColorOS 16.1（PLQ110_11_A.01 / AetherKernel 5.10.246），保留数据更新零丢损
    - SukiSU Ultra 4.2.0 (40900 / UAPI=2) 正常常驻
    - Zygisk Next 1.5.0 正常注入，`enforce_denylist` 维持 0，Vector 守护进程保持 `unshare -m`，Tricky Store 与 HMA 模块自然继承生效
    - 全面冻结系统 OTA 组件：已在红米 K60 与一加平板 2 Pro（100.107.36.2:5555）上将 `com.oplus.ota`、`com.oplus.cota`、`com.oplus.romupdate` 与 `com.oplus.upgradeguide` 全局及用户层级彻底禁用并清理缓存，双端彻底杜绝系统更新提示与后台静默下载

- **Tailscale 异地全端互联、通信共享无损分流与全自动无线 ADB 守护落地 (2026-10-24, 完成)**:
  - 核心架构与全端互联:
    - 电脑端（Linux CachyOS）：`tailscale` 安装并启用 `tailscaled.service`，绑定 IP 为 `100.73.79.77`，配置代理环境与 `--accept-dns=false` 彻底消除 DNS 冲突，授权 `lanrhyme` 无密码操作
    - 平板端（一加平板 2 Pro / c84b9192）：原生 ARM64 `tailscale` / `tailscaled` 部署至 `/data/adb/tailscale/`，认证上线绑定 IP 为 `100.107.36.2`
    - 手机端（红米 K60 / ed3fdd92）：静默安装官方 Tailscale App；部署原生 ARM64 二进制至 `/data/adb/tailscale/`，配置开机自启守护 `/data/adb/service.d/tailscaled.sh`，认证上线绑定 IP 为 `100.127.72.106`
  - ColorOS 通信共享与策略路由避坑重磅发现:
    - Netfilter 强力阻断避坑：Tailscale 默认的 `--netfilter-mode=on` 会在 `FORWARD` 链首部插入 `ts-forward` 丢弃非 `tailscale0` 的转发包，导致手机向平板共享蜂窝数据（`p2p0` -> `rmnet_data`）彻底断网；通过 `--netfilter-mode=off` 彻底清空防火墙链予以根治
    - 内核转发无 UID 陷阱：在 Linux 内核转发中，转发流量在某些路由阶段会被内核视为 uid 0，导致早前添加的 `uidrange 0-0 pref 4800 lookup $IFACE` 将互联网回给平板的包误路由回外网形成路由环路；彻底移除 rule 4800 并改用最高优先级 `pref 4700 to 100.64.0.0/10 lookup 52`，使 Tailscale 流量优先直入 WireGuard 隧道，其余流量自然走系统原生策略路由，通信共享与内网直连 100% 完美共存
  - 全自动无线 ADB 守护体系 (PC + 手机/平板双端自启):
    - 移动双端自启开机监听：红米 K60 与一加平板 2 Pro 均部署 `/data/adb/service.d/adbd-tcp.sh`，开机自动执行 `setprop service.adb.tcp.port 5555 && setprop ctl.restart adbd`，监听本地 `0.0.0.0:5555`
    - 双端开机分流优化：两台移动设备 `/data/adb/service.d/tailscaled.sh` 均配置 `--netfilter-mode=off` 与 `pref 4700 to 100.64.0.0/10 lookup 52`，平板配合 `iif lo uidrange 0-0 pref 4800` 动态绑定默认出口，实现蜂窝共享/Wi-Fi/Tailscale 零冲突
    - 电脑端后台守护与自启：编写 `~/.local/bin/adb-autoconnect.sh` 并配置 `~/.config/systemd/user/adb-autoconnect.service`，随电脑开机登录自启；轻量探测 `100.127.72.106:5555` 与 `100.107.36.2:5555`，一旦设备上线或进入网络自动执行 `adb connect`，两台设备均完全脱离 USB 数据线
  - Tailscale Serve 服务化注册 (Services 目录激活):
    - 官方服务注册：通过 `tailscale serve --bg 8787` 与 `tailscale serve --bg --https=5000 5000` 将 NyanoMuse 云端服务 (`:8787`) 与 Dufs WebDAV 文件服务 (`:5000`) 分别挂载至 Tailscale Serve 目录
    - 控制台服务呈现：服务正式在 Tailscale Admin Console 的 **Services** 目录上架显示，内置获得原生 HTTPS 反向代理支持
    - 双轨访问矩阵：对端既可通过 `tailscale.lanrhyme.top:8787` 与 `tailscale.lanrhyme.top:5000` 直连，亦可通过 Tailscale 官方虚拟服务域名无缝协同
  - 互通验证：
    - 平板端与手机端均成功与电脑双向通信（`ping 100.73.79.77` 0% packet loss），且电脑通过 Tailscale 同时稳定挂载 `100.127.72.106:5555` 与 `100.107.36.2:5555` 双端无线 ADB
    - 平板端直连请求 `http://tailscale.lanrhyme.top:8787/healthz` 响应正常（`ok: true, version: 0.26.0`），彻底摆脱公网 DNS/CDN 波动与校园网隔离限制

- **Antigrative Dashboard、Brain Visualizer 与 Link 扩展部署 (2026-10-24, 完成)**:
  - 核心架构与多端安装:
    - 仓库归档：源码归档至 `~/.local/share/antigrative-dashboard`
    - 桌面端插件：安装至 `~/.gemini/config/plugins/antigravity-pulse`，运行时模式挂载成功（已连接活动渲染窗口）
    - CLI 状态栏：通过 `manage.py install-cli --language zh-CN` 配置于 `~/.gemini/antigravity-cli/settings.json`，支持上下文、缓存率与额度监控
    - Brain Visualizer：下载并解压官方最新 v0.7.1 二进制，部署至 `~/.local/bin/agy-brain-viz`，支持可视化检查本地 `~/.gemini/antigravity/brain/`
    - Antigravity Link：下载最新 v1.0.20 VSIX，成功安装至 VS Code 扩展（`cafetechne.antigravity-link-extension`）
  - 运维与状态校验：
    - `python3 manage.py status` 与 `python3 manage.py status-cli` 校验均已正常 enabled
    - `agy-brain-viz --version` 与 `code --list-extensions` 均校验通过

- **NyanoMuse 跨端生图授权安全门与双轨情绪标签复制泄漏修复 (2026-10-23, 完成)**:
  - 核心架构与安全分级加固:
    - Hub 跨端生图授权安全门：将 image.generate 纳入 GATED_ACTIONS，杜绝免批准调用桌面端能力，未获用户授权前无法执行
    - 路径穿越防护与参数规范化：image_name 实施严格白名单正则校验（^[A-Za-z0-9_-]{1,64}$），移除 subprocess.run 中无效的单引号转义并采用 json.dumps 规范编码，防止自然语言提示注入与路径穿越
  - 双轨情绪闭环与选区复制防漏:
    - 选区复制标签泄漏根治：在 ChatFlatItems.buildFlatChatItems 入口处统一对助手消息正文与工具块执行 mood 标签剥离，根治跨代码块选区复制时剪贴板携带 nm:mood 标签的问题
    - 心境反哺提取顺序纠偏：ChatViewModel 调整情绪反馈提取顺序为本轮文本 turnText 优先于跨轮累积文本
    - 讽刺检测增量保留与互抑上限微调：CompanionMoodStore.applyFeedback 调准 suppressCap 为 1.5f，并在反哺时保留端侧检测到的讽刺生闷气增量（当端侧检测到讽刺且模型误判为开心得意时保留 50% 生闷气增量）
  - 测试与全平台构建验证:
    - CompanionMoodStoreTest 补齐讽刺保留单测，安卓全量 1762+ 项单元测试全绿通过
    - Python 端 test_coding.py 15 项测试全绿通过
    - assembleDebug 成功编译打包生成 57MB debug APK
    - 桌面端 harness 重新编译构建并同步部署至 ~/.local/opt/nyanomuse/

- **NyanoMuse 编程工具集成 Antigravity 与移动端跨端 agy 生图体系落地 (2026-10-23, 完成)**:
  - 核心架构与桌面端 Antigravity 接入 (nanomuse/coding & harness/dsh-nanomuse):
    - 运行时 5 代理支持：Python 端 `nanomuse/coding/agents.py` 与 TypeScript 端 `coding-readers.ts` 新增 `antigravity`，定义 `bins=("agy",)`、`process=("agy", "antigravity")`，动态索引 IDE 目录 `~/.gemini/antigravity` 与 CLI 目录 `~/.gemini/antigravity-cli` 下 `conversation_summaries.db` SQLite 索引数据库与 `transcript.jsonl` 会话流
    - 代理执行与事件归一化：`runner.py` 与 `coding-runner.ts` 接入 `agy --output-format stream-json --dangerously-skip-permissions`，并将 `agy` 的 `step_update` (text_delta)、`tool_call` 与 `state=DONE` 精准归一化为统一 coding 流程流式事件
    - Hub 生图动作注入：`nanomuse/hub/actions.py` 与 `harness/dsh-nanomuse/src/actions.ts`、`cloud.ts` 注册并实现 `image.generate` 动作，调用 `agy` 工具并解析 `file://...` 或 `brain/<cid>` 图片输出，封装 Base64 与多媒体元数据返回，并接入桌面端 Toast 提醒
  - 移动端双模触发与生图大图卡片交互 (Android):
    - 伴生体自主工具注入：`NativeSystemTools` 新增 `TOOL_IMAGE_GENERATE = "image_generate"` 工具定义与执行逻辑，自动探测 Hub 在线电脑设备并分发 `image.generate`，返回图片二进制并保存至 `context.filesDir/generated_images`
    - 手动 Slash 命令分发：`ChatViewModel` 接入 `/image <prompt>` 与 `/draw <prompt>`，自动装配并展示带加载状态的生图卡片，生成完成后将图片注入聊天气泡与流式 markdown 中
    - 交互式图片卡片操作面板：`ChatToolDetailUI` 与 `ChatToolFormatting` 为 `image_generate` 挂载预览卡片，提供「设为壁纸」（联动 `ChatWallpaperManager` 动态应用为全局莫兰迪壁纸）与「保存相册」（通过 `MediaStore` 写入公共相册）快捷动作
  - 编译测试与多端部署验证:
    - Python 端 `pytest tests/test_coding.py` 15 项单测全绿通过
    - 桌面端 harness `pnpm run build && pnpm test` 全量 359 项单测全绿通过，并同步部署至 `~/.local/opt/nyanomuse/`
    - 移动端 `testDebugUnitTest` 单元测试通过，`assembleDebug` 打包成功并通过 ADB 成功安装至红米 K60 (ed3fdd92) 与一加平板 2 Pro (c84b9192) 真机

- **NyanoMuse 移动端交互式终端与命令执行原生 Root 与 Host 模式深度适配 (2026-10-23, 完成)**:
  - 核心架构与交互式终端解绑 PRoot 容器:
    - 交互式终端 TerminalSession 执行模式动态路由：移除开机硬编码强制检查与启动 PRoot 容器的限制，根据用户在设置中选择的 ExecutionMode（ROOT、HOST_SHELL、PROOT_SANDBOX）分流；在 Root 模式下动态探测 su 路径（/system/bin/su、/system/xbin/su、/sbin/su、/data/adb/ksu/bin/su 等），PTY 直接以 root 环境变量（PATH 包含系统与 su 工具链、HOME=/storage/emulated/0、SHELL=/system/bin/sh 等）启动原生 root shell；在 Host 模式下直接启动 /system/bin/sh -i 原生宿主终端；在 PRoot 模式下保留既有 Alpine 容器沙箱启动流
    - 路径切换与鉴权提示保护：消除进入终端后硬编码 cd /var/minis && clear 导致的安卓宿主报错，仅在 PRoot 沙箱模式下执行容器路径切换，Root/Host 模式下工作目录默认指向 /storage/emulated/0 或会话专属目录；su 启动失败或权限被拒时在 PTY 终端内输出清晰的授权引导提示
  - 单次与后台命令执行及依赖检测适配:
    - ShellExecutor 单次与后台执行解耦：ShellExecutor 新增 executeHostOrRoot，在非 PRoot 模式下通过 ProcessBuilder 调用 su -c 或 sh -c，执行前跳过 PRoot 容器启动检查
    - 按需 Bash 检测适配：OnDemandBash 仅在 PRoot 容器内尝试执行 apk add bash，在 Root 与 Host 模式下直接探测宿主是否存在原生 bash，消除缺失 apk 命令导致的崩溃抛错
    - Hub 动作守护：HubActions.boot 仅在 ExecutionMode == PROOT_SANDBOX 时才触发 PRoot 容器启动
  - 界面呈现与模式切换联动:
    - 状态徽标与标题联动：TerminalScreen 顶部栏根据当前活跃模式动态展示 nanoMuse Shell (Root)、(Host) 或 (PRoot)
    - 切换模式生命周期终止：在设置界面（SettingsScreen）更改执行模式时，立即通过 ExecutionCoordinator.stopCurrentCommand 终止旧模式下的持久化 Shell 会话
  - 测试与真机部署验证:
    - 新增 ExecutionModeTest 覆盖各种执行模式判定与分支逻辑，单测全绿通过
    - assembleDebug 成功编译打包并通过 ADB 静默安装至红米 K60（ed3fdd92）真机
    - 提交记录 48f80a14 与 7537c03f

- **NyanoMuse 伴侣 33 种心境体系与双出口情绪感知面板落地 (2026-10-23, 完成)**:
  - 核心架构与 33 种心境分值引擎 (参考 dsh-mood):
    - 三层心境枚举与基线空间：新建 CompanionMoodStore，定义基础 11 种（CALM、HAPPY、CURIOUS、FOCUSED、EXCITED、TIRED、ANNOYED、DOWN、FEAR、DISGUST、SURPRISE）、复合 18 种（HURT、SULK、PROUD、GLOOMY、ANXIOUS、NUMB、LONELY、FLUTTER、LOVE、JEALOUS、SHAME、GUILT、AWKWARD、SYMPATHY、DISAPPOINTED、NOSTALGIA、COY、CONFLICT）、当代 4 种（BURNOUT、CRACKED、CHECKEDOUT、HYPER），每种配置独立自然基线分值（0~100）与行为倾向
    - 讽刺过滤与反向压制矩阵：detectSarcasm 提前拦截阴阳怪气与反讽用语，剔除「真厉害啊」「真行啊」等高频真诚夸奖误判词，压制误判并精准识别讽刺并转向委屈生闷气；judgeMessage 对用户输入进行意图识别并应用微调（±0.5~3.5），深度融合心理反向压制逻辑（真诚夸奖增加得意/开心/恋慕/撒娇并消解生闷气/委屈/烦躁，晚安睡眠强化困倦恬静，冷淡打发增加生闷气，摆烂内耗压制焦虑与防御，破防增加委屈低落并抑制烦躁火气）
    - 昼夜节律与周期衰减闭环：circadianOffset 动态注入深夜自然困倦与清晨活力，并与持久化主导心境判定解耦（仅参与分值与混合态 secondary 计算，不侵蚀带防抖和保持期的 primary）；checkPeriodicDecay 接入 ChatViewModel 与 CompanionAlarmReceiver 每 3~6 小时定期将分值以确定性微抖动回落至基线；sessionTurns 与 sessionErrors 记录单会话回合与错误疲劳
    - 大模型真实情感反哺与双轨去重闭环：建立端侧定「量」与模型定「义」的分工体系，支持大模型在回复末尾通过 <nm:mood feel="id" reason="..."/> 表达真实情感触动；applyFeedback 自动撤销端侧本轮临时预判增量以彻底消除双轨重复计数，并由客户端 FEEDBACK_DELTA 标定增量克服大模型自正面偏差与跨模型漂移；互抑总量硬封顶 <= 2.0；模型理由作为 modelNarrative 仅供仪表盘呈现而绝不回灌进入 prompt；权威落库点集中剥离并在桌面端 RemoteBubbles 增加兜底清洗
    - 防抖切换与混合态计算：主导心境切换要求分值高出原主导 >= 5 分且维持 >= 15 分钟（或单次跃迁分值差 >= 15 分），消灭心境频繁跳跃抖动；次高心境与主导心境分值差距 < 8 分时判定为混合气味共存并在标题体现
    - 客观事实切片与旧链清理：记录最近心境切换的时间戳、原始心境、目标心境与触发用户话语片段，严格以伴随客观事实呈现，避免生硬机械归因；彻底清理 ChatViewModel 中旧有的 appraiseUserTurn/impulseForAct 与 dynamic_bias 死代码
  - 危机安全硬线守护 (DistressGuard):
    - 绝望自伤敏感词硬线匹配：自杀、自残、割腕、想死、不想活了、撑不下去了等多字显式模式严格拦截，命中后激活 30 分钟硬线守护
    - 角色让位与通用心理热线支持：DistressGuard.safetyOverridePrompt 强制模型收起所有傲娇、戏谑与角色扮演表演，以沉稳克制温暖的语气提供陪伴并通用引导寻求当地心理援助热线与危机干预公共渠道，彻底移除硬编码电话号码
  - 提示词双出口与头像定制动效:
    - 深度思考内心戏与回复语气双出口：ChatViewModel.buildSystemPrompt 注入内心戏指引，要求在 think 深度思考流露真实小反差内心 OS，正式回复语气自然渗透心境倾向但严禁自报分值数值
    - 提示词黄金自检与易混情绪辨析指引：在 CompanionMoodStore.promptAddendum 注入三条黄金自检法则（换个人成立吗/替对方编了吗/姿态当内容了吗）、5 组易混情绪辨析（烦躁/生闷气、麻木/摆烂、焦虑/内耗、破防/吵架、兴奋/上头）、做不到的未来与同理心克制界限，以及极端痛苦自伤求救角色让位硬线；单测 testPromptAddendumQualityAndConstraints 全绿
    - 头像动效扩充：AgentAvatar 扩充支持 SULK_JEALOUS（生闷气微颤背身）、CRACKED_HURT（委屈缩紧低头）、HYPER（上头高频弹性跳跃）专属动效，其余 30 种心境优雅归入 8 大动效家族
  - 心境罗盘半屏仪表盘 (MoodDashboardSheet):
    - 交互式面板：直观展示当前主导心境、混合态气味、最近转移客观事实与回合信息、33 种心境分类（全部/基础/复合/当代）实时分值进度条与基线刻度，支持一键重置回基线分值
    - 双入口接入与深度多语言：主聊天顶栏副标题胶囊点击直接滑出 MoodDashboardSheet；伴侣设置界面（CompanionSettingsSheet）内响应式监听 emotionVersion 实时联动；状态胶囊与仪表盘文案全量接入 17 语种国际化
  - 全语言多端与自动化测试:
    - 17 种语言完整补齐心境名称、仪表盘、倾向、共存与转移事实等 19 个新 key 并通过 NmStringsParityTest 严格校验
    - CompanionMoodStoreTest 覆盖 33 种心境初始化、真诚夸奖不误判、讽刺拦截、昼夜节律、分值夹持、反向压制、防抖门槛、混合态共存、周期回落、重置基线以及安全硬线单测，全量通过
    - assembleDebug 编译打包成功

- **NyanoMuse 伴侣主动聊天历史上下文丢失与重复早安缺陷修复 (2026-10-23, 完成)**:
  - 核心架构与并发加载竞态修复:
    - 历史会话异步加载竞态消除：定位到 HeadlessChatRunner 在触发主动提问时仅等待 activeEntryId 就立即调用 sendMessage，此时 ChatViewModel 的 loadSession 仍处于 IO 线程解析 Room 数据库消息阶段，导致 sendMessage 抓取到的 agentHistory 为空，模型在零历史上下文状态下输出；通过在 ChatViewModel 暴露 isSessionLoaded 并在 sendMessage 协程开头执行 sessionLoaded.first { it }，同时在 HeadlessChatRunner 显式等待 isSessionLoaded，彻底杜绝历史消息加载与发送的并发竞态
    - 历史上下文完整性双重守卫：ChatViewModel 在 runAgentLoop 前置增加防御校验，若 agentHistory 仅包含当前新回合但数据库历史消息数量大于 1，自动从数据库重构 agentHistory，保证模型永远携带完整上下文
  - 伴侣情绪与早安意图防重逻辑优化:
    - 活跃互动场景优先守护：CompanionEmotion.evaluate 将 idleMs < 1h 的 FRESH_RESONANCE 判定前置，只要用户在 1 小时内有过真实对话，强制保持低意愿（proactiveScore = 0.15f）与静默陪伴，杜绝刚聊完天又被后台主动打扰
    - 早安问候每日单次与已互动豁免：引入 hasGreetedMorningToday 标志位与今日 06:00 起已有互动的拦截校验，用户今早打过招呼或已发送过早安后，同一自然日绝不再触发 MORNING_GREETING，而是平滑流转为 CALM_COMPANION 或 CURIOUS_CHECKIN
    - 主动提问频率真实用户消息守卫：CompanionPrefs.checkCanTrigger 增加 lastRealUserMessageTime 冷却校验，用户 1 小时内发言时阻断后台主动探访
    - 上下文延续引导增强：RoutineWakes.armCompanion 注入 Context Continuity 指令，明确要求伴侣结合前文自然承接已有对话，严禁机械重复打招呼
  - 测试与构建验证:
    - CompanionEmotionTest 补充早安前置活跃、已问候流转与今早已有互动防护单测，全部通过
    - assembleDebug 构建打包成功

- **NyanoMuse 多端同步时延极限压缩与重连秒级增量补偿落地 (2026-10-22, 完成)**:
  - 核心架构与同步链路时延优化:
    - 移动端人工延迟消除：ConversationSync 中 PUSH_DELAY_MS 由 2000ms 压缩至 200ms，TURN_END_SETTLE_MS 由 1500ms 压缩至 200ms，消灭单次回合结束后长达 3.5s 以上的人工滞后，WAL 落盘即刻触发推送
    - 前台自愈轮询提频：PULL_EVERY_MS 从 60000ms 优化至 15000ms，前台活跃期 15 秒快速自愈兜底，退后台自动停止轮询保持零耗电
    - 会话切入即时拉取：ChatScreen 挂载 LaunchedEffect(sessionId)，切换或进入会话时经 200ms 触发 ConversationSync.pullSoon，消灭进会话等待广播帧的时差
    - Hub 重连秒级全量补偿：HubClient 在 onState 变为 true（WebSocket 重连并握手完成）时立即调用 ConversationSync.syncSoon 与 FeedSync.triggerSync，彻底解决移动端锁屏休眠唤醒后漏广播导致的旧数据死区
    - 桌面端多端参数对齐：harness/dsh-nanomuse/src/sync.ts 同步调整 PUSH_DELAY_MS 与 FRAME_COALESCE_MS 为 200ms，PULL_EVERY_MS 调整为 15000ms，重新构建 lib 并同步部署至 ~/.local/opt/nyanomuse/ 运行时目录
  - 测试与多端部署:
    - 桌面端 pnpm test 全量 359 项单测全绿通过
    - 移动端 testDebugUnitTest 单测通过（io.github.nanomuse.sync.* 全绿）
    - assembleDebug 编译通过，并通过 ADB 成功静默安装至一加平板 2 Pro（c84b9192）与红米 K60（ed3fdd92）
    - 桌面端后台进程 nyanomuse-desktop 平滑重载

- **NyanoMuse 代码块超长折叠交互优化与伴侣全功能环境感知体系落地 (2026-10-22, 完成)**:
  - 核心架构与代码块视口折叠:
    - 行数阈值自适应折叠：StreamingMarkdownText 与 MarkdownText 实现超长代码保护，代码行数大于 12 行时自动折叠，仅保留前 5 行代码预览并在底部覆盖垂直渐变阴影，提供「展开全部 (共 N 行)」按钮；展开后顶部工具栏右侧常驻收起图标，长代码底部提供轻量收起手风琴，右上角常驻一键复制代码并带触觉震动与对勾反馈
    - 流式打字视口稳定守卫：通过 LocalIsStreaming 与 LocalLiveIncremental 动态感知流式输出阶段，正在生成打字中的代码块保持展开状态，彻底杜绝打字过程视口高度抖动
    - 全语言本地化与视口一致性：17 种国际化语言补全展开与收起文案，通过 NmStringsParityTest 严格校验
  - 伴侣环境感知工具链与主动迎候引擎:
    - 原生前台应用感知工具 foreground_app：NativeSystemTools 新增 TOOL_FOREGROUND_APP 只读工具，通过 Root 模式 dumpsys window mCurrentFocus 解析当前前台应用包名与 Activity，并转换为用户友好的应用标签（如哔哩哔哩、微信、QQ、游戏等）；非 Root 环境接入 Accessibility 与 ActivityManager 降级回退；附带当前电量、充电状态与系统时刻
    - 阶梯式感知架构：RoutineWakes.armCompanion 提示词注入环境感知引导，伴侣可自主先调用 foreground_app 或 device_info 感知用户动态，若需深入理解屏幕画面（如游戏战局、视频、代码报错）再自主按需调用 screen_capture 截图并通过视觉通道深度解析
    - 双重主动触发流与冷却防打扰：ChatScreen 挂载主聊天时接入前台迎候（Foreground Greeting），离开应用超过 30 分钟重新进入时，伴侣自动感知当前上下文并发出亲昵开场白；后台关怀每日上限 3~5 次并遵循夜间免打扰策略
  - 测试与真机部署:
    - NmStringsParityTest 国际化单测与 CompanionEmotionTest 单测全绿通过
    - assembleDebug 编译打包成功并已通过 ADB 静默安装至红米 K60（ed3fdd92）与一加平板 2 Pro（c84b9192）

- **NyanoMuse 桌面端真实动态同步打通与全页面全局壁纸背景透视落地 (2026-10-22, 完成)**:
  - 核心架构与桌面端动态通道修复:
    - 桌面端 DSH 扩展注册与广播：定位到电脑端实际运行的 Electron DSH 插件 harness/dsh-nanomuse/src/cloud.ts，此前未在 actions 声明 feed.posts 与 feed.activity 导致对端无法发现；在 actions() 注册这两项并在 Service.init 中挂载处理函数，直接读取 rooms.json 中的真实动态（400+ 行）与 activity 返回，重新构建 lib 并部署到运行时目录，重启 DSH 后台服务生效
    - 移动端多变体时间戳与日期容错解析：FeedSync 适配 rooms.json 的 at 毫秒时间戳字段（兼容 created_at、ts 与 at），若 day 为空自动格式化为 yyyy-MM-dd；目标设备选择策略优化，兼顾 online 状态与 actions 列表
    - 用户操作反馈与 Hub 状态监听：triggerSync 支持 userInitiated 模式，在手动同步成功或失败时通过 Toast 即时反馈导入条数与总数；FeedTab 监听 Hub.connected 与 Hub.devices，当设备上线时自动触发后台增量同步；FeedTab 接入 Material3 PullToRefreshBox 原生下拉刷新手势，随手下拉即可触发全量同步
  - 全页面全局壁纸背景与通透磨砂层级:
    - 根级壁纸容器 AppWallpaperBackground：封装对 ChatWallpaperManager 路径、高斯模糊与暗色遮罩的实时监听，通过 LocalHasAppWallpaper CompositionLocal 向全应用提供壁纸状态
    - 全页面透明化与卡片磨砂效果：修改 MainActivity 将 AppNavigation 包裹在 AppWallpaperBackground 中；AppNavigation 根级 NavHost modifier 设置透明背景消除对底层壁纸的遮盖；NanoMuseHome 非会话页外层 Surface、FeedTab、IdeasTab、GoalsTab、LibraryTab、SettingsScreen、SettingsScaffold、AvatarStudioScreen 与 AgentProfileScreen 的底层背景在存在壁纸时自动设为透明；MuseCard、FeedCard、Segmented 控件采用 0.88 混合半透明微磨砂质感，让壁纸在全应用通透沉浸呈现
    - 会话页去重：ChatScreen 接入 LocalHasAppWallpaper，移除自身多余的壁纸二次解码与模糊渲染，与全局底层壁纸无缝衔接且零闪烁
  - 构建与真机部署:
    - assembleDebug 构建通过，并通过 ADB 成功安装至红米 K60（ed3fdd92）
  - 提交记录 95be5bb9、36280c3b 与 7c99eedf

- **NyanoMuse 伴侣情绪夜间锁死修复与顶栏头像 8 情绪专属微动效落地 (2026-10-22, 完成)**:
  - 核心架构与情绪流转修复:
    - 夜间与静默时段活跃对话感知：CompanionEmotion.evaluate 引入 isActivelyEngaged = idleMs < 30min 判断，用户在 21:30~22:59 晚安关怀时段与 23:00~08:00 静默时段仍在前台活跃对话时，不再无条件锁死为困倦 SLEEPY，而是正常进入欢快活跃心境 FRESH_RESONANCE
    - 日常闲聊正向心境保持：blendWithAsymmetricDecay 中 CASUAL_CHAT 在活跃衰减期保持 PrimaryMood.HAPPY，消灭此前因价态门槛过高而频繁跌回夜间困倦状态的问题
    - 对话意图识别词库扩充与时间戳剥离：appraiseUserTurn 前置通过 BubbleTimeFormatter.stripUserPromptTimestamp 清洗尾部注入的提示词时间戳，扩充涵盖「可以可以」「好耶」「帮我看看」等高频日常口语词典，并增强闲聊打趣的愉悦冲量
    - 响应式状态流与即时通知：CompanionStatus 增加 emotionVersion: StateFlow<Long>，在 recordEmotionImpulse、recordLastRealUserMessageTime 以及情绪开关与强度调整时立即自增通知；ChatScreen 将其接入 remember key，彻底终结此前 60 秒轮询导致的状态迟钝
    - 发送即时感知：ChatViewModel 在用户点击发送与注入排队回合瞬间即刻执行意图与冲量计算，顶栏头像与状态秒级响应，模型提示词组装时直接读取最新情绪
  - 头像多维专属微动效系统:
    - 瞬时弹性入场动效：AgentAvatar 监听 companionMood，8 种情绪切换时分别触发定制弹簧与关键帧动画（EXCITED 活力跳跃、HAPPY 欢快双跳、TOUCHED 温暖双心跳脉冲、SHY 害羞歪头微红、CURIOUS 竖耳探头向上、SLEEPY 困倦低头、CARING 温柔关切侧倾、LONGING 依恋思念延展）
    - 差异化呼吸与位移节奏：针对不同情绪定制呼吸周期（EXCITED 1200ms、HAPPY 2000ms、CARING 2800ms、SLEEPY 3600ms）与微悬停位移幅度，实现生动细腻的伴侣级互动感
  - 自动化测试与构建:
    - CompanionEmotionTest 补充夜间活跃对话、晚安关怀活跃豁免与时间戳清洗单测，全量通过
    - assembleDebug 编译通过
  - 提交记录 45cdccc9

- **NyanoMuse 手机平板与电脑动态跨端同步与活动流展示落地 (2026-10-22, 完成)**:
  - 核心架构与跨端同步流打通:
    - 电脑端 Hub 动作扩展：nanomuse/hub/service.py 在 _extra_actions 注册 feed.posts 与 feed.activity 动作，并在分发调度器中对接 svc.feed_posts 与 svc.feed(limit)，打通电脑向移动端输出每日早报与后台离开期间活动流的能力
    - 移动端存储与持久化去重落盘：FeedStore 引入 RemotePost 数据结构与 importRemotePosts 方法，按日期分目录落盘 markdown 文件并按标题不区分大小写去重，完成后自动触发 reload 与 prune
    - 移动端 P2P 同步单例：新建 FeedSync 单例，封装 sync 与 triggerSync，自动识别 Hub 在线电脑设备并并发拉取 feed.posts 与 feed.activity，解析后台任务、文件产出与通知事件；同时提供 handleLocalPostsCall 响应对端设备的动态请求
    - 动态广播与静默唤醒：ConversationSync 在 Hub 接收到 what == "feed" 的广播同步帧时，自动唤醒 FeedSync.triggerSync 执行增量拉取
    - 移动端 FeedTab 视觉呈现与活动流展示：FeedTab 监听 FeedSync.activities 与 isSyncing，在进入动态页时自动触发静默同步；新增 While you were away（在你离开期间）活动卡片流与分类图标、相对时间戳与一键跳转所属会话能力；空白状态与设置弹窗中增加从电脑同步动态操作入口与进度指示器
    - 国际化文案支持：nm_strings.xml 与 values-zh 补齐在你离开期间、从电脑同步动态与正在同步动态等词条
  - 构建验证:
    - assembleDebug 编译打包通过，生成 57MB debug APK
  - 提交记录 871dc73a

- **NyanoMuse 手机端侧边栏 UI 重构与主导航移入抽屉落地 (2026-10-22, 完成)**:
  - 核心架构与交互重构:
    - 聊天界面全屏纯粹化：彻底移除手机聊天页面底部悬浮的 MuseBottomBar，输入框（Composer）自然贴近屏幕底部手势线，为聊天消息流腾出完整的纵向空间，nmBottomOverlay 设为 0dp
    - 侧边栏顶部功能导航：在侧边栏顶部伴侣名字下方，集成自适应横向 5-Tab 胶囊导航栏（聊天、动态、灵感、目标、知识库），点击平滑切换并自动收起抽屉，全应用支持边缘滑动呼出侧边栏
    - 侧边栏结构精简与重排：主聊天卡片使用低饱和微透明卡片与高亮边框替代生硬黑底，搜索栏移至全部会话列表正上方支持即时过滤与一键清空，底部移除重复新建按钮与挤压搜索框，仅保留精致清爽的设置与文档入口
  - 构建与真机部署:
    - assembleDebug 编译通过，并通过 ADB 静默安装至红米 K60（ed3fdd92）
  - 提交记录 fec910a7

- **NyanoMuse 伴侣多气泡切分提示词强引导与容错解析增强 (2026-10-22, 完成)**:
  - 核心架构与提示词引导增强:
    - 纯指令式提示词与边界规约：重构 bubbleFlowAddendum，摒弃冗长示例与弱语气英文，替换为极简纯中文直接指令，明确日常闲聊拆分 2~3 个短气泡及代码技术严禁切分的场景边界
    - 容错正则解析下沉：BubbleTimeFormatter 引入 BUBBLE_REGEX（忽略大小写，兼容带空格如 <nm:bubble /> 与变体），ChatFlatItems 与 ChatRepository 全面接入，杜绝因轻微语法差异导致漏切分
    - 气泡文本首尾清洗：ChatFlatItems 切分后执行 trim() 清洗，消除分段产生的换行与空白，保证自适应单行与时间戳测算精确生效
    - 流式节奏解耦全局支持：解除流式打字停顿对 isMain 的硬编码限制，只要出现气泡切分标签即触发 450ms 拟人停顿
  - 自动化测试与真机部署:
    - 507 项单元测试全绿通过，assembleDebug 编译打包通过，并通过 ADB 静默刷入平板（c84b9192）与手机（ed3fdd92）

- **NyanoMuse 消息列表自适应分页加载与历史静默预加载落地 (2026-10-22, 完成)**:
  - 核心架构与无感分页机制:
    - UI 视图层自适应分页（UI Windowing）：超长会话初次进入仅加载最新 60 条消息，大幅减少初始 FlatChatItem 构建与 Markdown 解析节点，彻底根除深层嵌套导致的内存峰值与 OOM 隐患；底层 agentHistory、LLM 上下文滑动窗口与 SQLite 数据无损完整保留
    - 动态增量视窗模型：以 initialSessionMessageCount 锚定历史基数，新发送与实时接收的新消息动态追加视窗容量，杜绝传统 takeLast 导致旧消息被挤出视口的吞消息隐患
    - 接近顶部静默无感预加载：通过 snapshotFlow 动态监听 LazyColumn 触顶距离（距顶部不超过 8 项时自动触发），无感后台递增 40 条历史，节流防抖平滑无跳变
    - 极简双态顶部指示器：存在更早历史时展示 16dp 微型转圈与「正在加载更早历史…」，加载完毕且会话超过 60 条时展示低饱和「已加载全部历史消息」极简文本
  - 自动化测试与构建验证:
    - 安卓端全量 505 项单元测试通过，assembleDebug 编译打包通过

- **NyanoMuse 顶栏纯余额胶囊展示、阶梯式全量预热与长会话滚动极致性能优化 (2026-10-22, 完成)**:
  - 核心架构与长对话滚动性能重构:
    - 顶栏纯余额胶囊：DeepSeekStatus displayText 精简移除「今日花费」，仅显示「¥余额」，极简紧凑且点击仍完整呼出 Token 消费详情面板
    - 渐进式二级 Markdown 预热（Two-Tier Prewarming）：ChatScreen 彻底打破原有 16 条视口限制，Tier 1 优先后台预热首屏 16 条保证冷启秒开，Tier 2 在后台以 yield 协程协作模式分批预热全量剩余历史消息，彻底消除长会话向上飞抛滚动时的冷解析预览闪烁、动态高度跳变与布局抖动
    - 自适应气泡 O(1) 零开销测算：ChatBubbleAdaptiveLayout 引入先验水平宽度校验，并通过 FirstBaseline == LastBaseline 原生判断单行，彻底消除滚动期间对 measurables[0].minIntrinsicHeight 的重复二次测量遍历开销，消息气泡追加 50 字快速短路保护
    - 冷解析日志去噪限频：StreamingMarkdownText 仅对超过 15ms 的重型解析输出日志，消灭滚动期间持续磁盘 I/O 开销
  - 自动化测试与构建验证:
    - 安卓端全量 505 项单元测试通过，assembleDebug 编译打包通过

- **NyanoMuse 跨端多气泡形态统一、列表预览过滤与时间戳清洗下沉 (2026-10-22, 完成)**:
  - 架构统合与端到端闭环:
    - 跨端多气泡形态一致性：Transcript.kt 恢复保留同步文本中的 `<nm:bubble/>`，RemoteBubbles.ts 桌面端实现多气泡分割（上限 3 气泡）并注入自适应圆角与纵向间距，实现手机端与桌面端完全一致的拟真多气泡流式视觉
    - 会话列表预览全链路清洗：ChatRepository.cleanPreview 过滤 `<nm:bubble/>` 为空格，桌面端 ui.plain 同步清洗，会话列表与搜索预览绝不泄漏分隔符
    - 时间戳与字符串工具下沉解耦：BubbleTimeFormatter 集中管理 NM_BUBBLE_TAG、BUBBLE_CADENCE_DELAY_MS、USER_PROMPT_TIMESTAMP_REGEX、stripUserPromptTimestamp 与 countOccurrences，ChatViewModel 委托调用；MemoryExtractor 提取前置清洗时间戳，杜绝时间戳污染被动记忆
    - CHANGELOG 全量补齐：CHANGELOG.md 补齐伴侣情绪系统、多气泡连续流与消息时间感知全部用户可见特性
  - 自动化测试与构建:
    - 安卓端全量 505+ 项单元测试全绿，桌面端 359/359 全绿且类型检查通过，assembleDebug 构建通过
  - 提交记录 c59732f5

- **NyanoMuse 跨端同步与历史回放气泡标签剥离、多气泡间距与探针脱敏修复 (2026-10-22, 完成)**:
  - 架构防御与跨端标签治理:
    - 剥离跨端同步与 LLM 历史气泡标签：Transcript.kt 与 RemoteBubbles.ts 在同步文本中将 `<nm:bubble/>` 剥离为双换行；ChatViewModel 在 agentHistory.add 与 toLLMMessage 中将助手消息中的 `<nm:bubble/>` 替换为双换行，彻底杜绝多端泄露与上下文失控失真
    - 解决多气泡间距假死代码：NmHomeChrome 修复 topPad 与 bottomPad 硬编码 2.dp 导致的簇内与边界间距未分化问题，簇内设为 1.5.dp（相邻累加 3.dp），边界分别设为 4.dp 与 6.dp，恢复真实聚类层次
    - 消除正则重复编译与常量提取：提取 NM_BUBBLE_TAG、BUBBLE_CADENCE_DELAY_MS 与 countOccurrences 纯字符遍历，彻底消灭流式打字中每 chunk 重复编译正则开销
    - 区分 blockIndex 与 segmentIndex：AssistantMarkdownBlock 与 ChatScreen 明确区分块索引与分段索引，key、slotKey、stableKey 与 shardId 补全段索引，彻底杜绝长文本与多段选择碰撞
    - 压缩摘要过滤提示词时间戳：buildConversationTextForSummary 过滤 USER_PROMPT_TIMESTAMP_REGEX，杜绝时间戳被当作对话历史记忆总结
    - 探针英文脱敏与文档更新：CompanionStatus.probeDetails 标签改为中性英文，docs/android.md 补充主聊天伴侣实时提示词增量说明
  - 自动化测试与构建:
    - 单元测试与 assembleDebug 100% 绿色构建通过
  - 提交记录 a5ca5359

- **NyanoMuse 消息气泡 Telegram 风格时间戳与主聊天用户发言时间感知落地 (2026-10-22, 完成)**:
  - 核心架构与拟真时间体验:
    - AI 时间感知零缓存破坏注入：仅在主聊天中，用户发言进入 agentHistory 与历史重建（toLLMMessage）时，在回合文本末尾附带发送真实时间戳 [yyyy-MM-dd EEE HH:mm]（如 [2026-10-22 周四 16:05]），前文历史前缀字节 100% 保持稳定无损，模型可精确感知跨天、深夜问候与数小时闲置间隔；副聊天严格排除该注入
    - 全局 Telegram 风格气泡时间戳：UserMessageBubble 与 NmAssistantBubble 右下角排布 11sp 微型时间角标（formatBubbleTime 输出 HH:mm），用户气泡半透明柔和显示，AI 气泡采用 ChatColors.tertiaryText
    - 多气泡聚合群规约：多气泡连续流中仅最后一个气泡显示时间戳，群内前序气泡保持极简干净，流式接收中动态抑制时间戳，完毕后平滑显现
    - 数据贯穿与持久化还原：ChatMessage 增加 createdAt 字段，toChatMessage 映射 SQLite entity.createdAt 真实入库时间戳，连续助手回合合并时正确继承最新时间戳，FlatChatItem 完整承接
  - 单元测试与构建验证:
    - BubbleTimeFormatterTest 覆盖时刻格式化、边界值防御与国际化完整日期星期格式化测试
    - AssistantBubbleGroupingTest 补充 createdAt 在 AssistantMarkdownBlock 上的传递校验
    - 全量单测绿色通过，assembleDebug 编译通过
  - 提交记录 51c19619

- **NyanoMuse 主对话拟真多气泡连续消息与打字节奏流全链路落地 (2026-10-22, 完成)**:
  - 核心架构与拟真人性化设计:
    - 结构性气泡语法解耦：采用显式语义标签 `<nm:bubble/>` 作为连续消息切分点，由模型在随意聊天、情绪共鸣或简短问候时自主触发，单回合最多 2 次切分（最多连续 3 个短气泡），长篇说明、技术讲解与代码块严禁拆分；Prompt 指导仅规范结构性排版，不预设也不侵入用户自定义人格
    - 流式打字节奏与动态停顿：ChatViewModel 在收集到 `<nm:bubble/>` 时即刻刷写 UI 封口当前气泡，并在协程层引入 450ms 拟人停顿与打字脉冲（BouncingDots），随后流式吐出下一气泡，还原真人打字断句与发消息节奏
    - 聚类气泡视觉与自适应圆角：NmAssistantBubble 与 AssistantMarkdownBlock 支持 clusterIndex 与 clusterSize，同簇气泡垂直间距紧凑（4dp），外侧角采用 18dp 莫兰迪大圆角，内侧相邻角收缩为 4dp 微圆角，形成微信/Telegram 风格的自然聚合气泡群
    - 数据展平与生命周期守卫：ChatFlatItems 在历史展平时安全解析 `<nm:bubble/>`，上限保护为最多 3 个气泡，首气泡承接 leadingThinking 思考引线，尾气泡承接流式状态与 selectedAnswer 作答，流式空尾段保留以展现打字指示器
  - 自动化测试与构建:
    - AssistantBubbleGroupingTest 补齐多气泡切分、簇数量上限截断、流式空尾气泡保留与思考引线归属全部用例，100% 绿色通过
    - assembleDebug 构建通过
  - 提交记录 814c5ed6

- **NyanoMuse 伴侣情绪系统全链路闭环优化与对话感知微动效联动 (2026-10-22, 完成)**:
  - 核心架构与二轮审查深度落实:
    - 落实外部 AI 审查报告 v2 提出的全部必改项与优化项（P0-1 助手落库点、P0-2 规避自指循环、P0-3 对话行为评估矩阵、P1-1 安全边界与独立开关、P1-2 负向自愈防打架、P1-3 前缀缓存零损耗、P1-4 可观测探针长按防冲突）
    - Dialogue Act 确定性矩阵：摒弃脆弱词典法与自指输入，appraiseUserTurn 仅严格解析用户发言文本，内置前置反讽/阴阳怪气识别（如「呵呵」「真棒呢」），支持 6 大行为类别（PRAISE/VENTING/PLAYFUL_TEASE/GREETING_NIGHT/QUESTION_CURIOUS/CASUAL_CHAT）
    - 非对称半衰衰减模型：blendWithAsymmetricDecay 纯函数实现积极情绪半衰期 15min、负向情绪半衰期 5min，当倾诉（VENTING）被识别后关切心境（CARING）持续主导 10min（ratio > 0.25），明确指示模型温柔关切绝不嬉皮笑脸，下一次用户互动即刻按新行为重构心境，杜绝死锁与失忆
    - 助手精准落库与幂等钩子：ChatViewModel runAgentLoop 仅在 no tool calls -> break 最终助手回合（:9356）触发单次情绪计算，以 lastAppraisedAssistantMsgId 实施幂等守卫，从 agentHistory 逆向提取最后一条用户文本，排查并避开中间工具轮与占位气泡
    - Prompt Cache 零损耗注入：在 buildSystemPrompt 的 volatileSections 尾部注入 MATE 规范的伴侣心境增量（Companion Heart & Disposition），严格位于 runtimeContext 之前，保持 stableSections 前缀字节完全稳定，DeepSeek / Anthropic 前缀缓存 100% 命中
    - 情绪与主动独立解耦：CompanionPrefs 新增 companion_emotion_enabled 独立开关，情绪表现（主聊心境感知）与主动陪伴（定时问候）可各自独立启闭；CompanionSettingsSheet 支持克制/正常/生动三档强度与好感度可见可重置
    - 顶栏心境探针与 Compose 微动效：主聊顶栏头像下方状态胶囊改用 combinedClickable，短按跳转档案，长按弹出包含效价、唤醒度、好感度与半衰期的实时探针 Toast；AgentAvatar 保持 5 态资源管线稳定，通过 graphicsLayer 读取伴侣心境并渲染害羞轻晃、好奇侧耳与兴奋雀跃微动效
    - 17 种国际化语言与穷举守卫：全量补齐 17 种语言 nm_strings.xml，CompanionNotifications 与 CompanionWake 穷举处理所有 8 种 PrimaryMood
  - 代码终审精细化缺陷修复 (emotion_system_code_review.md):
    - P0-1 称呼 key 拼写修复：FirstConversation.KEY_ADDRESS 改为 internal 统一引用，彻底解决 first_conversation_address 无点导致的读取失效问题，增加 12 字符安全截断防超长污染 prompt
    - P0-2 独立维度非对称衰减：提取 decayOne 纯函数，P（效价）与 A（唤醒度）分别按符号独立选择半衰期，解绑共用 ratio 缺陷，确保用户倾诉（VENTING）时高唤醒持续 15 分钟温情陪伴
    - P0-3/P1-5 反讽检测与误伤治理：词表补充中文高频阴阳怪气词句（「行吧」「你开心就好」「我可谢谢你了」等），移除易产生歧义的「你最好」，补全「辛苦了」，引入二段式防讽刺复查
    - P0-4 偏置累积与时间连续衰减统一：recordEmotionImpulse 移除与时间脱节的固定 0.4 系数，记录新冲量时先按 elapsedMs 执行 decayOne 衰减再累加，持久化数值严格反映当前真实偏置
    - P1-1/P1-2 顶栏状态性能与 60s 刷新：ChatScreen 单次计算 compState 并通过 60 秒低频 ticker 驱动重组，自然平复衰减在 UI 上清晰可感
    - 完备单元测试补齐：CompanionEmotionTest 新增 6 类行为判定、反讽拦截、单维度衰减数学、倾诉唤醒度保持与称呼安全截断全量用例
  - 测试与构建验证:
    - 单元测试 1721 项全部通过，assembleDebug 打包成功
  - 提交记录 ffe798c3, 6792a0c5

- **NyanoMuse 深度思考卡片融合进消息气泡与极简引线手风琴重构 (2026-10-22, 完成)**:
  - 核心痛点与视觉重塑:
    - 根除突兀亮蓝硬编码：彻底移除原先孤立的 Color(0xFF015CFB) 亮蓝实框大卡片，深度融入全局 Morandi 配色体系（ChatColors.thinking 与二级字色 ChatColors.secondaryText），告别刺眼视觉噪声
    - 极简引线手风琴交互：借鉴 DeepSeek 与 Claude 现代设计，外层去除繁重边框与底色，收缩时呈现单行轻量手风琴头部，展开时采用 2.5dp 莫兰迪圆角左引线 + 8dp 呼吸缩进，配合 drawBehind 规避 Compose 嵌套内嵌滚动测量问题
    - 中文自然字体排版：正文字体取代全等宽生硬 Monospace 字体，字号 13.sp、行高 19.5.sp，中文阅读舒适自然
    - 实时计时与状态分化：思考中展示旋转指示器与实时计时「思考中 (Xs)…」，思考结束自动收起并转换为「已深度思考 (Xs)」
  - 同气泡一体融合架构:
    - ChatFlatItems 构建时将紧邻正文的思考块作为 leadingThinking 注入 AssistantMarkdownBlock，NmAssistantBubble 内部气泡首行优先渲染思考手风琴，正文紧接着在下方顺滑衔接，真正消除两个卡片断裂感；纯思考流式阶段同样包裹统一气泡
    - ChatViewModel 完善思考块创建与结束计时（startTimeMs 与 durationMs 闭环记录）
    - 17 种国际化语言全面补齐思考中与完成文案并经 NmStringsParityTest 严格校验通过
  - 测试与构建:
    - 编写并更新 AssistantBubbleGroupingTest 覆盖融合气泡与流式独立气泡全部用例
    - 全量 1715 项单元测试 100% 绿色通过，assembleDebug 构建成功
  - 提交记录 46b2ec9c

- **NyanoMuse 安卓端动态配置弹窗滚动与保存按钮常驻优化 (2026-10-22, 完成)**:
  - 核心痛点根除与布局重构:
    - 针对 FeedSettingsSheet 原 OutlinedTextField 无最大高度约束且父容器缺少滚动与 imePadding，导致输入内容较长或输入法弹起时保存按钮被直接挤出可视区域的问题
    - 输入框 OutlinedTextField 增加 heightIn(min = 120.dp, max = 220.dp) 边界，超长内容内部滚动
    - 上半部分表单封装进 weight(1f, fill = false).verticalScroll(rememberScrollState()) 滚动容器，底部保存按钮独立常驻于底部并外挂 imePadding，无论内容多长或软键盘弹出均牢牢保持可见可用
  - 测试与部署:
    - assembleDebug 编译通过并已部署至一加平板 2 Pro（c84b9192）与红米 K60（ed3fdd92）

- **NyanoMuse 伴侣主动对话、情绪系统、侧边栏主聊天与大模型上下文扩充落地 (2026-10-22, 完成)**:
  - 核心架构与落地细节:
    - 阶段一 (纯函数情绪状态机与流控持久化): PAD 纯函数 CompanionEmotion，输入当前时钟、真实用户消息闲置时长（ChatDao allUserMessageStamps 排除虚拟 RoutineWakes 消息）与按本地时区聚合真实真人互动天数，计算确定性心境；清理未使用的 lastUserMessageCreatedAt；免打扰、冷却防抖、每日限额与今日计数存储于 nanomuse 偏好；专属高优先级通知通道
    - 阶段二 (无感评估、调度触发与发话投递): 注册 CompanionAlarmReceiver 30 分钟省电对齐闹钟监听开机自启；场景 tag 全面规范化（normalizeScenario 杜绝短前缀关不掉问题）；CompanionWake 使用 try-finally 恢复会话原始模型绑定；通过 HeadlessChatRunner.prompt 后台无声投递，后台时触发高优先级横幅通知；NmRoutineWakeRow 专属单行静默渲染
    - 阶段三 (主聊天大容量滑动窗口与异步记忆蒸馏): MainChatContextPolicy 针对 128k 至 1M 大模型动态放宽至 64k 至 256k Token 预算，意在保持主聊天细节绝对无损，溢出才触发蒸馏；ChatViewModel 彻底旁路主聊天三处 compactAll 入口规避累加衰减，溢出消息异步经 MainChatMemoryDistiller 蒸馏写入 StructuredMemory（事实 source='distilled'，羁绊 category='bond'），游标 companion_distilled_msg_ids 全消息去重防重复追加并加入 5MB 归档文件轮转保护
    - 阶段四 (UI、侧边栏常驻、多语言本地化与配置中心): 移动端 SideChatDrawer 与电脑端 MuseChats.tsx 顶部新建会话下方均常驻「主聊天」专属快捷入口，带有 Home 图标与选中指示圆点，列表剔除主会话防重；NanoMuseHeader 接入伴侣实时心境副标题；SettingsScreen 新增「伴侣与情绪系统」入口并挂载 CompanionSettingsSheet 底部弹窗；设置面板内场景列表、小时单位与上限标题全量补齐 17 种国际化语言文案并经 NmStringsParityTest 严格校验
  - 测试与部署:
    - 20 项 Companion/ContextPolicy 专项单元测试全部通过，全量 1711 项单元测试 100% 绿色通过，桌面端 358 项全绿
    - assembleDebug 构建通过并通过 ADB 成功热更新安装至手机端（ed3fdd92）与平板端（c84b9192）
    - 桌面端编译生成 lib 产物并部署至 ~/.local/opt/nyanomuse/，重载桌面端进程（nyanomuse-desktop）正常运行

- **NyanoMuse AI 输出完成通知提醒、触觉振动与内容摘要全链路落地 (2026-10-21, 完成)**:
  - 核心病因根治与提醒体系升级:
    - 原生缺口与体验痛点：原先 BackgroundTaskNotifier 仅在应用彻底退入后台时发通知，且通知通道被设为 IMPORTANCE_DEFAULT（低优先级静默无横幅），通知内容机械固定为「点击打开聊天查看回复」，未显示 AI 真实回复；同时前台无任何振动触觉反馈，前台切换到其他 Tab（如 Ideas/Goals/Library/Settings）或在桌面使用其他应用时，用户完全感知不到生成完毕
    - 全新高优先级横幅通知流：重构 BackgroundTaskNotifier，升级专属通知通道 nanomuse_task_completed 为 IMPORTANCE_HIGH 并启用振动与声音，以浮动横幅（Heads-up）形式直观弹出；标题智能提取 Agent 名称（如 nanoMuse / 小喵），正文动态携带真实回复摘要（lastReplyExcerpt / BigTextStyle），副标题显示会话标题，点击一键唤醒直达对应会话
    - 前台多场景智能感知与触觉触感：新增 VIBRATE 权限与轻量触感反馈（vibrateCompletion），AI 输出结束时触发轻快触感脉冲；智能感知 ChatViewModelStore.activeSessionId，用户正在注视当前对话时不冗余弹状态栏通知，在离开当前会话或切换页面时精准补发横幅提醒
    - 生命周期闭环清理：ChatScreen 挂载该会话时定向取消对应通知，不再在应用启动时粗暴清空所有未读完成消息
  - 自动化测试与部署:
    - 编写 BackgroundTaskNotifierTest 单元测试覆盖前台当前抑制、前台异屏放行、开关状态判断与指定取消等全部用例，100% 绿色通过
    - assembleDebug 构建通过并通过 ADB 成功部署安装至手机端（ed3fdd92）
  - 提交记录 e3d9fd10

- **NyanoMuse 应用重启默认进入最后活跃会话全链路打通 (2026-10-21, 完成)**:
  - 核心病因根除与架构重构:
    - 根因定位：NanoMuseHome 原逻辑在冷启动时硬编码 `if (chatSessionId == null) chatSessionId = main`，而 MainChat.resolve 会永久锁定偏好中首次创建的 KEY_SESSION（主聊天），导致无论用户在哪个副聊天中对话或收到跨端同步新消息，一旦重启应用均会被强行拽回最古老的主聊天；且草稿晋升（onPromoted）与会话切换均未持久化记录上次活跃会话
    - 启动恢复引擎升级：MainChat 引入 resolveLaunchSession，联动 KEY_LAUNCH_SESSION 偏好配置（模式 2 新对话 / 模式 3 主页 / 模式 0 自动与模式 1 上次会话）；自动比对本地最后活跃时间戳与数据库最新更新时间戳，智能承接跨端同步新会话或本地刚离开的会话；草稿完成首次发送晋升为真实会话时通过 StateFlow 实时回传并固化 last_active_session
    - 宿主双向同步绑定：NanoMuseHome 接入 LaunchedEffect(chatSessionId) 实时双向登记活跃会话，草稿晋升瞬时无缝切换当前活跃 ID 并高亮侧边栏行
  - 测试与部署:
    - 编写 MainChatTest 独立单测覆盖新对话、主页锁定、跨端最新覆盖与本地连续会话恢复等全场景，单元测试全绿通过
    - assembleDebug 打包并通过 ADB 成功部署安装至手机端（ed3fdd92）
  - 提交记录 af58ef05

- **NyanoMuse 提问工具挂起中实时推送与作答后卡片双向保留修复 (2026-10-21, 完成)**:
  - 核心病因深挖与修复:
    - 挂起中未入库导致不同步：ChatViewModel 在 runAgentLoop 中原先推迟至所有工具执行结束才调用 persistAssistantTurn，而 ask_user_question 在 executeAskUserQuestion 处挂起等待用户点击，导致提问等待期间该轮助手消息从未写入 SQLite，LocalChats 读不到新行，SyncEngine 无法推送，对端设备在提问中完全看不到卡片；修复为在执行 toolCalls 循环前检测到 isAskQuestionTool 即刻预先持久化，记录 assistantDbId 并触发 ConversationSync.changed 与 turnEnded，轮次全部结束时若已存在 assistantDbId 则 updateMessageParts 避免重复插入
    - 作答后分段覆盖导致卡片丢失：Transcript.Row 原先将所有带 toolResult 的消息视为非真人消息合并到同一分段，seg.lastOrNull 选取最终助手回复，导致提问工具调用卡片被永久吞噬；修复为识别问答工具结果 isQuestionAnswer，将其作为独立分段起始（isPersons = true），提取用户选择文本，使得提问卡片与用户答复、后续回复全部完整保留在转录流中
  - 测试与部署:
    - 补齐 Fakes.questionResult 与 TranscriptTest 问答完整轮次双向保留单测，单元测试全绿
    - assembleDebug 构建通过并已部署安装至手机端（ed3fdd92）与平板端（c84b9192）
  - 提交记录 4165041e

- **NyanoMuse 提问工具跨端同步卡片渲染与作答回显全链路修复 (2026-10-21, 完成)**:
  - 核心病因与数据流打通:
    - 根因定位：多端会话同步（SyncEngine / Transcript）原本仅提取 parts 中的纯文本（type == "text"），而模型调用的 ask_user_question 为 toolUse 块，不仅导致问题内容在生成推送文本时被全部丢弃，还因 hasToolUse 判定使得提问阶段的消息被误判为未完成轮次而直接阻断推送；拉取端收到空文本后无法解析任何卡片；即使收到历史问答，InteractiveQuestionCard 也未承接后续用户作答 selectedAnswer
    - 转录推送层升级：Transcript.Row 识别 isAskQuestionTool，将提问参数自动无损打包为 `<question>...</question>` 标准标签并合入 text，同时放行提问交互轮次的同步推送，确保对端设备实时可见问题卡片；桌面端 cloud.ts 同步补全 sessionLines 提问参数注入
    - 拉取与回显闭环：QuestionCardParser.extractQuestion 全面委托至 parseFromToolArgs 完整健壮解析器并支持嵌套代码围栏；ChatFlatItems 为 AssistantMarkdownBlock 注入后续用户消息作为 selectedAnswer，已答状态下卡片自动进入折叠与高亮回显模式
    - 桌面端联动：FenceCards 扩展监听 .nm-remote-bubble 远端气泡与代码围栏，打通双向全端卡片化渲染
  - 测试与部署:
    - 补齐 TranscriptTest 提问轮次推送单测与 QuestionCardTest 复合结构解析单测，全量通过
    - 桌面端 pnpm test 358 项全绿
    - assembleDebug 构建通过并已部署至手机端（ed3fdd92）与平板端（c84b9192）
  - 提交记录 d3bb7c46

- **NyanoMuse 提问工具多选题复选交互与合并提交落地 (2026-10-21, 完成)**:
  - 多选交互状态与视觉重构:
    - 修复此前 InteractiveQuestionCard 未感知 isMultiSelect 导致点击选项立即单选触发提交的问题
    - 引入 selectedOptions 状态容器与多选交互分支：在 isMultiSelect 为 true 时支持选项点击自由勾选或反选，选项前置复选框（RoundedCornerShape 方形带对勾）替代传统单选圆环
    - 标题栏动态附带「多选」指示胶囊，底部新增多选状态栏与「确认提交」操作按钮，实时显示当前已选项目数量，点击确认后统一聚合为逗号分隔字符串回传
    - 已提交回答回显支持按多选拆分（逗号、顿号、换行）高亮呈现全部已选项
    - QuestionCardParser 扩充 multiple 字段兼容检测
  - 测试与部署:
    - QuestionCardTest 补全蛇形与驼峰命名多选参数识别测试，单测 100% 通过
    - assembleDebug 编译通过并已部署安装至手机端（ed3fdd92）与平板端（c84b9192）
  - 提交记录 67148dcf

- **NyanoMuse 提问工具调用（ask_user_question / ask_question / ask_user）卡片渲染与参数解析全端修复 (2026-10-21, 完成)**:
  - 核心病因根治与容错加固:
    - 根因定位：AgentTools 中 ask_user_question 工具参数被声明为 `type: "string"`，导致 LLM 回传 JSON 字符串或直接传递对象，而 QuestionCardParser 仅按单一 JSONArray 提取；当解析为空时 ChatScreen 判定 `qData == null` 直接静默跳过渲染，且 Preflight 因参数校验过严产生误阻断，导致提问挂起后屏幕卡片完全空白
    - QuestionCardParser 全面升级：支持 Markdown 代码块剥离、根级 JSON 数组解析、字符串化 JSON 展开、直接根级 question/options 映射、prompt/choices/answers 兼容别名及文本/描述多字段抽取，在无预设选项时自动提供优雅交互兜底（确认/取消），杜绝解析失败返回 null
    - 渲染兜底闭环：ChatScreen 在卡片构造器处接入安全兜底，即便原始参数异常也强制渲染问题卡片，保证用户始终可交互作答而不死锁
    - 跨端工具名与预检对齐：统一覆盖 ask_user_question、ask_question、ask_user 与 ask，ChatViewModel 预检对提问工具放宽直接 question/prompt 参数，桌面端 rooms.ts 同步补全多字段描述提取
  - 自动化测试与部署验证:
    - 编写安卓端独立单元测试 QuestionCardTest 覆盖标准数组、字符串化嵌套、根级对象、Markdown 围栏与预检放行等 10 种边界情况，100% 绿色通过
    - 桌面端 pnpm test 全量 358 项测试 100% 绿色通过
    - assembleDebug 编译通过，已自动部署安装至手机端（ed3fdd92）并同步更新桌面端安装产物
  - 提交记录 55a5d18d

- **NyanoMuse 全链路长上下文治理与注意力优化全端落地 (2026-10-21, 完成)**:
  - 核心架构与注意力治理:
    - 针对长记忆与上下文注意力稀释问题（Lost in the Middle 与 128k 上下文降智），落地 Tier 3 动态注意力注入（Query-Aware Dynamic Attention Injection）
    - 废除静态全量灌入 3000 字符常驻记忆机制，重构为置顶核心底护照（Pinned Core Passport）+ 意图相关性动态召回（Dynamic Top-K Recall，上限 8 条记忆，总预算 2000 字符）
    - 系统提示词动态感知当前会话用户最新 Query，无相关提问时仅保持稳定前缀护照与全局文件，大幅提升 Provider Prompt Cache 命中率与长会话推理聚焦度
    - 活跃目标（Goals）仅注入 tracking 活跃状态，归档及完成目标彻底移出实时注意力上下文
  - 结构化四分面压缩提示词重构:
    - 安卓端 ChatViewModel 压缩提示词升级为 Markdown 四分面结构化契约（任务状态与目标、核心决策与约束、文件产物与代码变动、踩坑与禁止事项）
    - 杜绝长会话多轮压缩导致的上下文漂移与技术决策失真，严格规避盲目滑动窗口折叠对前缀缓存的破坏
  - 自动化测试与工程加固:
    - 抽离纯函数 selectMemoriesForPrompt 至独立模块，双端统一上限约束常量（MAX_PINNED_MEMORIES=6, MAX_PINNED_CHARS=800, MAX_INJECTED_MEMORIES=8, MAX_INJECTED_CHARS=2000），清理死代码
    - 修复测试虚脱问题：query-aware-context.test.mjs 覆盖置顶硬上限、动态意图排序、回退填充与字数预算；ContextOptimizationTest 直接断言 ChatViewModel 真实四分面标题常数并覆盖安卓端选择器
    - 同步更新 CHANGELOG.md 与 docs/desktop-muse.md、docs/android.md 文档
    - 桌面端 pnpm test 全量 357 项测试 100% 绿色通过，安卓端 testDebugUnitTest 全量测试通过，assembleDebug 构建并通过 ADB 安装部署至平板（c84b9192）
  - 提交记录 35f5c199, 8a7343cc

- **NyanoMuse 零开销语义概念扩展与被动自然偏好捕获全端落地 (2026-10-21, 完成)**:
  - 零开销语义概念与同义词泛化扩展:
    - 针对本地离线与轻量运行场景，彻底摆脱笨重 Embedding 模型开销，建立双向等价同义词表（EQUIVALENT_SYNONYMS）与单向上下位概念层级（HYPERNYM_EXPANSIONS）
    - FTS 查询构建器（buildFtsQuery）实现概念自动展开扩充，精准覆盖设备、系统、窗口管理器、包管理器、开发工具及日常饮食习惯
    - 应用层打分器（scoreCandidate）注入 0.5 语义覆盖增益，解决非字面重叠语义召回（如搜热饮召回拿铁，搜电脑系统召回 PC 操作系统）
  - 安全被动自然偏好捕获流（extractPassiveMemories）:
    - 严格遵守防投毒边界，仅对来自 user 角色的真实用户发言执行被动提取，绝对阻断工具调用与网页注入伪造
    - 精准识别硬件环境、居所变动、习惯、称呼、健康约束及沟通规范，内置 transient 过滤规则自动拦截瞬态即时指令与闲聊反问
    - 提取事实通过冲突消解体系（findDirectConflict / supersede）安全入库，多端保持一致
  - 自动化测试与工程验证:
    - 桌面端 pnpm test 全量 352 项测试 100% 绿色通过，pnpm typecheck 与 pnpm build 构建正常
    - 安卓端 testDebugUnitTest 全量测试通过，assembleDebug 构建并通过 ADB 安装部署至平板（c84b9192）
  - 提交记录 bd331198

- **NyanoMuse 记忆冲突消解与时态演进系统全端落地 (2026-10-21, 完成)**:
  - 核心架构与冲突消解闭环:
    - 落地信念修正与时态演进机制（Belief Revision & Temporal Evolution），杜绝事实冲突导致的常驻记忆污染
    - 双端引擎（MemoryStore / LocalMemoryDb）实现原子化 supersede：自动将旧事实标记归档至 Cold 持久区（is_archived = 1，降权），同时将新事实写入 Hot 常驻区并继承分类与置顶状态，双路操作同步派发 OpLog
    - 内置高精度直接属性冲突检测器（findDirectConflict）：针对称呼、居住地、核心硬件/OS、关键工具偏好等事实实现自动命中与静默覆盖，支持 detectConflicts 拓扑粗筛
  - 工具层与提示词注入升级:
    - 桌面 remember 与安卓 memory_write 工具参数扩充 replaces_id，模型可显式传入冲突旧记忆 ID 完成原子替换
    - 系统提示词动态注入记忆句柄：常驻记忆统一输出 `[- [id] 内容]` 显式锚点，并在上下文附带冲突消解指令，模型发现偏好或状态变更时精准调用覆盖
  - 自动化测试与验证:
    - 桌面端 pnpm test 全量 350 项测试 100% 绿色通过，pnpm build 构建正常
    - 安卓端 testDebugUnitTest 全绿，assembleDebug 打包并通过 ADB 部署至平板（c84b9192）

- **NyanoMuse 桌面端与安卓端设置记忆管理界面现代化重构 (2026-10-21, 完成)**:
  - 桌面端 (dsh-nanomuse):
    - 设置中设立独立记忆管理中心板块（Settings -> Memory），MuseSettings 注册主导航入口并绑定脑电波图标
    - 界面全面对接底层持久化 MemoryStore，支持实时多语种与 CJK 模糊即时检索，具备活跃/归档状态与分类多维筛选胶囊
    - 记忆卡片支持置顶/取消置顶、归档/恢复、实时编辑与二次确认删除，保留底层 MEMORY.md 浏览与数据导入导出入口
    - 样式深度注入莫兰迪亚克力毛玻璃质感，适配深浅双色主题
    - pnpm typecheck、pnpm build 与 pnpm test 全量 348 项测试 100% 绿色通过
  - 安卓端 (com.openminis.app & io.github.nanomuse):
    - MemoryManagementScreen 深度重构为 Jetpack Compose 现代仪表盘与卡片流
    - 顶部聚合常驻/归档/总计三联统计看板，支持关键字实时检索与状态/分类多维过滤胶囊
    - 列表项支持一键置顶、归档/取消归档、内联弹窗编辑与安全删除，底部收纳折叠式历史 Markdown 日志直达入口
    - LocalMemoryDb 与 MemoryRepository 补全封装接口，多语言资源全量对齐
    - 单元测试与 assembleDebug 构建通过，安装部署至平板（c84b9192）验证通过

- **NyanoMuse 会话全量漫游契约确立与记忆系统健壮性闭环 (2026-10-21, 完成)**:
  - 会话同步契约终局对齐：
    - 正式确立「全部会话默认同步漫游」为新架构契约，彻底统一桌面与移动端体验（会话即会话，不再区分主旁）
    - 同步更新 sync.ts 架构注释，在 sync.test.mjs 中完善断言：未迁移旧状态默认升级为同步开启（true），同时显式关闭（sideChats: false）依然安全保全
  - 记忆系统健壮性与安全防护加固：
    - 修复 upsert 显式传入不存在 ID 时误触 UPDATE 导致返回 null 且未落库的严重缺陷：仅在未传 ID 时做内容查重（findByContent），显式 ID 不存在时一律 INSERT，配套编写单测验证通过
    - 增加 FTS 粗筛候选集硬上限（LIMIT 500），防止海量数据下 MATCH 结果导致 IN 查询语句参数爆满
    - 安卓 LocalMemoryDb 补全 episodes 与 episodes_fts 虚表结构，保持双端 DDL 架构 100% 精确一致
    - 云端中继 sync.py 增加 client_time 与 updated_at 异常类型防御（ValueError/TypeError 降级回退），杜绝 500 崩溃
    - rooms-tools.ts 落地系统提示词记忆注入硬预算：单次对话最多注入 30 条或 3000 字符（约 1000~1500 tokens），置顶优先，超出部分友好提示引导调用 recall_memory
  - 自动化测试与验证：
    - 桌面端 pnpm test 全量 342 项单测 100% 绿色通过，pnpm build 构建正常
    - 安卓端 testDebugUnitTest 全绿，assembleDebug 构建并通过 ADB 安装部署至平板（c84b9192）
  - 提交记录 c2061a87, fcc49472

- **NyanoMuse 长期可检索记忆系统检索召回加固与全端落地 (2026-10-21, 完成)**:
  - 检索召回与分词缺陷根治：
    - 修复 FTS 查询空格隐式 AND 导致的召回归零问题，FTS 查询短语统一以 OR 语法拼接（buildFtsQuery），FTS 粗筛召回全部重叠候选后由应用层统一打分器（scoreCandidate）执行精准排序，评测集召回率由 0/8 跃升至 8/8（Top-1 100% 命中）
    - 分词器扩展支持全 Unicode 字母与数字范围（\p{L}\p{N} 与 Character.isLetterOrDigit），彻底规避重音字母、西里尔与特殊字符截断
  - 数据安全、去重与重置隐私闭环：
    - rooms.ts 与 LocalMemoryDb 在 upsert 阶段增加基于内容哈希/titleKey 的重复判定，彻底杜绝重复内容反复插入生成脏 ID
    - resetData 修复数据库连接残留与隐私泄漏风险：显式关闭数据库连接并彻底物理抹除 memory.db、memory.db-wal 与 memory.db-shm 后重建空库
    - exportData 补全全量记忆归档：导出 Zip 包时自动将全局记忆结构化转储为 nanomuse/memories.json
    - rooms-tools.ts 修复记忆注入倒序截断缺陷：将 memory.slice(-120) 纠正为 memory.slice(0, 100)，优先保留置顶记忆与最新高权重记忆
  - 移动端连接与全量测试闭环：
    - MemoryRepository 深度集成 LocalMemoryDb：在 loadGlobalMemoryFragment 注入常驻结构化记忆，在 getMemory 关键字检索时双路并发查询 Markdown 日志与 SQLite FTS
    - 移除 MemorySearchTest 中硬编码绝对路径，动态向上解析测试集资源
    - 桌面端 pnpm test 全量 341 项测试 100% 绿色通过，安卓端 testDebugUnitTest 全绿并完成 assembleDebug 打包安装至平板（c84b9192）
  - 提交记录 90fdc9ae

- **NyanoMuse 长期可检索记忆系统全链路全端落地 (2026-10-21, 完成)**:
  - 核心架构与决策闭环：
    - 废除 FTS 内建打分依赖，两端统一采用预分词 CJK Bigram + 单词切分（tokenizeForSearch），排序在应用层由统一算法（scoreCandidate）确定性计算，彻底消除 Android FTS4 缺 bm25 导致的跨端歧义
    - 废除 400 条硬编码截断，构建 Hot（活跃常驻区）与 Cold（持久归档区）分级体系，将系统提示词记忆输入预算由 500 放宽至 1500~2000 Tokens，配套提供 recall_memory 原生工具支持深度追溯
    - 确立客户端本地第一公民地位，离线与未登录下 100% 可用，云端作为轻量追加式 OpLog 中继与单调自增 seq 分配器
    - 确立防投毒边界：仅允许 user 角色输入触发自动记忆提炼，绝对阻断工具输出与外部网页内容注入伪造事实
  - 桌面端 (dsh-nanomuse)：
    - 实测 Electron 44.7.0 原生内置 Node 24.21.0 与 SQLite 3.53.4，基于 node:sqlite 构建持久化 MemoryStore，独立 FTS5 虚表显式事务双写
    - 接入 rooms.ts 与 rooms-tools.ts，提供 /memory/search 路由与 recall_memory 原生工具，历史 rooms.json 自动无缝迁移
    - 编写 memory-search.test.mjs 与 memory-store.test.mjs，全量通过评测基准测试
  - 云端中继 (nanomuse_cloud)：
    - db.py 增加 sync_memory_oplog 表（包含 seq, op_id 幂等校验, before_content 回滚），sync.py 实现 push_memory_ops 与 pull_memory_ops
    - api.py 暴露 /v1/sync/memory/push 与 /v1/sync/memory/pull 接口，完成 test_memory_sync.py 单元测试全绿
  - 安卓移动端 (io.github.nanomuse.memory)：
    - 落地 MemoryTokenizer 与 MemoryScorer，与桌面端算法 100% 精确对齐
    - 实现 LocalMemoryDb（基于 SQLiteOpenHelper 与 FTS4），通过 MemoryRepository 与 MinisApp.kt 挂载双写与检索支持
    - 编写 MemorySearchTest 通过黄金评测集，完成 assembleDebug 打包并通过 adb 部署至平板（c84b9192）
  - 提交记录 cce12372

- **NyanoMuse 安卓端全量对齐统一会话架构与草稿流新建 (2026-10-21, 完成)**:
  - 会话抽屉与侧边栏深度重构：
    - SideChatDrawer 移除割裂的「主要聊天」独立行，全面合并为统一扁平的全部会话列表，置顶会话优先、按更新时间倒序排列
    - 抽屉顶部新增高亮「＋ 新建会话」药丸行动按钮，点击即刻进入草稿流新会话，长按会话支持置顶/取消置顶、重命名与安全删除
    - 废除返回主聊天的异常回退拦截逻辑，NanoMuseHome 移除强占返回键的 BackHandler，底部栏切换不再无故跳回主要聊天
  - 会话顶栏体验均质化与莫兰迪玻璃拟态：
    - ChatScreen 顶栏抹平主旁会话差异，全量会话均展示 30dp 动态情绪猫咪头像、会话标题、DeepSeek 实时官方余额胶囊与副标题动态状态行
    - 多语言资源字符串全面对齐：消除所有旁聊与主要聊天陈旧表述，统一更名为全部会话、新建会话与同步所有会话
  - 完成 assembleDebug 打包并通过 adb 安装部署至平板端（c84b9192）截屏校验通过，提交记录 d12b8e14

- **NyanoMuse 统一会话列表架构、上线草稿流新建会话与自定义壁纸引擎 (2026-10-21, 完成)**:
  - 会话概念深度归一与草稿流新建体验：
    - 废除桌面端「主要聊天」与「旁聊」两极割裂的陈旧交互设计，界面呈现统一按置顶与最近更新时间倒序排列的会话列表
    - 会话侧边栏顶部增加高亮「＋ 新建会话」行动按钮与即时搜索框，点击触发 actions.startSession 开启空白草稿会话并聚焦输入区，在首条消息发送前不落库污染
    - 顶栏移除多余的返回主聊天按钮，会话右键菜单精炼为置顶、重命名与归档
  - 多端同步架构兼容与静默保护：
    - 保持云端中继数据库单一 kind='main' 约束的兼容性，在 SyncEngine 底层保持默认同步开启（sideChats: true），所有会话自动双向同步漫游
    - 界面层完全抹平主旁会话差异，对用户保持「会话即会话」的统一认知
  - 自定义壁纸系统与莫兰迪玻璃拟态：
    - cloud.ts 接入 /wallpaper RESTful 接口支持读取、保存与删除壁纸配置，支持一键读取 Noctalia 莫兰迪当前壁纸与用户本地图片上传
    - wallpaper.ts 动态挂载全屏壁纸图层与可调毛玻璃模糊度（0-40px）与暗化遮罩（0-85%）
    - MuseHeader.tsx 顶栏嵌入「壁纸」微型胶囊药丸，呼出沉浸式亚克力壁纸调节弹窗，样式全链路同步 Morandi 质感
  - 完成 build.mjs 编译部署覆盖并重启桌面端校验，提交记录 c20084eb

- **NyanoMuse 问答选择题卡片支持作答折叠与双端莫兰迪玻璃拟态UI深度对齐 (2026-10-20, 完成)**:
  - 移动端选择题卡片交互升级与折叠机制：
    - QuestionCard.kt 重构状态管理，作答后（selectedAnswer != null）自动平滑折叠为紧凑胶囊摘要条（22dp 对勾徽标、题目单行省略、高亮选项药丸与折叠展开箭头）
    - 展开视图全面重构：16dp 圆角、0.8dp 极细描边、26dp 帮助图标微型胶囊、已回答标签与顶栏收起按钮，选项行采用 11dp 莫兰迪药丸、选中态高亮与单选对勾指示
    - 结合 animateContentSize 实现平滑伸缩过渡，编译并在平板端安装部署校验通过
  - 桌面端（dsh-nanomuse）全链路对齐与部署：
    - FenceCards.ts 全面升级 questionCard：解析支持 questions 数组与单体 question 结构，引入 selectedAnswer 与 isExpanded 状态回路
    - 选项点击自动即时折叠为胶囊胶囊药丸，支持点击胶囊随时展开复查或重新作答
    - styles.ts 注入完整莫兰迪玻璃拟态样式（nm-question-card、nm-question-collapsed、nm-question-expanded、nm-question-option 等），并针对 Harness 原生 QuestionComposer 与 ToolRow 注入一致的圆角毛玻璃微调
    - 顶栏 DeepSeek 官方余额胶囊同步上线：cloud.ts 挂载 /balance 安全接口读取环境或凭据中的密钥并代理查询，MuseHeader.tsx 中心顶栏无缝渲染绿色状态圆点与实时余额，与移动端保持 100% 体验一致
    - 完成 build.mjs 编译覆盖并重启桌面端进程验证，提交记录 a9bc6655

- **NyanoMuse grill-me 全面重构为原生 ask_user_question 工具调用与协程挂起交互架构 (2026-10-20, 完成)**:
  - 架构升级与原生工具注册：
    - 废弃基于正文 `<question>` 结构化标签的伪交互协议，全面对齐 DeepSeek Harness 的原生 `ask_user_question` / `ask_question` 工具调用标准
    - 在 AgentTools.kt 中完成 askUserQuestionDefinition 注册，涵盖 questions 数组、question 精炼陈述、options 数组与 is_multi_select 声明
  - 协程挂起与双向交互响应回路：
    - ChatViewModel.kt 引入 pendingQuestionDeferreds 字典与 CompletableDeferred 挂起机制，当代理调用 ask_user_question 时挂起当前工具执行流
    - 用户在界面卡片点击选项或在输入框发送自定义文本时调用 answerQuestion，立即恢复挂起协程并返回「User selected: <choice>」工具执行结果，支持流式取消与重试清理
  - 渲染拦截与图层穿透防护：
    - ChatFlatItems.kt 增加 FlatChatItem.AssistantAskQuestion 独立卡片类型，在工具块遍历时前置拦截 ask_user_question 避免被 showSteps = false 隐藏，保证问题交互卡片永远可见
    - hasVisibleContent 与 stepsOnlyTurn 视其为可见内容，避免提问等待时出现无意义的闪烁输入中指示器
    - ChatScreen.kt 将其接入 InteractiveQuestionCard，绑定 answerQuestion 回调，并支持根据 content 结果展示「已回答」状态与选项高亮
  - 多端协议同步与构建部署：
    - 更新 SkillRepository.kt 的 GRILL_ME_CONTENT，版本升级为 2.0.0，并在 Android 打包时强制同步更新
    - 同步更新 ~/.nyanomuse/desktop/skills/grill-me/SKILL.md、~/.agents/skills/ 与 ~/.dsh/skills/
    - 编译 assembleDebug 通过并在平板端（c84b9192）完成安装部署

- **NyanoMuse 修复问答卡片重叠与高光渲染异常并全量部署更新桌面端 (2026-10-20, 完成)**:
  - 安卓端问答卡片（QuestionCard）布局重叠与颜色反差根治：
    - 排查定位 NmAssistantBubble 内部原使用 Box 容器，且 ChatScreen.kt 中 MarkdownBlock 与 InteractiveQuestionCard 作为无容器包裹的平级子项，导致卡片在坐标 (0, 0) 与上文 Markdown 描述文本物理重叠互相穿透
    - 将 NmAssistantBubble 内部容器调整为 Column，并在 ChatScreen.kt 中使用 Column(modifier = Modifier.fillMaxWidth()) 严格封装文本与卡片，彻底根除图层遮挡与穿透
    - 修复深色模式白底白字渲染异常：深色主题下 ChatColors.sendButton 为纯白（#FFFFFF），原先用作推荐徽标背景与边框导致严重刺眼高光且文字不可见；全面重构为 ChatColors.link（#58A6FF 莫兰迪蓝高对比主题色），推荐徽标改为半透明蓝色药丸底配同色加粗文字，选项卡片采用 toolCapsuleBg 与 toolBorder
    - 优化选项排版对齐：单项 Row 改为 Alignment.Top 顶端对齐，彻底解决长文本折行时徽标和圆点在垂直居中位置悬空的排版不适
    - 重新编译 assembleDebug 并通过 adb 安装至平板端（c84b9192）
  - 桌面端（dsh-nanomuse）深度对齐与全量构建部署：
    - 会话顶栏高度收缩：将 --nm-header-h 从 108px 压缩至 68px，顶栏渐变高度降低并叠加 backdrop-filter: blur(10px) 毛玻璃
    - 交互式问答卡片支持：在 FenceCards.ts 中增加对 <question> 结构化标签与代码块的动态扫描与解析，以 Web 标准 DOM 生成一致风格的交互选择题卡片，点击选项自动填充并即时发送
    - 桌面端 DeepSeek Harness 接入 /grill-me 技能：同步部署至 ~/.nyanomuse/desktop/skills/grill-me/SKILL.md、~/.agents/skills/ 与 ~/.dsh/skills/
    - 运行 build.mjs 完成全量编译，同步替换至 ~/.local/opt/nyanomuse/resources/dsh/node_modules/dsh-nanomuse/，并重启桌面端进程（nyanomuse-desktop）正常运行，提交记录 faef36d8

- **NyanoMuse 修复DeepSeek余额与今日花费胶囊在主聊天顶栏未显示问题 (2026-10-20, 完成)**:
  - 顶栏胶囊未展示根因定位与布局修复：
    - 排查定位 ChatScreen.kt 中原 DeepSeek 胶囊放置于 `else if (!nmHideModelRows)` 模型副标题列内部，由于主聊天默认开启极简模式（nmHideModelRows 为 true），导致整列副标题与 DeepSeek 胶囊在主聊天中被完全短路跳过未渲染
    - 废弃纵向副标题内的旧版胶囊，将其提升至顶栏中心标题行（与 displayTitle / sessionTitle 水平居中并列排布），不增加顶栏任何纵向高度，保持 50dp 极致紧凑顶栏
    - displayTitle 增加 weight(1f, fill = false) 弹性收缩保护，在保证标题与胶囊同屏优雅并排的同时杜绝超长标题导致的文本折行与视觉挤压
  - 余额获取与多模型适配全链路加固：
    - DeepSeekTracker.kt 的 isDeepSeekModel 扩展支持联合校验 modelId、displayName、providerName 与 baseUrl，全面覆盖直接调用、自建代理中继及模型别名
    - ChatViewModel.kt 的 refreshDeepSeekStatus 智能识别当前活跃实例：若当前实例为第三方中继且无官方余额接口，自动从配置中搜寻已启用的官方 DeepSeek 实例密钥查询官方余额（https://api.deepseek.com/user/balance），兼顾今日花费实时统计与官方真实余额展示
    - 新增流式结束（_isStreaming 翻转为 false）与会话加载完成（sessionLoaded）时的自动触发刷新机制，点击胶囊即刻强刷并呼出用量热力图底栏
  - 编译打包并通过 adb 安装至平板端（c84b9192）截屏验证，余额与花费正常展示，提交记录 f857a558

- **NyanoMuse 会话顶栏紧凑度与渐变模糊优化、多轮工具命令合并与底部悬浮条移除 (2026-10-20, 完成)**:
  - 会话顶栏高度压缩与渐变模糊优化：
    - 废弃原先纵向堆叠的大型头像圆盘（76dp）与双行药丸，重构为极致紧凑的水平 Row 布局（30dp 微型头像与标题状态垂直居中排布）
    - TopAppBar 的 expandedHeight 从 112~140dp 深度裁剪至 50dp（降幅超 60%），顶栏 hazeEffect 渐变模糊层高度减半，彻底解决遮挡聊天内容问题
    - 滚动列表 contentPadding 相应收窄，会话内容自然上浮呈现
  - 多轮命令与工具调用聚合为单张可展开折叠卡片：
    - 针对连续多轮工具调用（如 shell_execute 连续探测与多步排查），在 ChatFlatItems 中将工具组收集状态提升到消息循环层级
    - 消除模型中间推理思考（reasoning_content）对工具序列的切断影响，全回合连续工具/命令无缝合并为单张 ToolCallGroup 折叠胶囊
    - 默认以微型胶囊形态收纳（展示「已执行 N 个工具/命令 · 耗时 X.Xs ⌄」），支持点击平滑内联展开/收起全部工具执行细节
  - 移除执行命令时的底部冗余悬浮窗：
    - 移除输入框上方伴随工具运行而弹出的 FloatingToolStatusBar 悬浮条及其缩略图，将工具运行与完成状态完全收拢至消息流内联折叠卡中，保持输入区清爽干净
  - 编译并在平板端（c84b9192）完成安装验证，全链路测试通过，提交记录 45ab6263

  - 会话顶栏 DeepSeek 专属余额与今日花费胶囊：
    - 新增 io.github.nanomuse.chat.DeepSeekTracker：内置 DeepSeek 官方费率阶梯计算模型（V3: 输入¥1/M、缓存命中¥0.1/M、输出¥2/M；R1/Reasoner: 输入¥4/M、输出¥16/M），基于本地 Room 数据库扫描今日 00:00 至今的所有 UsageRecord 实时毫秒级计算累计今日花费
    - 异步调用 DeepSeek 官方余额接口（GET https://api.deepseek.com/user/balance），获取成功时展示「余额: ¥xx.xx · 今日花费: ¥x.xx」，第三方中继或超时时优雅降级仅展示「今日花费: ¥x.xx」，杜绝占位符报错
    - ChatScreen 顶栏模型副标题下方接入半透明毛玻璃微型芯片胶囊，点击即时触发余额强制刷新并弹出用量详情底栏
  - GitHub 风格用量贡献热力图与日周月多维看板重构：
    - UsageStatsScreen 深度重构：引入 7 行 × 26 周（近半年 182 天）横向平滑滚动的活动贡献热力图网格，动态映射当前系统莫兰迪主题阶梯色阶，自动平滑滚动定位至今日
    - 热力图交互下钻：点击具体日期展开当日卡片，清晰呈现当日总 Token、输入/输出/缓存明细、预估花费与活跃模型标签徽标
    - 日/周/月分段切换控制看板：提供「今日 / 本周 / 本月」胶囊切换，实时统计所选周期的总 Token、输入输出分布、缓存命中率与预估花费金额
    - TokenUsageSheet 与主导航新增直达入口，全链路互通
  - 全量单元测试 testDebugUnitTest 100% 绿色通过，Android Debug APK 构建完成，GitHub main 分支完成提交推送（4bd39144）

- **NyanoMuse 中继同步作用域修复、端点空URL防御与Root模式截图路径归一化 (2026-10-20, 完成)**:
  - 云端中继会话同步异常与 500 崩溃根治：
    - 排查定位 cloud/nanomuse_cloud/sync.py 中在 deleted 变量声明前提前引用（deleted = bool(conv.get("deleted"))），导致客户端推送带特定标题或更新时间戳时触发 UnboundLocalError 引发 HTTP 500
    - 调整赋值时序至前置判断之前，修复后 pytest 24/24 测试套件全绿通过并热重启 8787 端口中继服务
  - 安卓端登录与连接空 URL 防御：
    - 排查定位 CloudSignInScreen.kt 在服务器地址留空或异常重置时直接调用 login 导致 IllegalArgumentException
    - 增加非空校验拦截与友好错误反馈，并在 Hub.kt 中增加 baseUrl 空串拦截防止构建非法 WebSocket 协议连接
  - Root 模式跨设备截屏与文件下发真实路径直通：
    - ReachOffloadHandler.kt 原先硬编码返回 /var/minis/attachments/... 虚拟路径，在 Root 模式下脱离 PRoot 导致 AI 误判文件丢失或沙箱损坏
    - 将返回值 path 调整为宿主文件系统真实绝对路径（dest.absolutePath），同时保留 minis_path 与 markdown 便于界面富文本渲染
  - 全量单元测试与 Debug APK 编译验证通过，推送远端分支（05a2b690）

- **NyanoMuse 多端会话同步修复、PC端重连与Root模式系统提示词加固 (2026-10-20, 完成)**:
  - 桌面端与多端会话同步断连根因定位与修复：
    - 排查定位桌面端 ~/.nyanomuse/desktop/nanomuse/cloud.json 中 sync.accountId 留存旧账户 ID，启动时 cloud.ts 未检查内存与存储账户 ID 是否一致，导致桌面端 SyncEngine 游标无法与自建中继对齐
    - 修复 harness/dsh-nanomuse/src/cloud.ts：在启动挂载时检测如果 sync.state.accountId 与当前 account.id 不一致，自动触发 sync.accountChanged 重置同步引擎并对齐会话
    - 重新编译构建 dsh-nanomuse 并同步覆盖安装目录，重启桌面端进程，验证 devices 表中 CachyOS 成功上线（last_seen 实时心跳）
  - 安卓端旁聊默认同步机制开启：
    - 排查定位 ConversationSync.kt 与 SyncEngine.kt 中 sideChats（同时同步旁聊）默认写死为 false，导致只有主聊能同步，平板与手机侧边抽屉旁聊列表始终为空
    - 将 sideChats 默认值修改为 true（用户仍可在数据控制中自主关闭），并更新 harness 同步逻辑，实现平板与电脑双向无缝漫游
  - Root 模式系统提示词加固与远程设备离线指引：
    - 排查定位 ChatViewModel.kt 的基础系统提示词写死 Alpine PRoot 沙箱与 /var/minis，导致在 Root 模式下模型误以为沙箱损坏并幻觉报错
    - 系统提示词全面区分 isRootMode：Root 模式下明确告知当前直通安卓宿主 root shell（su），PRoot 沙箱属于刻意停用，内置 CLI 工具（nanomuse-pc、android-* 等）由宿主环境直接分发
    - Computers.kt 提示词加固：当远端设备离线时，明确要求模型以一行简洁话术提示用户检查桌面端运行状态，禁止使用 root 盲目刺探本地端口或沙箱文件
  - 全量单元测试 100% 绿色通过，APK 构建完成，GitHub main 分支完成提交推送（23789a8c）

- **NyanoMuse 聊天输入框完全透明修复与动态页面主题色一致性对齐 (2026-10-20, 完成)**:
  - 聊天输入框完全透明无背景问题根治：
    - 排查定位 ChatScreen.kt 中输入框 Column 在 hazeState != null 时只应用了 hazeEffect 却完全省略了 Modifier.background(...)，且采样的是外层外壳的全局 hazeState，因祖先容器包含 hazeSource 导致循环依赖或未对齐消息层
    - ChatScreen.kt 内部独立建立专属 chatHazeState 节点，将消息列表 Box 注册为 hazeSource(chatHazeState)，顶栏 TopAppBar 与输入框胶囊无缝采样滚动消息层
    - 输入框 Column 与顶栏 Box 无条件显式填充半透明表面背景（composerBg 与 topBarBg）并配置描边，彻底解决无消息滑动或毛玻璃未就绪时输入框 100% 镂空穿透的问题
    - MuseBottomBar、MuseNavRail 与 SideChatDrawer 同步补充显式 background 兜底，防止极端情况下出现图层穿透
  - 动态（Feed）页面背景颜色统一对齐：
    - 排查定位 FeedTab.kt 中 LazyColumn 误用硬编码调色板 MuseTones.canvas（深色下写死纯黑 #000000，浅色下为 #F3F3F5），导致与 Ideas、Goals、Library 以及莫兰迪动态主题严重割裂
    - 将 FeedTab.kt 的 LazyColumn 背景颜色无缝修改为 ChatColors.background，与其他功能标签页及全局主题配色完全统一
  - 平板大屏细节打磨：
    - 平板分栏展开时隐藏聊天顶栏多余的侧边栏折叠圆按钮，统一由最左侧 Navigation Rail 顶部按钮总控，消除界面元素重复与卡片视觉遮挡
  - 全量单元测试 100% 通过，APK 编译完成并推送到 GitHub 远端仓库（34a15b31）

- **NyanoMuse 统一手机与平板端主页UI、全面应用Haze毛玻璃与大屏自适应架构 (2026-10-20, 完成)**:
  - 架构统一与大屏自适应（Adaptive nanoMuse Home）：
    - 废除 AppNavigation.kt 中平板大屏强制分流到 OpenMinis 老版 ChatSplitScaffoldRoute 的旧逻辑，全设备统一由 NanoMuseHome 统一自适应承接，彻底消除手机与平板像是两套软件的割裂感
    - 新增 MuseNavRail.kt：平板横屏与大屏展开时，左侧自适应呈现纵向磨砂毛玻璃 Navigation Rail，优雅收纳 Chat、Feed、Ideas、Goals、Library 5 个核心标签胶囊，底部提供新建会话与设置快捷入口
    - 双栏工作台与可折叠会话列表：在 Chat 模式下，大屏左侧自适应呈现 SideChatDrawer 会话栏（主聊、副聊、设备），支持点击顶栏或导航栏图标一键丝滑折叠展开（expandHorizontally / shrinkHorizontally），右侧为主聊天工作流；其他标签页自适应居中并限制 900dp 黄金阅读宽度，杜绝 3K 超宽屏横向拉伸疲劳
  - 全局 Haze 玻璃拟态深度铺设与高分辨率性能调优：
    - ChatScreen.kt 顶栏 TopAppBar 与输入框卡片全面接入 HazeState 与 hazeEffect 磨砂玻璃质感，输入卡片与底部 MuseBottomBar 悬浮双胶囊质感遥相呼应
    - 侧边抽屉底板从死板的纯色 Surface 改为半透明磨砂层（hazeEffect + 0.5dp 细分界线）
    - 针对高分辨率屏幕调优渲染开销：将模糊半径统一优化为 22dp、噪点系数 0.05，共享单根 HazeState 节点，彻底杜绝多层离屏重复采样导致的掉帧卡顿
  - 键盘人体工程学与细节打磨（IME Ergonomics）：
    - 监听软键盘 insets（WindowInsets.ime）：手机端打字弹起键盘时，底部 MuseBottomBar 自动下沉淡出避让，输入框直接吸附于键盘上沿并消除多余空白；键盘收起后平滑弹回
    - 修复 MenuOpen 图标使用为 AutoMirrored 版本消除编译弃用告警
    - 全量自动化单元测试 100% 绿色通过，APK 构建完成并推送到 GitHub 远端仓库（159e2977）

- **NyanoMuse 开放Root模式全局文件系统直通、系统实时截屏工具上线与工具链深度加固 (2026-10-20, 完成)**:
  - Root 模式全局文件系统直通与路径归一化：
    - PRootKernel.kt 重构路径解析：非 PRoot 容器环境（Root 模式与宿主模式）解除前缀白名单限制，任意绝对路径直连底层文件系统，支持波浪号（~）自动映射至真实存储空间与临时目录，支持常见系统分区（system、vendor、data、sdcard、dev、proc、sys 等）省略前导斜杠时自动归一化补全
    - SettingsScreen.kt 在当前执行模式为 ExecutionMode.ROOT 时自动隐藏「挂载外部文件夹」配置入口，避免对具备全盘操作能力的 Root 模式产生冗余误导
  - 系统实时屏幕截屏工具（screen_capture）与多端视觉管线集成：
    - NativeSystemTools.kt 新增 screen_capture 原生系统工具：Root 模式下通过 su 管道直通 /system/bin/screencap -p 零延迟捕获无损 PNG 字节流，非 Root 模式下无缝回退至 AccessibilityService 屏幕快照
    - ChatViewModel.kt 的 executeToolCall 将 screen_capture 深度接入视觉解析管线：原生支持视觉的多模态大模型直接接收像素分析屏幕，无原生视觉模型自动分发给 Vision Group 协同生成详细屏幕描述
  - 文件读写、编辑与图像解析工具链深度加固：
    - FileReadTool.kt 补全 Root 环境目录探测保护（直接读取目录时给出友好提示并指引使用 shell_execute ls 列出），优化非 root 权限文件大小探测，采用 sed 与 tail 分页安全读取大文件防内存溢出
    - ReadImageTool.kt 深度适配 Root 模式：当 Java 权限受限时自动通过 su 管道流读取底层受限目录（如 /data/local/tmp、/data/data/ 等）中的图片字节并由 BitmapFactory 内存解码，增加目录误读拦截
    - FileWriteTool.kt 与 FileEditTool.kt 全面采用 POSIX 单引号安全转义（'\''），彻底消除路径中包含特殊字符、美元符变量（$）或空格时的 Shell 变量展开漏洞，父目录缺失时自动递归补建（mkdir -p）
    - ToolSelfHealing 扩展支持 screen_capture、file_write 与 read_image 的自愈诊断提示
  - Root 模式原生扩展 CLI 工具链（nanomuse-pc、android-*）直发直通支持：
    - NativeOffloadServer 新增 canHandle 与 dispatchDirect，并在 ExecutionCoordinator 中无缝拦截分发，彻底解决过去在 Root 模式下执行 nanomuse-pc、android-device 等命令时因脱离 PRoot Alpine 沙箱导致提示找不到命令（127）的断层问题，免除重装 Alpine 沙箱镜像的额外开销
  - 虚拟路径解析优先级修正与多端协同遗留文案清理：
    - PRootKernel.kt 调整路径解析优先级：确保以 /var/minis/ 开头的应用内部虚拟路径（记忆、技能、工作区、附件、minis://）在 Root 模式下优先解析至真实的内部 filesDir 存储目录，避免被普通绝对路径规则短路到宿主根目录
    - Computers.kt 与 ReachOffloadHandler.kt 全面清理旧版官方云遗留文案，统一对齐自建中继服务
  - 关键系统分区与敏感文件风控告警防护：
    - RiskGate.kt 新增 checkFileModification 与 assessFileModification 校验门控，精确识别 dev/block、proc/sys、sys/fs、sys/kernel 以及 system、vendor、product、apex、packages.xml、init 脚本等核心高危系统路径
    - ChatViewModel.kt 的 executeToolCall 在执行 FileWriteTool 与 FileEditTool 时前置接入风险拦截，涉及高危路径时抛出二次审批卡片，常规目录（sdcard、data/adb/modules、data/local/tmp、用户沙盒等）保持零摩擦极速执行
    - 全量自动化单元测试 100% 绿色通过，APK 构建完成并推送到 GitHub 远端仓库（8fe19a00）

- **NyanoMuse 初始引导对话移除、平板气泡自适应宽度、多端设备自动识别与多语言资源对齐 (2026-10-20, 完成)**:
  - 初始引导对话剧本彻底移除：
    - 排查定位 FirstConversation.kt 中硬编码的开屏引导剧本（包含「你好，我是 nanoMuse」、「我该怎么称呼你？」及改名卡片），将其 shouldShowIntro 设为 false，状态默认锁定为 Phase.DONE，intro 与 promptAddendum 返回空
    - ChatViewModel.kt 的 nmSeedFirstConversation() 增加虚拟消息 nm_intro_* 与改名卡片硬清除
    - harness/dsh-nanomuse/src/firstrun.ts 同步将 showsIntro 置为 false
  - 平板与大屏气泡最大宽度自适应重构：
    - NmHomeChrome.kt 中原先写死 Modifier.widthIn(max = 340.dp) 导致在一加平板 2 Pro（12.1 寸大屏）上气泡过于狭窄
    - 改用 BoxWithConstraints 动态适配：小屏手机保持原有优雅宽度，平板与宽屏自适应扩展至 minOf(760.dp, maxWidth * 0.88f)
  - 多端设备类型自动识别与标识增强：
    - Hub.kt 与 NanoMuseCloud.kt 引入 isTablet 屏幕尺寸探测（smallestScreenWidthDp >= 600）
    - 平板设备自动赋予 tablet- 设备 ID 前缀并在默认设备名称后追加 (Tablet) 后缀，自建中继多端列表中手机与平板设备一眼区分
  - 多语言资源对齐与单测全量修复：
    - 清理剩余代码与资源中遗留的官方 nanoMuse Cloud 文案，统一为「自建中继 / 自建服务」
    - 修复 nm_cloud_err_allowance 与 nm_cloud_warn_line 占位符格式化参数缺失，并在全部 16 种语言包中补全 nm_cloud_title
    - 全量单元测试 testDebugUnitTest 100% 绿色通过，Android Debug APK 构建完成，GitHub main 分支完成提交推送（43caf8fe）

- **NyanoMuse 自建服务页面暗色文字根治与智能体黑猫人设记忆防覆盖保护 (2026-10-20, 完成)**:
  - 自建服务与多端同步页面深色模式黑字根治：
    - 排查定位 MuseChrome.kt 中 MuseCard 仅设置 color = MuseTones.surface（#1C1C1E），未显式指定 contentColor，Compose M3 的 contentColorFor 无法匹配自定义色值导致 Color.Unspecified，使得未显式设色的 Text 组件全部回退到 Color.Black
    - MuseCard 内部显式补充 contentColor = MaterialTheme.colorScheme.onSurface
    - 在 CloudAccountScreen.kt 中为登录用户名（a?.hint）、免费开源非营利卡片标题（R.string.nm_cloud_notice_title）以及未登录卡片标题（R.string.nm_cloud_not_signed_in）显式传入 color = MaterialTheme.colorScheme.onSurface，确保深色模式下全部清晰反白
  - 智能体黑猫人格与记忆防覆盖保护：
    - 排查定位手机端登录自建账号后，远端 ConfigSync 误用默认空模板拉取覆盖了本地真实的 SOUL.md 与黑猫人设
    - 从本地备份恢复 2405 字节完整纯黑大蓝眼小猫人设与记忆至 K60（SOUL.md，属主 u0_a545:u0_a545）
    - 修复自建中继数据库 profiles 表唯一所有者人设名称为 nanoMeow，同步本地 shared_prefs
    - 重构 ConfigSync.kt 下发保护逻辑：若本地已存在定制 SOUL.md，远端默认模板绝对不覆盖本地内容，仅当远端更新时间戳更新且内容为定制设定时才允许合并
    - 重新编译打包 Android Debug APK 并通过 ADB 静默安装至 Redmi K60，GitHub 提交推送完成

- **NyanoMuse 聊天页面底部黑色阴影清除与深色模式气泡文字配色全面优化 (2026-10-19, 完成)**:
  - 聊天底部黑色阴影根治：
    - 排查定位 `ChatScreen.kt` 中 `NmComposerVignette` 滚屏渐变遮罩、输入框外部 `Modifier.shadow` 4dp 黑影及 `MuseBottomBar.kt` 中 `amoledNavPillSurround` 底栏强绘制纯黑遮罩
    - 彻底移除 `NmComposerVignette` 与底栏多余修饰符，剥离输入卡片多余投影，恢复平滑自然的沉浸通透渲染
  - 深色模式文字与气泡配色全面修正：
    - 排查定位旧版深色模式下用户气泡错误写死为白底黑字（`userBubble = Color.White`、`onUserBubble = Color.Black`）的视觉颠倒问题
    - 重构 `ChatColors.kt` 与 `ThemePalette.kt`（含莫兰迪、经典蓝、OLED纯黑、猫猫暖樱、Material You）：深色模式下用户气泡改为沉稳暗色容器，文字统一调整为高对比度清晰白字
    - 修复 `MorandiDarkColorScheme`、`SakuraDarkColorScheme` 与 `OledDarkColorScheme` 中 `onSecondary` 误设为纯黑的问题
    - 优化 `MuseBottomBar` 激活态底色为 `primaryContainer` 与 `onPrimaryContainer`，杜绝暗色模式下底栏白底黑图标刺眼对比
    - 重新编译生成 Android Debug APK 并通过 ADB 安装部署至 Redmi K60

- **NyanoMuse 后台动态批处理会话阻断与多端旁聊僵尸会话自愈清理系统 (2026-10-19, 完成)**:
  - 动态会话旁聊泄露根因定位：
    - 桌面端 DeepSeek Harness 插件层 `rooms.ts` 中 `refreshFeed()` 每日后台批处理任务使用普通会话临时生成动态卡片（标题为「动态 · YYYY年MM月DD日」或「Feed · YYYY年MM月DD日」）
    - 桌面 `SyncEngine` 与 `nanomuse/sync/engine.py` 未对批处理会话进行排查，在开启「同时同步旁聊」时将该临时会话以 `kind: "side"` 格式推送到自建中继
    - 手机端从自建中继拉取远程会话并以 `source = "sync"` 写入本地数据库，导致手机侧边抽屉中涌入大量「动态 · ...」孤儿会话
  - 全链路四层阻断防护：
    - 桌面插件层拦截：`rooms.ts` 新增 `isBatchSession` 并在批处理生命周期内全程锁定；`cloud.ts` 与 `sync.ts` 在会话列表、推流过滤与变更广播阶段全方位丢弃批处理与动态标题会话
    - 桌面服务阻断：`nanomuse/sync/engine.py` 的 `_eligible` 增加动态标题前缀硬拦截
    - 自建中继防护：`cloud/nanomuse_cloud/sync.py` 在推送端增加动态会话拒绝逻辑，并在中继数据库中将历史 9 条动态残留会话批量标为墓碑并推进游标
    - 移动端双层过滤：`SyncEngine.kt` 丢弃远程动态标题；`LocalChats.kt` 与 `ChatRepository.kt` 在查询与展示层彻底过滤动态会话
  - 启动自愈与历史僵尸清理：
    - Android 端 `ConversationSync.init()` 引入启动自愈清理逻辑，自动扫描并彻底擦除本地数据库与同步引擎中的历史动态残留会话及消息记录
    - Android Debug APK 完成打包并通过 ADB 安装部署至 Redmi K60

- **NyanoMuse 服务商与模型多端配置端到端加密同步与冲突自愈系统落地 (2026-10-19, 完成)**:
  - 核心架构与端到端加密（E2EE）保障：
    - 自建服务端新增 `sync_configs` 存储表与 REST 接口（`GET/PUT /v1/sync/config`），采用零知识加密存储，中继仅负责中转密文与版本控制
    - 客户端使用 PBKDF2-HMAC-SHA256（100,000 次迭代）结合主账户 ID 派生 256 位密钥，通过 AES-256-GCM 进行认证加密
    - 手机端 `ConfigSync` 与桌面桥接器 `nanomuse-bridge` 双端均实现本地自动快照备份（`backups/configs/`），防止异常合并
  - 同步范围与负向排除范围：
    - 同步对象：AI 服务商实例配置（`providers`）、API 密钥、自定义 Base URL、核心模型插槽映射（`slots` 包括 chat、hands 等）及智能体人设与提示词（`SOUL.md`）
    - 负向排除范围：严格排除主题方案（Morandi、Sakura、OLED、默认蓝等）与聊天壁纸，两类属性 100% 仅保存在各设备本地，不参与多端漫游
  - 冲突处理与多端广播联动：
    - 版本控制采用单调递增版本号 `rev`，字段级合并遵循最后写入者胜（LWW）策略
    - 服务端通过 WebSocket Hub 实时广播 `config` 变更帧，多端接收后平滑解密并热更新本地存储与仓储实例
    - 移动端 `CloudAccountScreen` 增加 E2EE 配置同步状态与密码设置交互，Android APK 编译通过并已部署至 Redmi K60

- **NyanoMuse 单用户独占服务端锁定、Grok-bot科技感默认立绘全面替换与全栈去额度化 (2026-10-19, 完成)**:
  - 自建服务端单用户独占安全锁定：
    - `config.py` 新增 `single_user` 开关（自建中继默认开启）
    - `service.py` 严格校验账户数，当已有所有者账户时立即抛出 403 `registration_closed` 拒绝任何后续新用户注册
    - 清理服务端历史冗余测试账户，将黑猫形象、名字与会话数据全量平移至当前唯一所有者账户 `lanrhyme`（版本提升至 rev 15 触发多端即时覆盖更新）
  - 全局默认形象全面重构为 Grok-bot 科技机器人：
    - 彻底剔除全工程奶龙（custard dragon）资源，由极简暗黑赛博 Grok 风格发光机器人接管（涵盖 idle/working/waiting/happy/error 五种状态 1024x1024 纯净 WebP）
    - 移动端 `AgentAvatar` 与 Web 前端剔除旧版 MP4 动画依赖，由 Compose 与 CSS 原生弹性物理动画驱动
    - 移动端全语种 `nm_avatar_default_description` 与 Web 前端文案同步更新为科技机器人设定
  - 移动端与 Web 端去额度化与品牌深度重构：
    - 移动端 `CloudAccountScreen` 彻底剥离额度池进度条、用量明细分类、好友邀请码与 Star 弹窗组件，专注设备会话管理与自建同步
    - Web 前端完成 NyanoMuse 全局品牌文案重构，重新编译并打包静态资源至 `nanomuse/server/static/`
    - Electron 桌面原生包完成编译并部署至 `~/.local/opt/nyanomuse/`，Android Debug APK 构建完成

- **NyanoMuse 手机号短信登录全面清除、自建中继直连IP与账号密码认证落地 (2026-10-19, 完成)**:
  - 手机号短信与邀请码彻底剔除：
    - 全面清除移动端、桌面与 Web 端的中国大陆手机号限制、海外号段拦截告警、短信验证码获取、60秒倒计时及好友邀请码逻辑
    - 登录界面全面重构为「服务器地址 (IP/域名) + 用户名/账号 + 密码」直连模式，提供即时连接可用性检测
  - 自建中继后端认证全流程打通：
    - 中继 `identifiers.py` 扩展支持通用用户名（`user` 渠道），不再强制要求邮箱或手机号正则
    - `service.py` 优化自建服务下的密码认证，开放注册模式下首次使用账号密码登录自动创建账号并写入哈希，彻底摆脱短信初始化依赖
    - 桌面端 Electron、Web 前端与 Android 客户端完成全量重构与构建，ADB 部署至 Redmi K60 并推送远端（`5c278c8a`）

- **NyanoMuse 官方云服务彻底剥离、代码私有地址脱敏、设置层级重构与导航条透明渲染 (2026-10-19, 完成)**:
  - 代码库私有地址彻底脱敏：
    - 全面清除代码库中所有硬编码的自建中继域名与官方云地址，改为由环境变量（`NYANOMUSE_RELAY_URL` / `NANOMUSE_CLOUD_URL`）、用户本地输入或配置文件动态解析，代码库保持绝对纯净开源规范
  - 官方云服务与 branding 剥离：
    - 移动端、桌面与 Web 端剥离 nanoCloud 官方云依赖，仅保留自建中继服务器（Self-Hosted Relay）连接模式
    - 界面标题与文案统一重构为「自建服务与多端同步」，清除服务器重置逻辑不再回退到任何私有硬编码
  - Android 设置页面层级重构：
    - 按照模型与中继服务、智能体人设与能力、跨设备协同与控制、系统执行与权限、界面网络与数据、关于与支持 6 大板块进行 MuseSectionLabel 结构重整，信息架构清晰易读
  - 手机端壁纸导航栏黑边根治：
    - 排查定位 `MuseBottomBar` 中的 `amoledNavPillSurround` 在有壁纸时依然强制裁剪并绘制纯黑底色覆盖导航栏缝隙的问题
    - 增加 `!hasWallpaper` 守卫条件，在启用聊天背景壁纸时使胶囊导航条外侧及屏幕底端系统手势区实现完全透通渲染
  - 部署与推送：
    - Android Debug APK 重新编译通过并通过 ADB 静默安装至 Redmi K60（`ed3fdd92`）
    - 桌面端 Electron 原生包重新打补丁并构建更新至 `~/.local/opt/nyanomuse/`
    - Git 提交规范化推送至 GitHub `main` 分支（`8627ff1e`）

- **NyanoMuse 品牌包名全面重构、Android 数据无缝迁移与 Electron 桌面端原生构建部署 (2026-10-19, 完成)**:
  - 品牌与包名全栈重构：
    - 应用显示名称全端统一为 `NyanoMuse`（涵盖 Android 17 种语言资源、Web 前端与桌面窗口菜单）
    - Android 端包名与 Application ID 由 `io.github.nanomuse.app` 彻底变更为 `top.lanrhyme.nyanomuse`，快捷方式与广播接收器动作全面切为 `top.lanrhyme.nyanomuse.*`
    - 桌面端 AppId 设为 `top.lanrhyme.nyanomuse.desktop`，可执行文件命名为 `nyanomuse-desktop`
    - 数据主目录全面迁至 `~/.nyanomuse`，桌面配置与状态路径平滑过渡
  - Android 移动端（Redmi K60 / ed3fdd92）无缝数据迁移：
    - ADB 交互严格执行非前台避让原则，在用户使用前台（Bilibili）期间执行全静默后台作业
    - 通过 root 权限全量备份原应用数据目录（SQLite 数据库、files、shared_prefs），安装新版 APK 后恢复并修正 `u0_a545` 属主与 SELinux MLS 安全标签
    - 卸载旧版 `io.github.nanomuse.app` 并清理临时备份，广播接收器 `RELOAD_CONFIG` 校验成功
  - 桌面端 Electron 构建与深度系统集成：
    - 使用 `pnpm` 编译 `dsh-nanomuse` 插件层并注入 DeepSeek Harness 运行时依赖
    - 运行 `electron-builder --dir` 编译生成原生 Linux 目录版本（`linux-unpacked`），彻底规避 AppImage 与 FUSE 开销，部署至 `~/.local/opt/nyanomuse/`
    - 建立 `~/.local/bin/nyanomuse` 主执行链接与防递归 MCP 包装脚本，部署 `~/.local/share/applications/nyanomuse.desktop` 桌面项
    - 迁移 `~/.nanomuse` 至 `~/.nyanomuse` 并保留软链接向后兼容
    - Chezmoi dotfiles 同步更新 Niri 窗口规则（`rules.kdl` 支持 `nyanomuse-desktop` 隔离至后台工作区 `bg` 且不抢占焦点）与自启（`autostart.kdl`）
  - 外部 AI 桥接联动：
    - `nanomuse-bridge.py` 同步支持 `~/.nyanomuse` 优先与 `top.lanrhyme.nyanomuse` 广播，创建双向命令别名 `nyanomuse-bridge`

- **NyanoMuse 官方服务彻底剥离、自定义立绘包导入与外部 AI 自由配置系统上线 (2026-10-19, 完成)**:
  - 官方依赖清空与自建云端锁死：
    - 全面剔除所有指向官方 `cloud.nanomuse.cn` 与 `nanomuse.cn` 的硬编码中继地址、下载检查与遥测通道，默认全面切为自建高可用中继 `https://nyanomuse.lanrhyme.top`
    - 更新检查与文档完全回退并接入 GitHub 官方仓库 `https://github.com/LanRhyme/NyanoMuse`，遥测与数据贡献开关默认关闭，杜绝任何外部数据外泄
  - 自定义多状态立绘包导入系统（全端就绪）：
    - Android 端新增 `AvatarPackImporter`，支持解压 ZIP 压缩包或读取本地图片，自动语义识别 `idle`、`working`、`waiting`、`happy`、`error` 5 种表情状态，硬件级裁剪缩放为 512x512 WebP 并写入 `AvatarStore`，同时联动 `ProfileSync` 自动推送云端中继
    - `AvatarStudioScreen` 新增显式「导入立绘包 (ZIP/多图)」快速操作按钮与菜单项
    - 桌面与 Web 端支持通过桥接工具直接打包注入与即时全端漫游，全套 5 状态黑猫立绘包（`~/tmp/nyanomuse_avatar_pack.zip`，哈希 `1e9abf11ff90`）已成功固化到桌面并同步至自建中继与手机端
  - 外部 AI 自由配置与双向热重载桥接系统：
    - 打造 `nanomuse-bridge` CLI 工具（软链接至 `~/.local/bin/nanomuse-bridge`），赋予外部 AI 代理（Antigravity、Claude Code 等）对 `SOUL.md`、`profile.json`、`cloud.json`、模型提供商与立绘资源的无沙箱全权控制与命令行读写能力
    - Android 端实现 `ExternalAiReceiver` 广播接收器，外部脚本或 ADB 可通过 `io.github.nanomuse.UPDATE_SOUL`、`io.github.nanomuse.IMPORT_AVATAR`、`io.github.nanomuse.UPDATE_RELAY` 和 `io.github.nanomuse.RELOAD_CONFIG` 动作实现免重启热注入
    - 撰写并提交 `docs/zh/ai-bridge.md` 开发者规范，严格恪守无句号无表情符号规则
  - 部署与验证：
    - Android Debug APK 完成打包并经 ADB 静默安装至 Redmi K60（`ed3fdd92`），避开前台用户活跃应用，广播注入 SOUL 设定与立绘包成功
    - 桌面端 Web 前端 Vite 重新打包输出至 `nanomuse/server/static/`
    - 所有改动经 Git 规范化提交（`feat: 剔除官方服务依赖、支持自定义立绘包导入与外部 AI 自由配置接口`）并推送至 GitHub 远端 `799fde16`

- **NyanoMuse 多预设主题、聊天壁纸、毛玻璃特效与工具系统全面进化 (2026-10-19, 全端就绪)**:
  - 主题与调色盘系统（移动端与桌面/Web端同步）：
    - 预设色调引擎：莫兰迪 Morandi（默认暖灰/鼠尾草护眼）、OLED 纯黑（极致对比度与节能）、猫猫暖樱 Sakura Pink（甜美粉嫩萌系专属）、经典蓝 Default Blue，以及 Android 12+ Material You / Monet 动态壁纸取色
    - Android 端由 `ThemePalette` 与 `ThemePalettes` 驱动全局 `ColorScheme` 与 `ChatPalette` 解析，`AppearanceScreen` 提供色块可视化切换并实时联动 Compose 全局重组
    - 桌面与 Web 端由 `theme.ts` 与 `index.css` 提供 `data-palette` 与 CSS 变量切换，在 Settings 的 Appearance 中提供图形化选项
  - 聊天背景壁纸与毛玻璃效果系统（移动端与桌面/Web端同步）：
    - 移动端由 `ChatWallpaperManager` 集中管理图片持久化存储、暗化蒙版（0% 至 85%）与高斯模糊（0 至 25dp），在 `ChatScreen` 底层以 `AsyncImage` 与硬件级模糊分层渲染
    - 桌面与 Web 端支持本地图片上传至 `localStorage`，支持暗化遮罩与模糊滑块调节，结合 CSS `backdrop-filter` 与 `color-mix` 落地全景半透明亚克力与 Mica 毛玻璃质感（`data-glass`）
  - 工具系统全方位进化（Android 原生工具库与自愈管线）：
    - 新增 `device_info`：免 Root/有 Root 双通只读工具，读取设备电池电量、充电状态、RAM 与内置存储空间利用率、网络连接类型与系统内核环境
    - 新增 `app_launch`：支持按包名或按中英文应用名称模糊检索并启动已安装应用（如微信、设置、相机等）
    - 新增 `system_notify`：支持发送带 nanoMuse 专属头像图标的系统状态栏通知或即时 Toast 提示
    - 智能容错自愈：新增 `ToolSelfHealing`，在工具失败时根据失败模式自动注入文件搜索、PATH 缺失排查及 su 权限指导等自愈提示，防止模型盲目重复失败
    - 测试与构建：Android 全量单元测试 `testDebugUnitTest` 100% 绿色通过，桌面/Web 端 Vite 生产构建与 18 个测试套件 112 项测试全数通过，改动已提交并推送至 `LanRhyme/NyanoMuse` 的 main 分支
  - 桌面端自建中继适配与本地配置（2026-10-19，完成）：
    - 桌面端彻底剔除 nanoMuse Cloud 专有文案与残留配置，设置项导航与文案变更为自建同步服务
    - 登录界面改用服务器地址、用户名与密码验证体系，移除短信验证码与邀请码残留
    - 桌面端主进程与插件支持从本地 `~/.nyanomuse/desktop/desktop.json`（`relayUrl`）或 `environment.d` 读取私有服务器地址直连
    - 全面剔除账户页面的额度池（Allowance）、用量明细（Usage）、邀请好友（Invite）与 Star 弹窗组件，停用 80% 额度预警
    - 本地清除历史官方云残留会话（cloud.json 与 .credentials.yaml 中的旧 Token），确保桌面端处于未登录净态
    - 全量单测 333 项测试通过，完成 Electron 桌面端构建并热部署至 `~/.local/opt/nyanomuse/`
  - 平板端（一加平板 2 Pro / OPD2413）完成 NyanoMuse 最新版 APK 安装与原 io.github.nanomuse.app 全量数据无缝迁移，电池优化白名单与后台权限已配置完成

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
  - 键鼠输入动态自愈与全桌面优先：排查开机随 systemd 启动（开启 linger）时因图形界面尚未完全建立被误判为 X11 后端，原逻辑跳过 uinput 初始化且写死旧状态，导致后续连入时向 Wayland 盲目调用 X11 XTest 接口失败（日志狂报 `Desktop mouse injection failed: -1`、`Pointer button audit: result=-1`），键鼠完全瘫痪；修复方案：1. `src/uinput.rs` 中 `wanted` 调整为全桌面默认优先使用内核 uinput；2. `src/input.rs` 将 `InputInjector` 的 `uinput` 设备改为 `Mutex<Option<Devices>>` 并引入 `with_uinput` 惰性自愈探测，未打开时每次事件触发动态补建；3. 废除写死的 `backend` 字段，改用 `current_backend()` 实时感知桌面合成器状态；4. `systemd` 服务补充 `Environment=UU_INPUT_BACKEND=uinput` 并重新编译部署
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
