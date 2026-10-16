--!nonstrict

local function isRemoteActive(): boolean
    local ok, f = pcall(io.open, "/tmp/uu_remote_active", "r")
    if ok and f then
        f:close()
        return true
    end
    return false
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
