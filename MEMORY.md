# 配置记忆

本文件作为 AI 代理的实时上下文缓冲区，记录系统配置当前状态、活跃任务与环境关键事实，确保会话间平滑交接
结构：最近动态 → 设备 → 桌面环境 → 项目 → 安装与服务 → 已弃用 → 踩坑速查

## 最近动态

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
