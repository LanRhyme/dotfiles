--!nonstrict

local function onClipboardLine(line)
    if line:sub(1, 7) == "COPIED|" then
        local content = line:sub(8)
        content = content:match("^%s*(.-)%s*$") or content
        if content == "" then
            content = "图片或二进制数据"
        end
        noctalia.notify("已复制", content)
    end
end

local watchCommand = "wl-paste --watch sh -c 'printf \"COPIED|\"; wl-paste -n | head -n 1 | cut -c 1-50; echo'"
noctalia.runStream(watchCommand, onClipboardLine)
