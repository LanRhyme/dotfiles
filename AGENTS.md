# LanRhyme 的 AI 代理系统指南

以下规则定义了用户的系统架构、偏好和配置/修改环境时的强制流程，所有代理必须严格遵守

## 1. 系统架构与包管理
- **操作系统**: Arch Linux（CachyOS）
- **包管理器**: 使用 `paru` 管理 AUR 包，使用 `pacman` 管理官方仓库，安装包时使用 `--noconfirm`
- **显示服务器与窗口管理器**: Wayland + `niri`（合成器）
- **桌面元素**: `noctalia`（状态栏）、`kando`（饼状菜单）

## 2. 全局主题引擎（莫兰迪主题）
- 系统使用一个集中的、动态的主题生成器（Python 编写），监听壁纸变化生成"莫兰迪"（低饱和度、暖/冷色调）颜色
- **核心脚本位置**: `~/.config/noctalia/morandi-gen.py`
- **规则**: 当被要求为主题化新应用或修改 UI 颜色时，**不要**直接编辑应用的配置文件，而**必须**扩展 `morandi-gen.py`，添加一个 `write_<app>` 函数解析应用配置并注入 `palette` 字典颜色，在 `main()` 中调用它，然后运行脚本，这确保应用在未来壁纸变化时自动同步

## 3. 配置管理（Chezmoi）
- **工具**: 使用 `chezmoi` 管理 dotfiles
- **源仓库**: `~/.local/share/chezmoi`
- **规则**: 修改系统配置文件（如 `~/.config/app/config`）时，必须确保变更提交到 dotfiles 仓库，专用同步脚本位于 `~/.local/bin/dotfiles-sync.sh`，在应用和测试任何 dotfile 修改后立即运行此脚本
- **规则**: 如果直接在 `~/.config` 中编辑脚本，记得先编辑 `~/.local/share/chezmoi` 中的源文件再复制过去，或者如果编辑了本地副本则运行 `chezmoi re-add`

## 4. 文档与写作偏好
- **格式规则**: 编写或更新 `README.md` 文件或 markdown 文档时，**绝不**使用句号，**绝不**使用表情符号，保持简洁和极简
- **语气**: 对话回复保持简洁、直接和专业

## 5. 存储与文件系统
- 系统可访问 Windows 分区：
  - Windows C 盘: `/mnt/WindowsC`
  - Windows D 盘: `/mnt/WindowsD`
- 搜索外部 VST、游戏或 Windows 配置时，始终检查这些挂载点
- **临时文件规则**: 家目录 `~` 必须保持干净，**绝不**在 `~` 直接创建临时文件、草稿、构建产物、下载残留或一次性脚本，所有临时输出一律写入 `~/tmp`（不存在则先创建），需对外暴露的系统级临时目录仍用 `/tmp`，但用户工作产物默认放 `~/tmp`

## 6. PKGBUILD 安全审查
- **规则**: 代替用户安装 AUR 或第三方软件时，**必须**先获取并审查 PKGBUILD，确认安全后再继续安装
- **检查内容**: 审查 `build()`、`package()` 和安装钩子（`.install` 文件、`post_install`、`pre_install`）中的可疑操作，例如：
  - 不受限制的 `rm -rf` 或破坏性文件操作
  - 向未知域名发起的异常网络请求
  - 隐藏的 `post_install` 逻辑或混淆命令
  - 可疑的权限变更（如 `chmod 777`、非标准二进制文件的 `setuid`）
  - 过多或不必要的依赖
- **处理**: 确认 PKGBUILD 安全后才继续安装，将任何发现报告给用户

## 7. 配置记忆与上下文（MEMORY.md）
- **概念**: 为促进无缝的配置工作并跨会话维护上下文，代理必须使用集中的记忆文件
- **位置**: `~/MEMORY.md`
- **读取规则**: 修改 dotfile 或开始配置任务前，**必须**读取 `~/MEMORY.md` 以了解用户的当前配置状态、进行中的任务和结构偏好
- **写入规则**: 当用户引入新的系统组件、建立配置模式（如路径管理方式）或留下未完成的任务时，**必须**更新 `~/MEMORY.md`，保持其聚焦于当前架构、活跃 TODO 和对进行中配置工作至关重要的特定环境状态

## 8. 提交信息规范
- **规则**: 所有 Git 提交信息**必须**使用中文书写，遵循标准化提交格式：`<类型>: <简要描述>`
- **类型**: `feat`（功能）、`fix`（修复）、`refactor`（重构）、`style`（样式）、`docs`（文档）、`chore`（杂项）
- **示例**: `feat: 添加暗色模式支持`、`fix: 修复登录页面崩溃问题`、`refactor: 重构主题引擎配色方案`

## 9. 移动设备系统更新与 Root 维护规范

### 9.1 通用前置准则与全生命周期规范
- **全生命周期闭环**: 代理在介入任何移动设备更新任务时，必须严格执行「更新前提取备份与镜像校验 → 更新中标准刷入流程 → 更新后自动恢复 Zygisk/Vector/HMA 隐匿链」
- **镜像备份铁律**: 刷机或更新前，必须通过 Root Shell 提取原厂当前槽位的官方纯净底包镜像，归档保存在电脑本地对应机型目录（如 `~/刷机/<机型>/原厂备份/`）与设备内部存储，严禁在无底包备份状态下盲目刷入修改后镜像
- **后置复验检查单**:
  - 执行 `/data/adb/ksu/bin/znctl status`，确认 Zygisk Next 的 `enforce_denylist` 处于 `disabled`（值为 0），防止普通应用被隔离无法注入 Vector
  - 检查 Vector 守护进程服务脚本 `/data/adb/modules/zygisk_vector/service.sh`，确保使用 `unshare -m` 而非 toybox 不支持的 `--propagation slave`
  - 运行 `android-hide-app -l` 校验目标应用（如金融、游戏）的防检测名单与 Tricky Store 目标列表完整性
  - 彻底排查不兼容的遗留模块，坚决避免因 Android 大版本更新（如 Android 16/17）导致系统服务崩溃

### 9.2 红米 K60 (mondrian / ed3fdd92) 专属流程
- **系统架构**: Android 17 / HyperOS 4 移植版（NexusHyper / 官方底包 OS4.0.0.7.XMNCNXM），内核 5.10.252-dirty，KernelSU-Next (LKM GKI2)
- **更新前准备**:
  - 从 OTA 增量或完整包中解压 `images/boot_a.img` 或 `boot.img`
  - 使用对应内核版本与 `android12-5.10` KMI，将 KernelSU-Next LKM 驱动与专属签名注入底包，生成 `boot_ksunext_*.img`（严禁使用签名不匹配的旧 LKM 驱动，否则触发 Seccomp 拦截报未安装）
  - 本地与手机保留修补后镜像及原厂纯净镜像备份
- **更新与刷入流程**:
  - 在 Fastboot 模式下直刷修改后的 boot 镜像到目标分区（如 `fastboot flash boot_ab boot_ksunext_*.img`）
  - 开机后进入 adb 检查并更新 `/data/adb/ksud` 二进制版本
- **专属避坑与注意事项**:
  - **模块 API 审查**: Android 17 (SDK 37) 环境下，硬编码判断 `SDK_INT <= 36` 的旧模块（如 Thanox）会触发 NPE 崩溃，严禁开机自启；OEM 应用（如相机）更新后混淆类名变更需适配更新 Hook 点
  - **虚拟距离传感器修复**: 该机型采用 Goodix 触摸固件与 xiaomi_touch 融合的虚拟距离传感器，若日常使用出现亮屏/灭屏误触发，执行 `su -c sh /data/local/tmp/fix_prox.sh` 并重启
  - **ADB 交互规范**: 锁屏抽屉易卡住，执行 adb 指令前先核对 `dumpsys window mCurrentFocus`，用户使用前台操作手机时绝不抢占界面

### 9.3 一加平板 2 Pro (OPD2413 / c84b9192) 核心规范
- **系统架构**: ColorOS 16 (Android 16 / SDK 36)，骁龙 8 至尊版 (SM8750P / sun 平台)，SpiderDroid GKI 6.6.118 定制内核，KowSU Pro (35700-2 / UAPI=2) + 内核内置 SuSFS 2.3.0
- **绝对禁忌红线（Hard Block，前置强力阻断）**:
  - **严禁跨版本或降级刷机**: 严禁执行任何低版本降级操作，防止触发高通骁龙 8 至尊版与 OPPO 硬件级 ARB (Anti-Rollback) 硬件熔断变砖，检测到降级需求必须直接阻断
  - **严禁刷入第三方 Recovery**: 平板依赖官方 ColorOS Recovery 与双槽位（Slot A/B）无缝升级机制，第三方 Recovery 会破坏 OTA 校验链与加密分区，必须永久使用官方 Recovery
  - **严禁使用手机端防误触与触控旁路补丁**: 严禁安装 `patch-trackmotion`、`disable-stylus-blocker` 等外挂触控模块，此类补丁会破坏平板原生防误触算法并导致手写笔压感失效
- **更新前准备与镜像打包标准**:
  - 备份提取：更新前必须从活动槽位（`boot_b`/`init_boot_b`）完整提取官方底包，归档至 `~/刷机/一加平板2Pro/原厂备份/`
  - **AVB 2.0 校验尾部注入**: 骁龙 8 至尊版 ABL 强校验标准 AVB 签名，替换定制内核时必须使用 raw ARM64 `Image` 并调用 `avbtool add_hash_footer` 注入 Hash Footer（boot 分区尺寸严格设定为 96MB / 100663296 字节）
- **音频系统与防检测更新要点**:
  - **音频架构红线**: ColorOS 16 采用 AIDL Audio Effect HAL 架构，旧版 JamesDSP (HIDL 架构) 存在断代冲突会导致系统音频服务崩溃闪退，系统更新后严禁安装遗留 JamesDSP 模块
  - **一键防检测恢复**: 系统更新后直接调用 `android-hide-app` 校验或快速重新注入《三角洲行动》等关键应用的防检测规则，无需任何屏幕触摸交互
