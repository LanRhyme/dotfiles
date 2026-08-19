--!nonstrict
-- MicYou control-center quick tile shortcut

local isRunning = false
local available = false

local function applyStatus(status)
    if type(status) == "table" then
        isRunning = (status.state == "running")
        available = if status.available ~= nil then status.available else true
    end

    shortcut.setLabel(if isRunning then noctalia.tr("shortcut.running") else noctalia.tr("shortcut.stopped"))
    shortcut.setIcon("microphone", "microphone-off")
    shortcut.setActive(isRunning)
    shortcut.setEnabled(available)
end

applyStatus(noctalia.state.get("status"))
noctalia.state.watch("status", applyStatus)

function onClick()
    noctalia.state.set("command", { action = "toggle" })
end

function onRightClick()
    noctalia.state.set("command", { action = "launch-tui" })
end
