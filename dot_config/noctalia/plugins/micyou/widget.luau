--!nonstrict
-- MicYou bar widget with volume ring and panel trigger

local state = "stopped"
local isRunning = false
local micVolume = 1.0
local isMuted = false

local function sampleMicVolume()
    noctalia.runAsync("wpctl get-volume @DEFAULT_AUDIO_SOURCE@ 2>/dev/null", function(res)
        if res.exitCode == 0 and res.stdout then
            local val = res.stdout:match("Volume:%s*([%d%.]+)")
            if val then
                micVolume = math.clamp(tonumber(val) or 1.0, 0.0, 1.0)
            end
            isMuted = (res.stdout:find("%[MUTED%]") ~= nil)
            render()
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

function render()
    local hideInactive = noctalia.getConfig("hide_inactive") or false
    local container = barWidget.isVertical() and ui.column or ui.row
    local children = {}

    if isRunning then
        barWidget.setVisible(true)
        table.insert(children, ui.glyph({
            name = isMuted and "microphone-off" or "microphone",
            size = 18,
            color = isMuted and "warning" or "primary",
        }))
        table.insert(children, ui.progress({
            value = micVolume,
            variant = "circle",
            size = 16,
            thickness = 2.5,
            color = isMuted and "warning" or "primary",
        }))
        barWidget.setTooltip(string.format("MicYou: 运行中 (麦克风音量: %d%%)\n左键点击打开控制面板\n右键点击停止服务", math.floor(micVolume * 100)))
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

noctalia.setUpdateInterval(1000)

function update()
    if isRunning then
        sampleMicVolume()
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
