--!nonstrict
-- MicYou — interactive control panel

local status = noctalia.state.get("status") or {}
local isRunning = false
local currentMode = "wifi"
local serverPid = "-"

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

function onOpen(_context)
    applyStatus(noctalia.state.get("status"))
end

function onCloseClicked()
    panel.close()
end

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
    currentMode = modes[(tonumber(index) or 0) + 1] or "wifi"
    render()
end

function onLaunchTuiClicked()
    sendCommand("launch-tui")
end

function onLaunchGuiClicked()
    noctalia.runAsync("micyou-app &")
end

function onToggleNs()
    noctalia.runAsync("micyou settings set nsEnabled true 2>/dev/null || true")
end

function onToggleAec()
    noctalia.runAsync("micyou settings set aecEnabled true 2>/dev/null || true")
end

function onToggleDereverb()
    noctalia.runAsync("micyou settings set dereverbEnabled true 2>/dev/null || true")
end

function onToggleVad()
    noctalia.runAsync("micyou settings set vadEnabled true 2>/dev/null || true")
end

function onToggleAgc()
    noctalia.runAsync("micyou settings set agcEnabled true 2>/dev/null || true")
end

function onToggleMute()
    noctalia.runAsync("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle 2>/dev/null || true")
end

function render()
    local modeIndex = (currentMode == "usb" and 1) or (currentMode == "web" and 2) or 0

    local actionButtons = {}
    if isRunning then
        actionButtons[1] = ui.button({ text = "停止", glyph = "player-stop", variant = "danger", onClick = "onStopClicked" })
        actionButtons[2] = ui.button({ glyph = "reload", variant = "secondary", tooltip = "重启服务", onClick = "onRestartClicked" })
    else
        actionButtons[1] = ui.button({ text = "启动服务", glyph = "player-play", variant = "primary", onClick = "onStartClicked" })
    end

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
                    text = isRunning and `连接模式: {string.upper(currentMode)} · PID: {serverPid}` or "服务未启动",
                    color = "on_surface_variant",
                    fontSize = 11,
                }),
            }),
            ui.button({ glyph = "close", variant = "ghost", tooltip = "关闭", onClick = "onCloseClicked" }),
        }),

        ui.separator({}),

        -- Connection Mode & Service Controls
        ui.row({ align = "center", gap = 8 }, {
            ui.column({ flexGrow = 1, gap = 4 }, {
                ui.label({ text = "连接方式", fontSize = 12, color = "on_surface_variant" }),
                ui.select({
                    options = { "Wi-Fi (局域网直连)", "USB (ADB 有线)", "Web (网页串流)" },
                    selectedIndex = modeIndex,
                    onChange = "onModeChanged",
                }),
            }),
            ui.column({ gap = 4, align = "end" }, {
                ui.label({ text = "服务控制", fontSize = 12, color = "on_surface_variant" }),
                ui.row({ gap = 6 }, actionButtons),
            }),
        }),

        ui.separator({}),

        -- Audio Enhancement Module Toggles
        ui.label({ text = "音频增强处理", fontSize = 13, fontWeight = "bold" }),
        ui.column({ gap = 8 }, {
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "AI 智能降噪 (PureVox)" }),
                ui.button({ text = "开关", variant = "ghost", onClick = "onToggleNs" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "声学回声消除 (AEC)" }),
                ui.button({ text = "开关", variant = "ghost", onClick = "onToggleAec" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "空间去混响 (Dereverb)" }),
                ui.button({ text = "开关", variant = "ghost", onClick = "onToggleDereverb" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "语音活动检测 (VAD)" }),
                ui.button({ text = "开关", variant = "ghost", onClick = "onToggleVad" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "自动增益控制 (AGC)" }),
                ui.button({ text = "开关", variant = "ghost", onClick = "onToggleAgc" }),
            }),
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "麦克风静音 (Mute)" }),
                ui.button({ text = "静音/恢复", variant = "ghost", onClick = "onToggleMute" }),
            }),
        }),

        ui.separator({}),

        -- Extra Tools Row
        ui.row({ align = "center", gap = 8 }, {
            ui.button({ flexGrow = 1, text = "TUI 终端模式", glyph = "terminal-2", variant = "secondary", onClick = "onLaunchTuiClicked" }),
            ui.button({ flexGrow = 1, text = "桌面端 GUI", glyph = "layout-dashboard", variant = "ghost", onClick = "onLaunchGuiClicked" }),
        }),
    }))
end

applyStatus(noctalia.state.get("status"))
