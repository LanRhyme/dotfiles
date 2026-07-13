import QtQuick
import Quickshell.Io
import qs.Services.UI

Item {
    id: root

    property var pluginApi: null

    Process {
        id: watcher
        command: ["wl-paste", "--watch", "sh", "-c", "printf \"COPIED_CLIPBOARD|\"; wl-paste -n | head -n 1 | cut -c 1-50; echo"]
        running: true
        stdout: SplitParser {
            onRead: data => {
                var text = String(data).trim();
                if (text.startsWith("COPIED_CLIPBOARD|")) {
                    var content = text.substring("COPIED_CLIPBOARD|".length).trim();
                    if (content.length === 0) content = "图片或二进制数据";
                    showOsd(content);
                }
            }
        }
    }

    function showOsd(content) {
        // Try Noctalia 5 ToastService first (usually better for text notifications)
        if (typeof ToastService !== "undefined" && typeof ToastService.showNotice === "function") {
            ToastService.showNotice("已复制到剪贴板", content, "edit-copy", 2000);
        } else {
            // Fallback
            var p = Qt.createQmlObject('import Quickshell.Io; Process { command: ["noctalia", "msg", "notification-show", "已复制到剪贴板", "--", "' + content.replace(/"/g, '\\"') + '"] }', root);
            p.running = true;
        }
    }
}
