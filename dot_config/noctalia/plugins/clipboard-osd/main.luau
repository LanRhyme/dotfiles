--!nonstrict

local REMOTE_FLAG = "/tmp/uu_remote_active"

local function isRemoteActive(): boolean
    -- Noctalia 5.4 的 Luau 沙箱不再暴露 io 库，改用 noctalia.readFile
    -- 文件不存在返回 nil，存在则为字符串（空文件也是 ""，同样判定为真）
    local ok, content = pcall(noctalia.readFile, REMOTE_FLAG)
    return ok and content ~= nil
end

local function onClipboardLine(line)
    if isRemoteActive() then
        return
    end

    if line:sub(1, 7) == "COPIED|" then
        local content = line:sub(8)
        content = content:match("^%s*(.-)%s*$") or content
        
        if content == "" then
            noctalia.notify("󰅍 已复制媒体内容", "图片或二进制数据已存入剪贴板")
        else
            noctalia.notify("󰅍 已复制到剪贴板", content)
        end
    end
end

local watchCommand = "wl-paste --watch sh -c '[ -f /tmp/uu_remote_active ] && exit 0; printf \"COPIED|\"; wl-paste -n --type text/plain 2>/dev/null | head -n 1 | cut -c 1-50; echo'"
noctalia.runStream(watchCommand, onClipboardLine)
