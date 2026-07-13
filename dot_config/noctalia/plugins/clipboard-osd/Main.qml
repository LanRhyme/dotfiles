import QtQuick
import Quickshell.Io
import qs.Services.UI

Item {
    id: root

    property var pluginApi: null

    Process {
        id: watcher
        command: ["wl-paste", "--watch", "echo", "COPIED_CLIPBOARD"]
        running: true
        stdout.onReadyRead: {
            var data = stdout.readAll();
            var text = String(data);
            if (text.indexOf("COPIED_CLIPBOARD") !== -1) {
                showOsd();
            }
        }
    }

    function showOsd() {
        // Try different known signatures or fallback to notification
        if (typeof OsdService !== "undefined") {
            if (typeof OsdService.show === "function") {
                try {
                    OsdService.show("edit-copy", "已复制到剪贴板", 0);
                } catch (e) {
                    fallbackNotification();
                }
            } else if (typeof OsdService.showOsd === "function") {
                try {
                    OsdService.showOsd("edit-copy", "已复制到剪贴板");
                } catch (e) {
                    fallbackNotification();
                }
            } else {
                fallbackNotification();
            }
        } else {
            fallbackNotification();
        }
    }

    function fallbackNotification() {
        var p = Qt.createQmlObject('import Quickshell.Io; Process { command: ["noctalia", "msg", "notification-show", "已复制", "--", "已复制到剪贴板"] }', root);
        p.running = true;
    }
}
