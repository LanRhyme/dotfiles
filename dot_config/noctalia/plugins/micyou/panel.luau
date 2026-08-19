--!nonstrict
-- MicYou — interactive control panel

local status = noctalia.state.get("status") or {}
local isRunning = false
local currentMode = "wifi"
local serverPid = "-"
local gain = 15.0
local nsEnabled = true

local function readSettings()
    local path = noctalia.expandPath("~/.config/micyou/settings.json")
    local content = noctalia.readFile(path)
    if content and content ~= "" then
        local g = content:match('"gain":%s*([%d%.]+)')
        if g then
            gain = tonumber(g) or 15.0
        end
        local ns = content:match('"nsEnabled":%s*(%a+)')
        if ns then
            nsEnabled = (ns == "true")
        end
    end
end

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
    readSettings()
    render()
end

noctalia.state.watch("status", applyStatus)

function onOpen(_context)
    readSettings()
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

function onGainChanged(val)
    local num = tonumber(val) or 15
    gain = num
    noctalia.runAsync(`micyou settings set gain {num}`)
    render()
end

function onNsToggled(checked)
    local val = (checked == true or checked == 1 or checked == "true")
    nsEnabled = val
    noctalia.runAsync(`micyou settings set nsEnabled {val and "true" or "false"}`)
    render()
end

function onLaunchTuiClicked()
    sendCommand("launch-tui")
end

function onLaunchGuiClicked()
    noctalia.runAsync("micyou-app &")
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

    panel.render(ui.column({ flexGrow = 1, gap = 14, align = "stretch", padding = 16 }, {
        -- Header Row
        ui.row({ align = "center", gap = 8 }, {
            ui.glyph({ name = isRunning and "circle-dot" or "microphone-off", size = 24, color = isRunning and "primary" or "on_surface_variant" }),
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

        -- Audio Controls: Gain Slider & AI Noise Suppression Switch
        ui.column({ gap = 10 }, {
            -- Gain Slider
            ui.row({ align = "center", justify = "space-between" }, {
                ui.label({ text = "麦克风增益 (Gain)", fontWeight = "bold", fontSize = 13 }),
                ui.label({ text = string.format("%d dB", math.floor(gain)), color = "primary", fontWeight = "bold", fontSize = 13 }),
            }),
            ui.slider({
                value = gain,
                min = 0,
                max = 30,
                step = 1,
                onChange = "onGainChanged",
            }),

            -- AI Noise Suppression Switch
            ui.row({ align = "center", justify = "space-between" }, {
                ui.column({ gap = 2 }, {
                    ui.label({ text = "AI 智能降噪 (PureVox)", fontWeight = "bold", fontSize = 13 }),
                    ui.label({ text = "实时过滤环境噪音与杂音", color = "on_surface_variant", fontSize = 11 }),
                }),
                ui.toggle({
                    checked = nsEnabled,
                    onChange = "onNsToggled",
                }),
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

readSettings()
applyStatus(noctalia.state.get("status"))
