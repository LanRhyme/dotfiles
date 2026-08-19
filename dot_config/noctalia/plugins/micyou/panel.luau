--!nonstrict
-- MicYou — interactive control panel

local status = noctalia.state.get("status") or {}
local isRunning = status.state == "running"
local currentMode = status.mode or "wifi"
local serverPid = status.pid or "-"

local function sendCommand(action, mode)
    noctalia.state.set("command", {
        action = action,
        mode = mode or currentMode,
    })
end

local function applyStatus(newStatus)
    if type(newStatus) == "table" then
        status = newStatus
        isRunning = (status.state == "running")
        currentMode = status.mode or "wifi"
        serverPid = status.pid or "-"
    end
    render()
end

noctalia.state.watch("status", applyStatus)

function onStartClicked()
    sendCommand("start", currentMode)
end

function onStopClicked()
    sendCommand("stop")
end

function onRestartClicked()
    sendCommand("stop")
    noctalia.runAsync("sleep 0.5", function()
        sendCommand("start", currentMode)
    end)
end

function onModeChanged(index)
    local modes = { "wifi", "usb", "web" }
    currentMode = modes[index + 1] or "wifi"
    render()
end

function onLaunchTuiClicked()
    sendCommand("launch-tui")
end

function onLaunchGuiClicked()
    noctalia.runAsync("micyou-app &")
end

function onCloseClicked()
    noctalia.togglePanel("lanrhyme/micyou:panel")
end

function onToggleNs(val)
    noctalia.runAsync(`micyou settings set nsEnabled {val and "true" or "false"}`)
end

function onToggleAec(val)
    noctalia.runAsync(`micyou settings set aecEnabled {val and "true" or "false"}`)
end

function onToggleDereverb(val)
    noctalia.runAsync(`micyou settings set dereverbEnabled {val and "true" or "false"}`)
end

function onToggleVad(val)
    noctalia.runAsync(`micyou settings set vadEnabled {val and "true" or "false"}`)
end

function onToggleAgc(val)
    noctalia.runAsync(`micyou settings set agcEnabled {val and "true" or "false"}`)
end

function onToggleMute(val)
    noctalia.runAsync(`micyou settings set mute {val and "true" or "false"}`)
end

function render()
    local modeIndex = (currentMode == "usb" and 1) or (currentMode == "web" and 2) or 0

    panel.render(ui.column({ flexGrow = 1, gap = 12, align = "stretch", padding = 16 }, {
        -- Header Row
        ui.row({ align = "center", gap = 8 }, {
            ui.glyph({ name = isRunning and "microphone" or "microphone-off", size = 24, color = isRunning and "primary" or "on_surface_variant" }),
            ui.column({ flexGrow = 1, gap = 2 }, {
                ui.row({ align = "center", gap = 6 }, {
                    ui.label({ text = "MicYou 麦克风", fontSize = 16, fontWeight = "bold" }),
                    ui.label({
                        text = isRunning and "● 运行中" or "○ 已停止",
                        color = isRunning and "success" or "on_surface_variant",
                        fontSize = 11,
                    }),
                }),
                ui.label({
                    text = isRunning and `模式: {string.upper(currentMode)} · PID: {serverPid}` or "已准备就绪",
                    color = "on_surface_variant",
                    fontSize = 11,
                }),
            }),
            ui.button({ glyph = "close", variant = "ghost", tooltip = "关闭", onClick = "onCloseClicked" }),
        }),

        ui.divider(),

        -- Connection Mode & Main Control
        ui.row({ align = "center", gap = 8 }, {
            ui.column({ flexGrow = 1, gap = 4 }, {
                ui.label({ text = "连接方式", fontSize = 12, color = "on_surface_variant" }),
                ui.select({
                    options = { "Wi-Fi (局域网)", "USB (ADB 传输)", "Web (网页串流)" },
                    selectedIndex = modeIndex,
                    onChange = "onModeChanged",
                }),
            }),
            ui.column({ gap = 4, align = "end" }, {
                ui.label({ text = "状态控制", fontSize = 12, color = "on_surface_variant" }),
                if isRunning then
                    ui.row({ gap = 6 }, {
                        ui.button({ text = "停止", glyph = "player-stop", variant = "danger", onClick = "onStopClicked" }),
                        ui.button({ glyph = "reload", variant = "secondary", tooltip = "重启", onClick = "onRestartClicked" }),
                    })
                else
                    ui.button({ text = "启动服务", glyph = "player-play", variant = "primary", onClick = "onStartClicked" })
            }),
        }),

        ui.divider(),

        -- Audio DSP Module Toggles
        ui.label({ text = "音频增强处理", fontSize = 13, fontWeight = "bold" }),
        ui.column({ gap = 6 }, {
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "AI 智能降噪 (PureVox)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleNs" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "声学回声消除 (AEC)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleAec" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "空间去混响 (Dereverb)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleDereverb" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "语音活动检测 (VAD)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleVad" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "自动增益控制 (AGC)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleAgc" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "全局静音 (Mute)" }),
                ui.button({ text = "切换", variant = "ghost", onClick = "onToggleMute" }),
            }),
        }),

        ui.divider(),

        -- Extra Tools
        ui.row({ align = "center", gap = 8 }, {
            ui.button({ flexGrow = 1, text = "TUI 终端模式", glyph = "terminal-2", variant = "secondary", onClick = "onLaunchTuiClicked" }),
            ui.button({ flexGrow = 1, text = "桌面端 GUI", glyph = "layout-dashboard", variant = "ghost", onClick = "onLaunchGuiClicked" }),
        }),
    }))
end

render()
