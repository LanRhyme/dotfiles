--!nonstrict
-- MicYou bar widget: exact replication of Tauri AudioRing (smooth GPU-cached dynamic arc)

local state = "stopped"
local isRunning = false
local isMuted = false
local targetLevel = 0.0
local smoothedLevel = 0.0

local primaryColor = "#89a484"
local errorColor = "#fd4663"
local ringsDir = noctalia.expandPath("~/.config/noctalia/plugins/micyou/rings")

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

local function generateRingFrames()
    local circumference = 219.9
    for i = 0, 20 do
        local fraction = i / 20.0
        local offset = circumference * (1.0 - fraction)
        local svg = string.format([[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="22" height="22">
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="5" opacity="0.25"/>
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="219.9" stroke-dashoffset="%.2f" transform="rotate(-90 50 50)"/>
  <circle cx="50" cy="50" r="7" fill="%s"/>
</svg>]], primaryColor, primaryColor, offset, primaryColor)
        noctalia.writeFile(string.format("%s/ring_%d.svg", ringsDir, i), svg)
    end

    local muteSvg = string.format([[<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="22" height="22">
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="5" opacity="0.25"/>
  <circle cx="50" cy="50" r="35" fill="none" stroke="%s" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="219.9" stroke-dashoffset="219.9" transform="rotate(-90 50 50)"/>
  <circle cx="50" cy="50" r="7" fill="%s"/>
</svg>]], errorColor, errorColor, errorColor)
    noctalia.writeFile(string.format("%s/ring_mute.svg", ringsDir), muteSvg)
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
        local frameIndex = math.clamp(math.floor(smoothedLevel * 20 + 0.5), 0, 20)
        local svgPath = if isMuted
            then string.format("%s/ring_mute.svg", ringsDir)
            else string.format("%s/ring_%d.svg", ringsDir, frameIndex)

        table.insert(children, ui.image({
            path = svgPath,
            width = 22,
            height = 22,
        }))
        barWidget.setTooltip(string.format("MicYou: 运行中 (音量电平: %d%%)\n左键点击打开控制面板\n右键点击停止服务", math.floor(smoothedLevel * 100)))
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
        -- Lerp interpolation matching Tauri AudioRing.vue
        local delta = targetLevel - smoothedLevel
        if math.abs(delta) > 0.01 then
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
generateRingFrames()
applyStatus(noctalia.state.get("status"))
noctalia.state.watch("status", applyStatus)
