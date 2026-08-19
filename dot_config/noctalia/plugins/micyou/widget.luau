--!nonstrict
-- MicYou bar widget: exact replication of Tauri AudioRing (dynamic arc + center dot + background ring)

local state = "stopped"
local isRunning = false
local isMuted = false
local targetLevel = 0.0
local smoothedLevel = 0.0
local ringSvgPath = noctalia.expandPath("~/.local/state/noctalia/micyou_ring.svg")

local primaryColor = "#89a484"
local errorColor = "#fd4663"

local function loadColors()
    local path = noctalia.expandPath("~/.config/noctalia/colors.json")
    local content = noctalia.readFile(path)
    if content and content ~= "" then
        local p = content:match('"primary_container":%s*"([^"]+)"') or content:match('"primary":%s*"([^"]+)"')
        if p then primaryColor = p end
        local e = content:match('"error":%s*"([^"]+)"')
        if e then errorColor = e end
    end
end

local function generateSvg(level)
    local color = if isMuted then errorColor else primaryColor
    local circumference = 219.9
    local clamped = math.clamp(level, 0.0, 1.0)
    local offset = circumference * (1.0 - clamped)

    local svg = string.format([[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="22" height="22">
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="5" opacity="0.25"/>
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="219.9" stroke-dashoffset="%.2f" transform="rotate(-90 50 50)"/>
  <circle cx="50" cy="50" r="7" fill="%s"/>
</svg>]], color, color, offset, color)

    noctalia.writeFile(ringSvgPath, svg)
end

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
    targetLevel = math.clamp(num / 100.0, 0.0, 1.0)
end

noctalia.state.watch("audio_level", onAudioLevel)

function render()
    local hideInactive = noctalia.getConfig("hide_inactive") or false
    local container = barWidget.isVertical() and ui.column or ui.row
    local children = {}

    if isRunning then
        barWidget.setVisible(true)
        generateSvg(smoothedLevel)

        table.insert(children, ui.image({
            path = ringSvgPath,
            width = 22,
            height = 22,
        }))
        barWidget.setTooltip("MicYou: 运行中 (实时音频输入)\n左键点击打开控制面板\n右键点击停止服务")
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

noctalia.setUpdateInterval(33) -- 30 FPS smooth arc interpolation

function update()
    if isRunning then
        -- Smooth lerp interpolation identical to Tauri AudioRing.vue
        local delta = targetLevel - smoothedLevel
        if math.abs(delta) > 0.005 then
            smoothedLevel = smoothedLevel + delta * 0.25
            render()
        elseif smoothedLevel ~= targetLevel then
            smoothedLevel = targetLevel
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

loadColors()
applyStatus(noctalia.state.get("status"))
noctalia.state.watch("status", applyStatus)
