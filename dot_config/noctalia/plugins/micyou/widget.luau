--!nonstrict
-- MicYou bar widget: dynamic real-time voice-reactive volume ring with center dot

local state = "stopped"
local isRunning = false
local isMuted = false
local rawLevel = 0.0
local displayLevel = 0.05

local function checkMute()
    noctalia.runAsync("wpctl get-volume @DEFAULT_AUDIO_SOURCE@ 2>/dev/null", function(res)
        if res.exitCode == 0 and res.stdout then
            local muted = (res.stdout:find("%[MUTED%]") ~= nil)
            if muted ~= isMuted then
                isMuted = muted
                render()
            end
        end
    end)
end

local function applyStatus(status)
    if type(status) == "table" then
        state = status.state or "stopped"
        isRunning = (state == "running")
    end
    render()
end

local function onAudioLevel(lvl)
    local num = tonumber(lvl) or 0
    rawLevel = math.clamp(num / 100.0, 0.0, 1.0)
    displayLevel = math.max(0.08, rawLevel)
    if isRunning then
        render()
    end
end

noctalia.state.watch("audio_level", onAudioLevel)

function render()
    local hideInactive = noctalia.getConfig("hide_inactive") or false
    local container = barWidget.isVertical() and ui.column or ui.row
    local children = {}

    if isRunning then
        barWidget.setVisible(true)
        local ringColor = isMuted and "warning" or "primary"

        -- Dynamic voice-reactive volume ring + center dot
        local ringWithDot = ui.box({ width = 22, height = 22, align = "center", justify = "center" }, {
            ui.progress({
                value = displayLevel,
                shape = "ring",
                size = 20,
                thickness = 2.5,
                color = ringColor,
            }),
            ui.label({
                text = "•",
                fontSize = 14,
                baseline = "inkCentered",
                color = ringColor,
            }),
        })

        table.insert(children, ringWithDot)
        barWidget.setTooltip("MicYou: 运行中 (实时音频监听)\n左键点击打开控制面板\n右键点击停止服务")
    elseif state == "starting" or state == "stopping" then
        barWidget.setVisible(true)
        table.insert(children, ui.glyph({
            name = "microphone",
            size = 18,
            color = "warning",
        }))
        barWidget.setTooltip(state == "starting" and "正在启动 MicYou..." or "正在停止 MicYou...")
    else
        barWidget.setVisible(not hideInactive)
        table.insert(children, ui.glyph({
            name = "microphone-off",
            size = 18,
            color = "on_surface_variant",
        }))
        barWidget.setTooltip("MicYou: 已停止\n左键点击打开控制面板\n右键点击启动服务")
    end

    barWidget.render(container({ gap = 4, align = "center" }, children))
end

noctalia.setUpdateInterval(50)

function update()
    if isRunning then
        -- Smoothly decay level back to idle baseline when silent
        if displayLevel > 0.08 then
            displayLevel = math.max(0.08, displayLevel - 0.06)
            render()
        end
    end
end

function onClick()
    noctalia.togglePanel("lanrhyme/micyou:panel")
end

function onRightClick()
    noctalia.state.set("command", { action = "toggle" })
end

function onMiddleClick()
    noctalia.state.set("command", { action = "launch-tui" })
end

applyStatus(noctalia.state.get("status"))
noctalia.state.watch("status", applyStatus)
