--!nonstrict
-- MicYou — headless background service managing CLI daemon and state channels

noctalia.setUpdateInterval(1000)

local state = "stopped" -- "stopped" | "starting" | "running" | "stopping"
local connectionMode = "wifi"
local serverPid = nil
local isAvailable = true
local tickCount = 0

local function cfg(key)
    return noctalia.getConfig(key)
end

local function log(msg)
    noctalia.log(`micyou: {msg}`)
end

local function updateStatusChannel()
    noctalia.state.set("status", {
        state = state,
        mode = connectionMode,
        pid = serverPid,
        available = isAvailable,
    })
end

local function getLockFilePath()
    local base = noctalia.getenv("XDG_DATA_HOME")
    if base == nil or base == "" then
        base = "~/.local/share"
    end
    return noctalia.expandPath(`{base}/micyou/mode.lock`)
end

local function resolveCliBinary()
    if noctalia.commandExists("micyou-cli") then
        return "micyou-cli"
    end
    local devBin = noctalia.expandPath("~/Projects/MicYou/tauri-app/target/release/micyou")
    if noctalia.readFile(devBin) then
        return devBin
    end
    return "micyou"
end

local function checkStatus()
    local lockPath = getLockFilePath()
    local content = noctalia.readFile(lockPath)

    if content and content ~= "" then
        local pidMatch = content:match('"pid":%s*(%d+)')
        local modeMatch = content:match('"mode":%s*"([^"]+)"')

        if pidMatch then
            local pid = tonumber(pidMatch)
            local procCmd = noctalia.readFile(`/proc/{pid}/cmdline`)
            if procCmd and procCmd ~= "" then
                serverPid = pid
                state = "running"
                if modeMatch then
                    connectionMode = modeMatch
                end
                updateStatusChannel()
                return
            end
        end
    end

    if state == "running" then
        state = "stopped"
        serverPid = nil
    elseif state ~= "starting" and state ~= "stopping" then
        state = "stopped"
        serverPid = nil
    end
    updateStatusChannel()
end

local function startServer(overrideMode)
    if state == "running" or state == "starting" then return end

    state = "starting"
    updateStatusChannel()

    local mode = overrideMode or cfg("default_mode") or "wifi"
    connectionMode = mode
    local port = cfg("default_port") or 8554
    local bin = resolveCliBinary()

    log(`starting server: bin={bin} mode={mode} port={port}`)
    local launchCmd = `{bin} serve --mode {mode} --port {port}`

    noctalia.runStream(launchCmd, function(line)
        if not line then return end
        local lvl = line:match("%[level%]%s*(%d+)")
        if lvl then
            local num = tonumber(lvl) or 0
            noctalia.state.set("audio_level", num)
        end
        if line:find("%[mic%] connected") then
            state = "running"
            updateStatusChannel()
        elseif line:find("%[server%] stopped") then
            state = "stopped"
            updateStatusChannel()
        end
    end)

    noctalia.notify(noctalia.tr("name"), noctalia.tr("notify.started") .. ` ({mode})`)
    checkStatus()
end

local function stopServer()
    if state == "stopped" or state == "stopping" then return end

    state = "stopping"
    updateStatusChannel()

    log("stopping server")
    noctalia.runAsync("pkill -f 'micyou.*serve' 2>/dev/null || true")
    noctalia.notify(noctalia.tr("name"), noctalia.tr("notify.stopped"))
    state = "stopped"
    serverPid = nil
    noctalia.state.set("audio_level", 0)
    updateStatusChannel()
end

local function handleCommand(cmd)
    if type(cmd) ~= "table" then return end
    local action = cmd.action

    if action == "toggle" then
        if state == "running" then
            stopServer()
        else
            startServer(cmd.mode)
        end
    elseif action == "start" then
        startServer(cmd.mode)
    elseif action == "stop" then
        stopServer()
    elseif action == "launch-tui" then
        local termCmd = cfg("terminal_command") or "ghostty -e"
        local bin = resolveCliBinary()
        noctalia.runAsync(`{termCmd} {bin} &`)
    end
end

-- Watch incoming commands from widgets or shortcuts
noctalia.state.watch("command", handleCommand)

function update()
    tickCount += 1
    if tickCount % 2 == 0 then
        checkStatus()
    end
end

-- Initial check via file read
checkStatus()
