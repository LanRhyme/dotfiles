# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

- **网易 UU 远程 Linux 被控端部署、Wayland 适配、移动端中文输入法与按键映射修复 (2026-10-16, 配置完成)**:
  - 架构与安装：AUR `uu-remote-bin` 基础环境；拉取官方最新源码 (v0.1.22) 启用 `--features wayland,portal` 重新编译优化版二进制，替换 `/usr/bin/uuremote-server` 解决预编译包不支持 Wayland 桌面串流问题
  - 权限与输入：部署 `/usr/lib/udev/rules.d/60-uu-remote-linux-uinput.rules` 赋予 `/dev/uinput` 用户级访问权限，内核级注入虚拟键鼠，绕过 Wayland 输入隔离限制
  - 移动端中文输入法队列化与吞字根治：原并发异步任务在连续快速输入时会导致多个剪贴板进程与 Ctrl+V 按键事件竞态，后到达字符覆写尚未粘贴的前序内容造成吞字；重构为专属 FIFO 异步合并队列，快速连击时自动将多个待上屏字符合并为单次原子写入，并将按键时序深度压缩至毫秒级，彻底消除吞字掉字与输入迟滞
  - 串流超低延迟硬件加速：排查发现双显卡环境下因 FFmpeg 编译版本（nv-codec-headers 13.1）与当前 NVIDIA 580 驱动（13.0 API）不兼容导致 hevc_nvenc 启动失败并退化为 CPU 软解（libx265），造成 200% CPU 占用与显著串流延迟；配置 `LIBVA_DRIVER_NAME=iHD` 与 `UU_VIDEO_ENCODER=vaapi` 激活 Intel 核显 QuickSync 原生硬件编码，单帧硬件编码耗时骤降至毫秒级，彻底解决远程控制高延迟与卡顿
  - 游戏按键映射与触控轮盘协议修复：逆向 Windows 服务端发现 mobile 客户端下发的 input_keys 并非整型数组，而是包含 `[{"input_device":"keyboard","input_code":65}]` 或其 JSON 序列化字符串，原数组解析返回 None 导致 keys 为空；重构 parse_input_keys 兼容对象数组、内联 JSON 字符串及逗号分隔格式，将 keyboard 与 mouse 设备精准分发至虚拟键盘按键与虚拟鼠标点击
  - 凭据与常驻：登录凭据存储于 `~/.config/uuremote/config.json`；启用 systemd 用户服务 `uu-remote-native.service` 实现开机自动登录并常驻连接网易远控网络

- **IntelliJ IDEA 莫兰迪配色与主题引擎集成 (2026-10-15, 配置完成)**:
  - 主题架构：在 `~/.config/noctalia/morandi-gen.py` 扩展 `write_idea(palette)`，生成独立的编辑器配色方案（`Morandi.icls`）与配套 UI 主题插件包（`morandi-theme.jar`）
  - 配色注入：编辑器方案映射关键字（rose）、字符串（gold）、数值（peach）、函数（foam）、类接口（sky）、注释（overlay1/pine）与界面基底（base/surface/text），UI 主题包注册 `morandi.dark` 主题并链接配色方案
  - 自动同步：在 `main()` 接入 `write_idea`，随壁纸与系统调色板变更自动重载更新，并在 `colors.scheme.xml` 与 `laf.xml` 中激活

- **IntelliJ IDEA 界面语言切换为简体中文 (2026-10-15, 配置完成)**:
  - 根因：Arch Linux 官方仓库 `intellij-idea-community-edition` (Build IC-262.10968.63) 采用开源源码构建，未内置专有语言包且插件商店因构建号兼容性校验过滤了语言包
  - 插件部署：提取官方中文语言包（Chinese (Simplified) Language Pack / `com.intellij.zh`），解除 `until-build` 兼容性约束后部署至 `~/.local/share/JetBrains/IdeaIC2026.2/zh/lib/zh.jar`
  - 本地化配置：在 `~/.config/JetBrains/IdeaIC2026.2/options/ide.general.xml` 配置 `LocalizationStateService` 为 `zh-CN`，在 `~/.config/JetBrains/IdeaIC2026.2/idea64.vmoptions` 写入 `-Duser.language=zh` 与 `-Duser.country=CN`

- **ReveriePaint v1.4.0 版本发布与全量架构升级 (2026-10-02, 发布完成)**:
  - 版本号与构建体系：版本号自 1.3.10 (27) 升级至 1.4.0 (28)，打标签 `v1.4.0` 并推送至 GitHub 触发 Release 打包工作流
  - 核心功能升级集成：集成快捷笔刷悬浮面板、快捷操作悬浮面板、防崩溃快照恢复系统、Procreate 风格动态流动斑马纹选区与黑白相间矢量流动蚂蚁线系统、界面动效速度设置三档调节、边缘侧滑返回手势与起笔防误画优化
  - 核心崩溃与视觉修复：修复多步撤销 Swap 溢出崩溃、Android MotionPredictor 原生 Abort 崩溃、渲染线程与后台异步合并器（KisAsyncMerger）写瓦片竞态崩溃、变换预览与图层缩略图 NEON 矢量加速透明度预乘泛光过曝修复，并通过 -PbuildNative 重编最新 native 动态库与符号注入

- **ReveriePaint 选区 Procreate 风格动态斑马纹与流动蚂蚁线升级及创建后不显示修复 (2026-10-02, 实现完成)**:
  - 增加选区失效根因排查与修复：进入选区工具后画出首个选区，使用「增加」模式追加新选区时旧选区被冲掉；排查发现三重诱因：1. `loadToolOptions` 仅恢复 Kotlin 变量未向 C++ 底层下发 `setSelectionMode` 导致 native 默认为 SelReplace (0)；2. `applyTool` 切入选区工具时未同步模式；3. C++ 底层 `selectShape` 与 `selectPolygon` 依赖 `hasSelection()` 且 `selectedExactRect()` 未及时缓存时误判为空强行 fallback 为替换；在 `applyTool` 与 `loadToolOptions` 建立向 C++ 实时同步机制，并在 C++ 底层对 `oldMask` 实施直接非零像素安全扫描，彻底根除新旧选区追加丢失问题
  - 选区创建完成后不显示与流动蚂蚁线丢失修复：排查定位用户在创建选区后画面无显示的深层根因：1. `buildSelectionOverlayLocked` 在后台渲染线程直接向 Compose 状态 `selectionOutlinePath` 赋值，缺少 Snapshot apply 导致主线程无法感知变更，引入 `@Volatile pendingSelectionOutlinePath` 并在主线程 `after = { ... }` 回调安全发布，同时接入向量兜底路径 fallbackPath；2. Gradle 构建系统默认使用 `third_party/android-native-libs/libreverie_jni.so` 预编译二进制，此前在 C++ 新增的 `selectionOutline()` 导出符号未编入 prebuilt SO，导致 JNI 调用触发静默异常或中断，使用 `-PbuildNative` 重新编译 native 库并同步更新 prebuilt SO，并在 Kotlin 端增加容错捕获；3. 斑马纹维持低对比度 Procreate 原生柔和质感（暗阶 18% 对亮阶 8%）；4. 覆盖安装后关闭后台旧进程残留，确保设备启动时完整载入全新 native 动态库与 DEX
  - 矢量选区轮廓提取管道：在 C++ 端新增 `ReverieCore::selectionOutline()` 与 JNI 导出，直接调用 Krita `KisPixelSelection::outline()` 获取高精度封闭多边形轮廓顶点向量，以紧凑整型数组序列化回传给 Kotlin 并在 `buildSelectionOverlayLocked` 转换缓存为 Compose 矢量 `Path`（自动对齐文档与视口坐标），实现缩放旋转无损零光栅化失真
  - Procreate 风格动态流动斑马纹与低对比度调优：重构 `CanvasOverlay` 选区视觉表现，在选区工具组（`ToolGroup.SELECTION`）内对未选区遮罩采用 45 度斜向动态流动半透明斑马纹，复刻 Procreate 水印般的微光暗影质感；通过 Skia `saveLayer` 配合 `PorterDuff.Mode.DST_IN` 实时镂空选中区域，并结合画布缩放/旋转逆变换保持物理屏幕 1:1 像素密度与严格 45 度视角；切到画笔/橡皮擦/涂抹等非选区工具时自动隐藏斑马纹遮罩，释放作画视野
  - 选区创建全流程 Procreate 风格化：在套索绘制（自由/折线）、多边形、矩形与椭圆创建拖拽全阶段，彻底移除高对比彩色填充（accent/红/绿），统一接入反向实时斑马纹预览管线；在离屏缓冲层（Skia `saveLayer`）预填全屏动态斑马纹，在拖拽与绘制未闭合或预览路径内部实时以 `PorterDuff.Mode.CLEAR` 极速镂空透明像素，实现画笔绘制区域内部原作清晰透出、选区外侧即时被动态斑马纹遮蔽的原生交互体验；减选模式直接在路径上覆写斑马纹，交集模式采用 API 26+ `clipOutPath` / `clipOutRect`，创建中几何轮廓全链路无缝同步黑白交替流动蚂蚁线与起点闭合圆点
  - 选区蒙版设置精简：完全移除通用设置页面冗余的「选区蒙版颜色」预设色卡与自定义拾色器弹窗，保留「选区蒙版不透明度」滑块并动态调制斑马纹整体透光度
  - 动态黑白交替流动蚂蚁线：无论在选区工具内还是切出至常规绘画工具，只要存在活动选区，选区边缘均常驻显示动态流动的黑白交替虚线蚂蚁线；在编选区（实时套索、折线套索、多边形选择、矩形/椭圆框选）全链路统一接入单帧无限流动时间线（LinearEasing 1200ms 无缝循环），并在无活动选区时旁路读取零重绘开销

- **ReveriePaint 变形预览与图层缩略图未预乘透明度泛光过曝修复 (2026-10-02, 修复完成)**:
  - 根因排查（Issue #33）：套索后调起变换工具时，半透明及边缘抗锯齿画笔笔画在变换预览阶段呈现 100% 刺眼纯白及杂边泛光（过曝发光），变换提交后即恢复正常；排查确认 Krita 的 `KisPaintDevice` 底层使用直通透明度（Straight Alpha），C++ 预览提取（`startTransformPreview`）及图层缩略图（`renderLayerThumb`、`renderKeyframeThumb`、`renderKeyframeFull`）直接采用非预乘格式 `QImage::Format_RGBA8888` 导出并拷入 Android `Bitmap.Config.ARGB_8888`；由于 Android Skia Canvas 与硬件加速渲染管线默认设定 `hasPremultiplied() == true`，在 `SRC_OVER` 混合阶段按预乘公式 `dst_rgb = src_rgb + dst_rgb * (1 - src_a)` 进行运算，导致未预乘的 RGB 颜色被未衰减全额累加，产生强烈的加色泛光过曝现象
  - 变形预览预乘与 ARM NEON 矢量加速：在 `ReverieCoreInternal.h` 实现高效矢量化转换函数 `blitBgraToRgbaPremultipliedFast`，利用 ARM NEON `vld4_u8` 将直通 BGRA 像素拆分至独立寄存器，通过 `vmull_u8` 与定点精度舍入公式 `((val + 128) + ((val + 128) >> 8)) >> 8` 极速完成透明度预乘并对调 B/R 通道，最后由 `vst4_u8` 重新交织存入 `QImage::Format_RGBA8888_Premultiplied` 图像，实现零开销高质量像素预乘；在 Kotlin 端同步显式标记 `b.setPremultiplied(true)`
  - 图层与关键帧缩略图预乘修正：将 `ReverieCoreIO.cpp` 中的 `renderLayerThumb` 输出画布格式从 `Format_RGBA8888` 升级为 `Format_RGBA8888_Premultiplied`，利用 Qt 绘图引擎直接在缩略图采样与绘制阶段完成高质量预乘合成；同步将 `ReverieCoreAnimation.cpp` 中的关键帧缩略图 `renderKeyframeThumb` 与洋葱皮全帧导出 `renderKeyframeFull` 升级为预乘格式，彻底根治图层面板透明棋盘格背景上的白色泛光杂边与描边过曝瑕疵

- **ReveriePaint 快捷笔刷悬浮面板与常用画笔管理工具 (2026-10-02, 实现完成)**:
  - 工具体系与独立入口：在 `Tool` 枚举体系中新增专用视图类工具「快捷笔刷」（`Tool.QUICK_BRUSH`），在侧边工具条 `ToolRail` 与全部工具面板 `AllToolsPanel` 中提供独立入口，点击即呼出悬浮面板并联动高亮状态
  - 极简单行胶囊悬浮窗：实现 `QuickBrushWindow`，默认以极简横向单行流线胶囊呈现常用画笔缩略图；支持横向与纵向两种单列布局形态切换，支持自由拖拽平移与屏幕边缘边界自适应吸附防出界；支持一键折叠收缩为半透明悬浮微球，点击微球丝滑展开
  - 默认屏幕居中定位与防出界钳位：重构快捷笔刷浮窗与快捷操作浮窗（`QuickActionWindow`）的初始坐标定位体系，将写死的偏角硬编码（60f/200f/280f）升级为未初始化/首次打开自动居中（`[screenWidth - width] / 2`）；在 `onSizeChanged` 与拖动全阶段引入屏幕边界动态钳位，彻底消除横竖屏翻转、形态展开折叠或初始化时悬浮窗半卡在屏幕边缘的问题
  - 即时切笔与就近微型气泡：点击任意画笔缩略图即时触发 `applyTool(Tool.BRUSH.id)` 与 `selectBrushPreset(preset.index)`，当前生效画笔呈现莫兰迪主题高亮光环与微弱缩放；悬浮窗旁自适应弹出就近微型 Toast 气泡展示画笔名称与分组信息，1.2 秒后平滑渐隐，给予精准操作反馈
  - 常用画笔管理与秒开优化：重构 `QuickBrushManageDialog`，剥离 500+ 全库预设重复扫描与分组计算，弹窗调起耗时从卡顿骤降至毫秒级瞬开；移除弹窗内冗余的库浏览添加模块，替换为优雅的极简操作提示横幅（引导在画笔面板星标或长按添加），并提供一键直达画笔面板快捷入口；保留常用笔刷列表的精细化上移、下移与移除管理
  - 面板最大长度与滚动浏览：新增 `quickBrushMaxLength` 设置（默认 6，支持 3~16 步进与 4/6/8/10/12 快速档位切换），当常用画笔数量超过设定的最大长度时，胶囊浮窗尺寸严格锁定在最大长度并在内部自动启用平滑滚动（LazyRow / LazyColumn），未超限时流线自适应贴合
  - 防误触拦截保护：在 `CanvasTouchView` 中注册快捷笔刷浮窗的实时动态几何边界，浮窗处于展开或折叠态时均严格拦截触控事件，防止拖动浮窗或点选画笔时在底层画布残留误画线条

- **ReveriePaint 防崩溃应急保存机制与最近自动保存快照恢复系统 (2026-10-02, 实现完成)**:
  - 无感绘画防卡顿保存门控：重构 `checkAutoSave` 触发管线，支持「5分钟定期兜底（伴随轻量 Toast）」与「25笔画/重大操作空闲静默快照（无 Toast）」双轨策略；严格执行三重门控阻断机制，在触控绘画进行中（`isInteracting`）、多指手势形变中（`isTransformActive`）、引擎队列非空（`pendingCoreOps > 0`）、滤镜预览活跃或落笔刚结束未满 4 秒（`sinceStrokeEnd < 4000ms`）时全面阻断保存触发，且在 `runCore` 执行前置再次复核，彻底杜绝自动保存抢占主线程或阻塞笔画导致掉帧卡顿
  - 崩溃应急拯救与 Native 标记：在 Java 层未捕获异常退出前（`CrashHandler.uncaughtException`）通过同步调用 `PaintViewModel.currentInstance?.emergencySaveOnCrash()` 抢救当前作画草稿并写入持久快照；在 C++ Native 崩溃拦截器（`ReverieCrashHandler.cpp`）中使用严格 async-signal-safe 系统调用向日志目录落盘 `CRASH_MARKER` 标记文件
  - 异常退出恢复对话框：在 `MainActivity` 启动流中异步扫描 `CRASH_MARKER` 与未落盘抢救草稿，检测到异常退出时弹出 Morandi 风格的 `CrashRecoveryDialog`，展示作品名称、备份时间与体积，支持一键恢复进画布或清理标记
  - 最近自动保存快照面板：实现 `AutoSaveHistoryManager` 滑动窗口持久化管理（严格保留最近 5 个独立工程快照），自动提取缩略图并生成元数据索引；在通用设置「自动保存」分组中新增「最近自动保存快照」入口，呼出 `RecentAutoSavesDialog` 支持查看快照卡片、缩略图、时间和体积，支持单项删除、一键清空，并提供「载入画布覆盖」与「新建为画廊副本」双恢复流程（带未保存改动防覆盖确认）

- **ReveriePaint 多步撤销Swap溢出崩溃与输入预测器原生Abort闪退修复 (2026-10-02, 修复完成)**:
  - 崩溃一根因与修复（Krita Swap与连续撤销）：用户连续撤销（25x Undo）时底层触发 `qFatal("KisChunkAllocator: out of swap space")` 导致 SIGABRT 进程自杀；排查发现 Krita 原生 `memorySoftLimitPercent` 默认仅为 2%（大内存设备上仅数十 MB 就会强制触发后台 `KisTileDataSwapper` 将历史撤销切片落盘到 flash），且 `KisChunkAllocator::getChunk` 在 swap 块耗尽时粗暴调用 `qFatal` 导致应用闪退；修复方案：在 `kis_chunk_allocator.cpp` 中将 `qFatal` 替换为 `qWarning` 并返回无效 chunk，在 `kis_swapped_data_store.cpp` 中对无效 chunk 优雅降级直接保留在内存中不强行释放（`trySwapOutTileData` 返回 false），在 `kis_image_config.cpp` 将默认软限制大幅调高至 50% 并将 `maxSwapSize` 默认提升至 8GB；在 ReveriePaint 端新增 `configureTileEngine` 明确配置应用专属 `cache/swap` 目录并联动软硬限制，在启动阶段自动异步清理历史残留的 `KRITA_SWAP_FILE_*` 僵尸文件（立清 360+ 个堆积文件，释放 80MB+ 缓存空间），安装自定义 `reverieQtMessageHandler` 将底层日志转发至 Logcat
  - 崩溃二根因与修复（Android MotionPredictor 原生 Abort）：用户使用导入画笔作画时在主线程触发 `libinput.so` 的 `android::MotionPredictor::record` 闪退；根因为 Android 14+ 系统的 `android.view.MotionPredictor` 底层依赖设备厂商内置的 TfLite 预测模型，在部分非原生/第三方 ROM 上模型缺失或硬件驱动不匹配时触发 C++ `LOG_ALWAYS_FATAL_IF` 强行 abort，Java 层的 try-catch 无法捕获；修复方案：彻底移除 `CanvasTouchView` 中对 `android.view.MotionPredictor` 的冗余回退调用，在 OPPO/一加等支持设备上维持官方验证的 `OplusMotionPredictor`，其余机型依靠引擎自带插值与平滑，彻底消除跨品牌机型的原生崩溃隐患

- **ReveriePaint 快捷操作悬浮面板与自定义配置系统 (2026-10-02, 实现完成)**:
  - 功能定位：在工具体系中新增独立工具「快捷操作」（Tool.SHORTCUT），在侧边工具条 ToolRail 与全部工具 AllToolsPanel 中提供直达入口，点击即呼出悬浮面板并联动高亮状态
  - 核心操作生态：全面支持 13 项高频绘画操作，包括锁定视角（固定缩放与旋转）、水平/垂直翻转画布、居中回正复位、撤销、重做、画笔与橡皮擦互切、上个工具互切、快速吸色、交换前背景色、笔刷尺寸增大/减小、Alpha透明锁（保护透明度）、新建图层、复制图层、向下合并、清空图层等，所有动作均具备实时状态反馈与激活高亮
  - 自适应形态与交互：支持横向单排胶囊、纵向单排胶囊、2列/3列圆角矩形自适应排布；顶部配备精巧微触把手，支持自由拖拽平移与一键微缩折叠为悬浮小胶囊球；深度集成 Morandi 配色系统与实时高斯毛玻璃效果（hazeChild）；在 CanvasTouchView 中接入边界命中防误画保护
  - 居中回正与就近反馈优化：重构 CanvasTouchView.animateFitCanvas 平滑复位动画，联动最短旋转角差（shortestDelta）与交互状态解锁，彻底修复居中回正无响应问题；新增悬浮窗自适应就近微型 Toast 提示，单列模式贴边侧出、横向与网格模式居中顶出/底出，伴随平滑弹簧伸缩与渐隐动效，点击动作即时给予局部视觉确认且不遮挡作画手势
  - 配置弹窗莫兰迪色彩统一、阴影内渗修复与实时预览卡片恢复：排查定位边缘与内部 box 色彩不一致根因为 Column 修饰符链中 .shadow() 误置于 .background() 之后，导致 Compose 提升层将 20dp 投射阴影直接渲染在面板底色上造成外圈 padding 区域色值异常发暗变脏（24, 24, 26），内部子项区域又呈现纯正 panel 底色（30, 29, 34）形成视觉断层框；修正为标准 shadow -> clip -> background -> glassBorder 链条，阴影完全投射到弹窗外部遮罩层，弹窗内外边缘实现 100% 纯正均一的 Morandi.panel 配色；完整恢复实时微缩效果预览卡片（QuickActionsPreviewCard），底色统一采用 Morandi.panelHi，实时响应排布模式（横向/纵向/网格）与文字标签显隐；平板双列模式左侧收拢排布设置与实时预览、右侧收拢已启用排序与候选池，手机分段 Tab 模式无缝联动，全配置持久化至 paint_prefs

- **ReveriePaint 界面动效速度设置与极速模式支持 (2026-10-02, 优化完成)**:
  - 需求背景：部分创作者在作画过程中需要极致敏捷的界面反馈，标准弹簧动效（约 200ms）在频繁切面板与弹窗时略显滞重，期望支持 <= 0.1s 的极速动效或完全关闭
  - 核心架构重构：扩展 `Motion.kt` 动效令牌总线，定义 `UiAnimationSpeed`（标准 NORMAL、极速 FAST、关闭 OFF 三档）；入场 `enterSpring()` 与出场 `exitTween(baseMillis)` 全面动态适配当前档位；极速档出场时间缩短为 80ms（<= 0.1s），入场弹簧刚度提升至 1200f/1500f 实现干脆利落收敛，关闭档直接采用 `snap()` 达到零延迟瞬时响应
  - 面板退场统一：重构 `PaintingPage` 中的画笔、图层、设置、色卡、更多工具、时间轴面板及常态参考窗口，将写死的 `tween(200)` / `tween(180)` 全量替换为 `Motion.exitTween`
  - 设置与持久化：在通用设置「界面动效速度」分段选项中接入三档切换，并持久化到 `paint_prefs`（键名 `uiAnimationSpeed`），启动时由 `PaintViewModel` 自动恢复并同步到 `Motion.currentSpeed`

- **ReveriePaint 创建画布预览缓动曲线修复与中心瞬移消除 (2026-10-02, 优化完成)**:
  - 根因定位：原预览动画采用弹簧曲线（spring DampingRatioMediumBouncy），切换不同画幅比例时有回弹与非单调迟滞感；且原布局在 fitsInside 条件突变时用外层 Row/Column 替换居中 Box，导致预览框在第一帧发生中心点横向/纵向位移突跳（瞬移）
  - 曲线重构：改用纯减速 out-only 缓动曲线（LinearOutSlowInEasing, 280ms），首帧以最大响应初速度启动，平滑单调收敛归位
  - 结构锁定：将画布预览框永久锚定在容器几何中心（Alignment.Center），尺寸过窄或过扁时的分辨率文字以框体边界为参考依附展示，杜绝容器重排引起的中心瞬移

- **ReveriePaint 边缘侧滑返回手势与起笔防误画优化 (2026-10-02, 优化完成)**:
  - 根因定位：原代码在 API 29+ 启用了全屏全高度左右边缘手势排除区（systemGestureExclusionRects），导致平板端系统侧滑返回手势被全屏强制阻断；且手指贴近边缘按下时立即触发 handleToolDown 抢占事件并在侧滑返回触发时残留误画线条
  - 智能手势策略与独立开关：在设置-通用中增加「允许边缘侧滑返回」开关（allowEdgeBackGesture），并在 PaintViewModel 中与返回键行为（BackKeyAction）智能联动；仅当用户主动关闭或返回键设为无行为且无浮层展开时才全高度排除手势以防误触，其余情况释放手势排除区让系统原生侧滑正常响应
  - 手指边缘起笔缓冲与防误画：在 CanvasTouchView 中对边缘 32dp 内的手指触控引入 180ms/滑动容差缓冲判定；若系统识别为侧滑返回派发 ACTION_CANCEL，则静默取消且绝不触发 handleToolDown 污染画布与撤销栈；若用户为垂直画线或持续移动则自动补偿落笔并平滑绘制；压感笔（Stylus）完全不受限制支持贴边作画

- **ReveriePaint 图层重命名冲突修复与 UI 交互升级 (2026-10-02, 优化完成)**:
  - 根因定位：硬件键盘事件由 `MainActivity.dispatchKeyEvent` 拦截处理，当 `isTextInputActive` 为假时自动走全局快捷键管线，导致重命名输入框内按下 Delete / Backspace 时触发 `removeLayer` 误删图层
  - 全局输入防护：在 `PaintViewModel` 引入输入框活跃计数器 `pushTextInputActive`/`popTextInputActive`，新增 `TextInputGuard` 声明式守卫组件并在所有文本编辑与重命名弹窗（图层、笔刷预设/分组、色卡、选区、文字工具）中全局接入；`PaintingPage` 根容器键盘分发增加输入态旁路保护
  - 快捷交互升级：在图层列表 `LayerRow` 图层名称上增加双击（Double-tap）手势，支持双击直接调起重命名弹窗，同时与原详情页入口无缝并存
  - 弹窗 UI 质感与校验：重命名弹窗升级为独立 Morandi 对话框，打开时通过 `FocusRequester` 自动聚焦并全选文本；右侧增加一键清空按钮；支持软硬件键盘 `Enter` 快捷确认与 `Esc` 取消；限制最大 40 字符并禁止全空白名称提交

- **ReveriePaint 笔刷面板冷启即时加载优化 (2026-10-02, 优化完成)**:
  - 根因定位：冷启笔刷加载原先在 Compose 首帧绘制后的 LaunchedEffect 才迟滞启动，且每次都要遍历检查 500+ 个 assets 文件，导致用户快速进入画布打开笔刷面板时数据尚未就绪，左侧仅剩 3 个分类、右侧触发 filtered.isEmpty() 呈现空状态
  - 启动预热：在 MainActivity.onCreate 完成引擎注册后立即并发预热 loadBrushPresets，充分利用 UI 渲染与测量窗口期
  - 资产快路径：针对已释放资源的普通启动跳过 500+ 个 assets 文件的解压与遍历检查，资产准备耗时从 1 秒锐减至 1 毫秒；对 assets 内置名称建立内存缓存，杜绝主线程与 JNI 多次重入扫描
  - 面板兜底与状态指示：当笔刷尚在载入时，左侧分类栏自动使用 BUILT_IN_BRUSH_GROUPS 兜底占位防止结构闪变坍塌；右侧预设列表展示微动加载指示器与文本提示，数据就绪后平滑无缝过渡

- **ReveriePaint 崩溃诊断引擎优化与 Native 信号捕获 (2026-10-02, 优化完成)**:
  - 根因定位：原系统仅具备 Java 层的 Thread.setDefaultUncaughtExceptionHandler，当底层 C++/Krita 核心发生 SIGSEGV 段错误或 SIGABRT 断言崩溃时，进程被 Linux 内核直接杀死，Java 异常捕获机制无法触发，导致崩溃目录完全为空
  - Native 信号捕获器：实现 ReverieCrashHandler (C++)，基于 sigaction 全面拦截 SIGSEGV/SIGABRT/SIGBUS/SIGFPE/SIGILL，分配 128KB sigaltstack 独立备用栈；全链路严格遵循 async-signal-safe 规范（无动态内存分配，纯 open/write/close 系统调用）；利用 _Unwind_Backtrace 与 dladdr 实时解析抓取 48 帧 Native 符号栈，记录 ARM64 核心寄存器与 si_addr，并重新抛出信号生成 tombstone
  - 操作轨迹环形缓冲区：实现 Breadcrumbs 诊断轨迹追踪，在 JVM 与 Native 端分别维护容量 25 条的环形缓冲区，对页面切换、工具选择、笔刷加载、图层增删与撤销重做进行轻量低开销埋点
  - 启动诊断与导出弹窗：MainActivity 启动阶段异步检测未提示过的崩溃日志；弹出 Morandi 风格的 CrashReportDialog 诊断弹窗，支持完整日志展开预览、一键复制剪贴板、系统分享面板以及基于 MediaStore 导出至公共目录 Download/ReveriePaint_CrashReports/

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
- 系统：ColorOS 16.1 / Android 16（ROM: ClearSkys 20261012 移植版，基底 OnePlus Ace 6，内核 5.10.246-AetherKernel），SukiSU Boot root
- 底层备份：位于 `~/刷机/k60/原厂备份/`（EFS/基带 `modemst1/2`、`fsg/fsc`，校准 `persist/persistbak`，`devinfo`，HyperOS 4 双槽位 `boot/vendor_boot/dtbo/recovery/vbmeta` 全套原厂镜像）
- 模块链：YABP、Zygisk Next (匿名内存模式，enforce-denylist 已置 0)、Vector (已修复 service.sh 为 unshare -m)、Tricky Store + TS Enhancer Extreme (内置 keybox)、HMA-OSS Zygisk、Material You for ColorOS、magic_mount_rs
- 激活 Xposed：LuckyTool v1.3.4、CorePatch v4.9、InxLocker（已启用并绑定 android/0，配套 InstallerX Revived 锁定默认安装器）、WeType-Kaomoji、WeTypeHook、couiexpressive、soulfrog
- 授权机制：轻量主板 ID 验证（本机 ID `0x0000043bfce1db8a`），授权凭据位于 `/mi_ext/product/etc/security/verificationlist.bin`（SHA-256 token `9a033082...`）；补丁包采用 Zip 伪加密，消除中心目录标志位后卡刷成功
- 数据保持：保留全部用户数据、应用配置与模块平滑升级成功
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
- 笔刷：KisBrushOp::paintLine + KisFakeRunnableStrokeJobsExecutor 同步驱动异步管线；静态注册 kritadefaultpaintops_static 防 DSO 段错误；ensurePresetInfo 与 parseKppAttributes 兼容 Krita 5 OpacityUseCurve/FlowUseCurve/SizeUseCurve 无 PressureOpacity 标签预设，loadBrushPreset 归一化补全 settings 压感开关防 KisOpacityOption 曲线跳过，computeEffectivePressure 移除 brushPressureSize 错误缩放防止无尺寸压感笔刷压感被锁死为 1.0，setBrushPressureDynamics 隔离 OpacityValue/FlowValue 基底参数杜绝压感覆盖导致的笔刷隐形或流量清空；updateKppBytes 自动补全 ABR 导入预设缺失的压感传感器与曲线 XML，支持 transfer/paintDynamics 多版本 Photoshop 描述符键值解析；ScratchpadCanvas 试画栏改用 awaitEachGesture 零延迟捕获单击打点与笔画起点并读取 historical 高频采样点，按弧长均匀插值步进 dabs 且距离余量无缝跨线段累加，彻底解决手绘采样率间隔造成的线条断裂成点阵虚线问题
- 图层架构：手势消费仲裁与 combinedClickable 共存；列表级长按接管拖拽；松手冻结 pendingOrder 存层名 List<String> 防索引错位；KisNode 语义向上拖 insert 上方，向下拖 insert 下方；collapsedGroupNames 提升至 ViewModel 并在 .revp extraJson 中持久化；editTargetLayers 自动将选中图层组递归展开为所有后代图层供变换/液化/滤镜统一操作；isLayerEffectivelyHidden 级联检查父组可见性并拦截绘制；向下合并解除源层剪裁通道限制并原子化事务与图层移除，图层组合并修正坐标偏移至 ext.topLeft() 并原子化撤销
- 工具栏：内容溢出时上下边缘叠加轻柔渐变遮罩，初始与滑动时唤醒上下呼吸微动箭头提示可滚动，静止 2.5 秒后平滑淡化为边缘极简指示圆点且不拦截工具点击
- 快捷键与外接键盘：StylusDriver 与手写笔 Adapter 增加 isStylusKeyEvent 判定，阻断 PageUp/PageDown 等键盘按键被误拦截吞噬；keyEventToString 兼容 Meta (Command/Win) 与 Ctrl 统一映射，补全 NumPadEnter/Backspace/方向键等映射；handleKeyEvent 引入长按连发节流与单次触发限制，笔刷缩放限频 50ms、撤销重做限频 200ms，离散动作长按不连发；applyTool 增加当前工具瞬时退出避免冗余重载；undo/redo 改为 runCore(render=false) 消除单次撤销双重渲染卡顿，并遵从 undoToastEnabled；Settings 录制弹窗期间由 isShortcutRecordingActive 旁路全局快捷键拦截
- 手势与拾色：解除 canEyedrop 对 !penOnlyMode 的限制，笔模式下单指长按画布吸色与手写笔吸色完全并存；ACTION_MOVE 增加长按等待期容差检测，位移在 moveSlopPx 内拦截平移与画线保持画面稳定，超阈值时取消长按并无缝转为单指平移（开启平移时）或忽略防误触；ACTION_UP 拦截笔模式短触画线杜绝误触打点；双指捏合平移触发时立即执行 cancelPendingShapeGesture 回滚首指误落的节点与零尺寸形状，多边形选区同步回退临时点，彻底根除双指移动画布误创节点问题
- 渲染引擎与投影管线：renderToBuffer 在后台异步调度器活跃时强制 waitForDone 阻塞等待合并完成，空闲时才由 compositeLayersRange 毫秒级同步合成笔画与预览脏区，彻底根除多线程并发读写 projection 瓦片导致的 KisTiledExtentManager SIGABRT 闪退；setLayerOpacityDirect 移除高频 setDirty 改由快速同步预览合成，setLayerOpacity 与 setLayerBlendMode 提交后等待合并收敛；touchStrokeEnd 与 strokeAirbrushTick 移除 endDev->setDirty 与 target->setDirty 调用杜绝章鱼式抽动与 64x64 方块底色脏块
- 崩溃诊断引擎：接入 ReverieCrashHandler (C++) 信号安全拦截器 (SIGSEGV/SIGABRT/SIGBUS/SIGFPE/SIGILL) 与 128KB 独立信号备用栈，捕获 48 帧 Native 符号栈与 ARM64 寄存器状态；Java 层集成 Thread.UncaughtExceptionHandler；双端搭载容量 25 条的 Breadcrumbs 环形操作轨迹；启动阶段自动触发未读日志检测并弹出 Morandi 诊断弹窗，支持一键复制、系统分享与 MediaStore 公共 Downloads 目录导出
- 构建：`scripts/build_native.sh`（QT_ANDROID_DIR=/opt/Qt6/6.6.3/android_arm64_v8a，增量编译约 45s；纯 Kotlin 改动直接 assembleDebug）

### Horizon — `~/Projects/Horizon`
- 现代化 Android 平板浏览器（GeckoView + Mozilla Android Components + Rust Firefox Sync，前台 Jetpack Compose，针对一加平板 2 Pro 定制）
- 应用名：`Horizon`，包名：`top.lanrhyme.horizon`
- 架构特色：Zen / Arc 风格三态可折叠侧边栏、多工作区（Spaces）、同屏双开分屏（Split View）、WebExtensions 插件生态、全量 Firefox 跨端同步（书签/历史/标签/密码/Send Tab）、Morandi 与 Material You 双轨动态色彩

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

- **网易 UU 远程被控端 (uu-remote-linux)**：社区原生 Rust 被控端（`/usr/bin/uuremote-server`，已重编集成 `--features wayland,portal`）；用户服务 `uu-remote-native.service`（自启常驻）；依赖 `/dev/uinput`（uaccess 规则）与 `xdg-desktop-portal` + `libpipewire`；凭据存储于 `~/.config/uuremote/config.json`；支持官方客户端扫码登录绑定
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
