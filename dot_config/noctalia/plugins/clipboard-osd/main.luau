--!nonstrict

local function onClipboardLine(line)
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

local watchCommand = "wl-paste --watch sh -c 'printf \"COPIED|\"; wl-paste -n --type text/plain 2>/dev/null | head -n 1 | cut -c 1-50; echo'"
noctalia.runStream(watchCommand, onClipboardLine)
