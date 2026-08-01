import type { ExtensionAPI, ExtensionContext, Theme } from "@earendil-works/pi-coding-agent";
import { Container, Input, Key, matchesKey, Spacer, Text } from "@earendil-works/pi-tui";

interface PaletteCommand {
  name: string;
  category: "常用" | "高级" | "配置" | "系统";
  cnName: string;
  description: string;
}

const PALETTE_COMMANDS: PaletteCommand[] = [
  // 常用命令
  { name: "tree", category: "常用", cnName: "对话树视图与节点回溯", description: "快捷键 Esc Esc — 打开对话树图切回历史 Turn" },
  { name: "rewind", category: "常用", cnName: "工作区代码与对话回溯", description: "可视化 Git 快照回溯与预览代码 Diff" },
  { name: "undo", category: "常用", cnName: "快捷撤销上一步修改", description: "撤销上一步 AI 对本地文件做出的改动" },
  { name: "redo", category: "常用", cnName: "恢复上一步撤销修改", description: "恢复上一步被撤销的代码改动" },
  { name: "websearch", category: "常用", cnName: "AnySearch 联网搜索", description: "全功能联网搜索与网页/PDF解析" },
  { name: "search", category: "常用", cnName: "快捷联网搜索", description: "搜索并直接返回 AI 总结摘要" },
  { name: "model", category: "常用", cnName: "切换 AI 语言模型", description: "快捷键 Ctrl+L — 选择与切换当前 LLM" },
  { name: "thinking", category: "常用", cnName: "调整推理思考深度", description: "快捷键 Shift+Tab — 切换思考深度 (off/low/high)" },
  { name: "subagents", category: "常用", cnName: "Sub-agents 子代理控制台", description: "管理、监控与调度后台协同 Sub-agent" },
  { name: "goal", category: "常用", cnName: "自主目标循环修复", description: "开启自主目标拆解，自动测试与修复" },
  { name: "plan", category: "常用", cnName: "只读规划模式", description: "Codex 风格 /plan — 动手前进入只读规划，批注审查 AI 方案" },
  { name: "btw", category: "常用", cnName: "侧边快速提问", description: "问个小问题不打断主对话，独立线程回答" },
  { name: "piolium-lite", category: "常用", cnName: "快速安全与密钥扫描", description: "快速扫描代码库密钥泄露与安全隐患" },
  { name: "usage", category: "常用", cnName: "Token 消耗与资费看板", description: "实时统计模型 Token 消耗与费用" },
  { name: "extmgr", category: "常用", cnName: "扩展 TUI 图形管理器", description: "可视化查看、开关、更新已安装扩展" },

  // 高级命令
  { name: "fork", category: "高级", cnName: "分化新会话分支", description: "派生新分支，不污染主会话" },
  { name: "label", category: "高级", cnName: "标记当前对话节点", description: "设置黄色高亮标记方便精准回溯" },
  { name: "session", category: "高级", cnName: "历史会话管理", description: "切换、管理与导出历史 Session" },
  { name: "compact", category: "高级", cnName: "压缩会话上下文", description: "手动将历史对话总结为结构化摘要" },
  { name: "memctx", category: "高级", cnName: "Markdown 长期记忆", description: "管理项目 MEMORY.md 知识库" },
  { name: "lean-ctx", category: "高级", cnName: "Token 极限压缩看板", description: "查看 MCP Session 缓存与压缩率" },
  { name: "lens", category: "高级", cnName: "代码质量与 LSP 检查", description: "运行 LSP 语言服务与 Linter 检查" },
  { name: "spawn", category: "高级", cnName: "终端 Overlay 浮窗", description: "在浮窗中运行 vim, lazygit 等 CLI" },
  { name: "attach", category: "高级", cnName: "连接交互终端", description: "重新连接后台运行的交互终端" },
  { name: "chrome-devtools", category: "高级", cnName: "Chrome 浏览器调试", description: "CDP 连接 Chrome：开标签、导航、截图、执行 JS" },
  { name: "piolium-deep", category: "高级", cnName: "深度多阶段漏洞挖掘", description: "对代码进行深度多阶段安全审计" },

  // 配置与系统
  { name: "zentui", category: "配置", cnName: "ZentUI 主题设置", description: "配置固定底部输入框与 Starship 状态栏" },
  { name: "open-tui", category: "配置", cnName: "OpenTUI 顶栏设置", description: "配置直角 ASCII Art Logo 顶栏" },
  { name: "stamp", category: "配置", cnName: "时间戳与耗时显示", description: "配置会话时间戳、助手元数据与工具耗时显示" },
  { name: "curator", category: "配置", cnName: "开关搜索审查界面", description: "开启或关闭搜索 Live Browser Curator" },
  { name: "clear", category: "系统", cnName: "清空终端屏幕", description: "快捷键 Ctrl+C — 清空当前终端内容" },
  { name: "help", category: "系统", cnName: "帮助文档", description: "查看 Pi Agent 官方使用帮助与指南" }
];

class CommandPaletteComponent extends Container {
  private searchInput: Input;
  private listContainer: Container;
  private filteredCommands: PaletteCommand[] = PALETTE_COMMANDS;
  private selectedIndex: number = 0;

  constructor(
    private theme: Theme,
    private onSelectCallback: (cmdName: string) => void,
    private onCancelCallback: () => void
  ) {
    super();

    // 1. 顶栏标题与说明
    this.addChild(new Text(theme.bold(theme.fg("accent", "  🔍 Pi Agent 命令面板 (Command Palette)")), 0, 0));
    this.addChild(new Text(theme.fg("dim", "  打字直接搜索 · ↑/↓: 选择 · Enter: 执行 · Esc: 关闭"), 0, 0));
    this.addChild(new Spacer(1));

    // 2. 搜索框 Component
    this.searchInput = new Input();
    this.addChild(this.searchInput);
    this.addChild(new Spacer(1));

    // 3. 列表容器
    this.listContainer = new Container();
    this.addChild(this.listContainer);

    this.addChild(new Spacer(1));

    this.updateList();
  }

  private filterCommands(query: string): void {
    const q = query.trim().toLowerCase();
    if (!q) {
      this.filteredCommands = PALETTE_COMMANDS;
    } else {
      this.filteredCommands = PALETTE_COMMANDS.filter(cmd =>
        cmd.name.toLowerCase().includes(q) ||
        cmd.cnName.toLowerCase().includes(q) ||
        cmd.category.toLowerCase().includes(q) ||
        cmd.description.toLowerCase().includes(q)
      );
    }
    this.selectedIndex = query ? 0 : Math.min(this.selectedIndex, Math.max(0, this.filteredCommands.length - 1));
    this.updateList();
  }

  private updateList(): void {
    this.listContainer.clear();

    const maxVisible = 10;
    const startIndex = Math.max(
      0,
      Math.min(this.selectedIndex - Math.floor(maxVisible / 2), this.filteredCommands.length - maxVisible)
    );
    const safeStartIdx = Math.max(0, startIndex);
    const endIndex = Math.min(safeStartIdx + maxVisible, this.filteredCommands.length);

    if (this.filteredCommands.length === 0) {
      this.listContainer.addChild(new Text(this.theme.fg("warning", "  未找到匹配的指令"), 0, 0));
      return;
    }

    for (let i = safeStartIdx; i < endIndex; i++) {
      const cmd = this.filteredCommands[i];
      if (!cmd) continue;

      const isSelected = i === this.selectedIndex;

      const prefix = isSelected ? this.theme.fg("accent", " → ") : "   ";
      const categoryTag = cmd.category === "常用"
        ? this.theme.fg("success", `[${cmd.category}]`)
        : cmd.category === "高级"
        ? this.theme.fg("warning", `[${cmd.category}]`)
        : cmd.category === "配置"
        ? this.theme.fg("accent", `[${cmd.category}]`)
        : this.theme.fg("muted", `[${cmd.category}]`);

      const cmdName = this.theme.bold(this.theme.fg("accent", `/${cmd.name}`));
      const cnName = this.theme.fg("text", cmd.cnName);

      let line = `${prefix}${categoryTag} ${cmdName}  —  ${cnName}`;
      if (isSelected) {
        line = this.theme.bg("selectedBg", line);
      }

      this.listContainer.addChild(new Text(line, 0, 0));
    }

    if (this.filteredCommands.length > 0) {
      const scrollInfo = this.theme.fg("dim", `  (${this.selectedIndex + 1}/${this.filteredCommands.length})`);
      const selected = this.filteredCommands[this.selectedIndex];
      const descText = selected ? this.theme.fg("muted", `  💡 说明: ${selected.description}`) : "";
      this.listContainer.addChild(new Spacer(1));
      this.listContainer.addChild(new Text(`${scrollInfo}\n${descText}`, 0, 0));
    }
  }

  handleInput(keyData: string): void {
    // 上方向键
    if (matchesKey(keyData, Key.up) || keyData === "\x0b" || keyData === "\x10") {
      if (this.filteredCommands.length === 0) return;
      this.selectedIndex = this.selectedIndex === 0 ? this.filteredCommands.length - 1 : this.selectedIndex - 1;
      this.updateList();
      return;
    }

    // 下方向键
    if (matchesKey(keyData, Key.down) || keyData === "\x0a" || keyData === "\x0e") {
      if (this.filteredCommands.length === 0) return;
      this.selectedIndex = this.selectedIndex === this.filteredCommands.length - 1 ? 0 : this.selectedIndex + 1;
      this.updateList();
      return;
    }

    // 回车键
    if (matchesKey(keyData, Key.enter)) {
      const selected = this.filteredCommands[this.selectedIndex];
      if (selected) {
        this.onSelectCallback(selected.name);
      }
      return;
    }

    // Esc 关闭
    if (matchesKey(keyData, Key.escape)) {
      this.onCancelCallback();
      return;
    }

    // 传递给 Input 并实时筛选
    this.searchInput.handleInput(keyData);
    this.filterCommands(this.searchInput.getValue());
  }
}

export default function (pi: ExtensionAPI) {
  pi.registerCommand("cmd", {
    description: "打开交互式中文命令面板 (Command Palette)",
    handler: async (_args, ctx: ExtensionContext) => {
      if (!ctx.hasUI) return;

      await ctx.ui.custom<void>((tui, theme, _kb, done) => {
        const paletteComponent = new CommandPaletteComponent(
          theme,
          async (cmdName) => {
            done(undefined);
            try {
              const registered = pi.getCommands();
              const cmdObj = registered.find(c => c.name === cmdName);

              if (cmdObj && typeof cmdObj.handler === "function") {
                await cmdObj.handler([], ctx);
                return;
              }

              if (cmdName === "tree") {
                ctx.ui.notify("对话树快捷键: 双击 Esc 键 (Esc Esc)", "info");
              } else if (cmdName === "model") {
                ctx.ui.notify("模型选择快捷键: Ctrl+L", "info");
              } else if (cmdName === "thinking") {
                ctx.ui.notify("思考深度快捷键: Shift+Tab", "info");
              } else if (cmdName === "clear") {
                ctx.ui.notify("清屏快捷键: Ctrl+C", "info");
              } else {
                ctx.ui.notify(`命令 /${cmdName} 为 CLI 底层指令`, "info");
              }
            } catch (err) {
              ctx.ui.notify(`执行 /${cmdName} 失败: ${err}`, "warning");
            }
          },
          () => {
            done(undefined);
          }
        );

        return {
          render: (w: number) => paletteComponent.render(w),
          invalidate: () => paletteComponent.invalidate(),
          handleInput: (data: string) => {
            paletteComponent.handleInput(data);
            tui.requestRender();
          }
        };
      });
    }
  });

  pi.registerCommand("menu", {
    description: "打开交互式中文命令面板 (Command Palette)",
    handler: async (_args, ctx) => {
      if (!ctx.hasUI) return;
      const registered = pi.getCommands();
      const cmdObj = registered.find(c => c.name === "cmd");
      if (cmdObj && typeof cmdObj.handler === "function") {
        await cmdObj.handler([], ctx);
      }
    }
  });

  pi.registerCommand("palette", {
    description: "打开交互式中文命令面板 (Command Palette)",
    handler: async (_args, ctx) => {
      if (!ctx.hasUI) return;
      const registered = pi.getCommands();
      const cmdObj = registered.find(c => c.name === "cmd");
      if (cmdObj && typeof cmdObj.handler === "function") {
        await cmdObj.handler([], ctx);
      }
    }
  });
}
