import QtQuick
import QtQuick.Layouts
import Quickshell
import qs.Commons
import qs.Widgets
import qs.Services.UI

ColumnLayout {
    id: root
    spacing: Style.marginL

    property var pluginApi: null

    property string editExecutablePath: pluginApi?.pluginSettings?.executablePath || pluginApi?.manifest?.metadata?.defaultSettings?.executablePath || ""
    property string editTerminalCommand: pluginApi?.pluginSettings?.terminalCommand || pluginApi?.manifest?.metadata?.defaultSettings?.terminalCommand || "ghostty -e"
    property string editDefaultMode: pluginApi?.pluginSettings?.defaultMode || pluginApi?.manifest?.metadata?.defaultSettings?.defaultMode || "wifi"
    property int editDefaultPort: pluginApi?.pluginSettings?.defaultPort || pluginApi?.manifest?.metadata?.defaultSettings?.defaultPort || 8554
    property string editBarClickAction: pluginApi?.pluginSettings?.barClickAction || pluginApi?.manifest?.metadata?.defaultSettings?.barClickAction || "panel"
    property bool editAutoStart: pluginApi?.pluginSettings?.autoStart ?? pluginApi?.manifest?.metadata?.defaultSettings?.autoStart ?? false
    property bool editHideInactive: pluginApi?.pluginSettings?.hideInactive ?? pluginApi?.manifest?.metadata?.defaultSettings?.hideInactive ?? false
    property int editPollInterval: pluginApi?.pluginSettings?.pollInterval || pluginApi?.manifest?.metadata?.defaultSettings?.pollInterval || 3000

    function saveSettings() {
        if (!pluginApi || !pluginApi.pluginSettings) {
            Logger.e("MicYouPlugin", "Cannot save settings: pluginSettings is null");
            return;
        }

        pluginApi.pluginSettings.executablePath = root.editExecutablePath.trim();
        pluginApi.pluginSettings.terminalCommand = root.editTerminalCommand.trim();
        pluginApi.pluginSettings.defaultMode = root.editDefaultMode;
        pluginApi.pluginSettings.defaultPort = root.editDefaultPort;
        pluginApi.pluginSettings.barClickAction = root.editBarClickAction;
        pluginApi.pluginSettings.autoStart = root.editAutoStart;
        pluginApi.pluginSettings.hideInactive = root.editHideInactive;
        pluginApi.pluginSettings.pollInterval = root.editPollInterval;

        pluginApi.saveSettings();
        ToastService.showNotice(pluginApi.tr("settings.saved") || "MicYou 设置已保存");
    }

    // --- CLI Executable Path ---
    NTextInput {
        label: pluginApi?.tr("settings.executable-path") || "MicYou 可执行文件路径"
        description: pluginApi?.tr("settings.executable-path-desc") || "留空则自动检测 PATH、target/release 或 ~/.cargo/bin"
        text: root.editExecutablePath
        placeholderText: "micyou"
        onTextChanged: root.editExecutablePath = text
    }

    // --- Terminal Launcher Command ---
    NTextInput {
        label: pluginApi?.tr("settings.terminal-cmd") || "终端启动命令"
        description: pluginApi?.tr("settings.terminal-cmd-desc") || "用于启动 TUI 交互式终端的命令行前缀"
        text: root.editTerminalCommand
        placeholderText: "ghostty -e"
        onTextChanged: root.editTerminalCommand = text
    }

    NDivider { Layout.fillWidth: true }

    // --- Default Mode ---
    NComboBox {
        label: pluginApi?.tr("settings.default-mode") || "默认启动模式"
        description: pluginApi?.tr("settings.default-mode-desc") || "点击快速启动时采用的连接方式"
        model: [
            { "key": "wifi", "name": "Wi-Fi (局域网直连)" },
            { "key": "usb", "name": "USB (ADB 有线直连)" },
            { "key": "web", "name": "Web (浏览器扫码连接)" }
        ]
        currentKey: root.editDefaultMode
        onActivated: function(index) {
            root.editDefaultMode = model[index].key;
        }
    }

    // --- Default Port ---
    NTextInput {
        label: pluginApi?.tr("settings.default-port") || "默认音频端口"
        description: pluginApi?.tr("settings.default-port-desc") || "TCP 控制端口（UDP 音频流端口自动为端口+1）"
        text: String(root.editDefaultPort)
        placeholderText: "8554"
        onTextChanged: {
            var val = parseInt(text);
            if (!isNaN(val) && val > 0 && val < 65536) {
                root.editDefaultPort = val;
            }
        }
    }

    NDivider { Layout.fillWidth: true }

    // --- Bar Click Action ---
    NComboBox {
        label: pluginApi?.tr("settings.bar-click-action") || "状态栏图标左键点击行为"
        description: pluginApi?.tr("settings.bar-click-action-desc") || "选择左键点击状态栏图标时是打开控制面板还是直接切换服务运行状态"
        model: [
            { "key": "panel", "name": "打开控制面板 (Open Panel)" },
            { "key": "toggle", "name": "切换服务启停 (Toggle Service)" }
        ]
        currentKey: root.editBarClickAction
        onActivated: function(index) {
            root.editBarClickAction = model[index].key;
        }
    }

    // --- Auto Start ---
    NToggle {
        label: pluginApi?.tr("settings.auto-start") || "开机/启动时自动拉起 MicYou CLI"
        description: pluginApi?.tr("settings.auto-start-desc") || "在 Noctalia 状态栏加载完成后自动启动 MicYou 后台服务"
        checked: root.editAutoStart
        onToggled: function(c) { root.editAutoStart = c; }
        defaultValue: false
    }

    // --- Hide When Inactive ---
    NToggle {
        label: pluginApi?.tr("settings.hide-inactive") || "未运行时隐藏状态栏图标"
        description: pluginApi?.tr("settings.hide-inactive-desc") || "仅在 MicYou 服务处于运行或启动状态时在状态栏显示图标"
        checked: root.editHideInactive
        onToggled: function(c) { root.editHideInactive = c; }
        defaultValue: false
    }

    // --- Polling Interval ---
    ColumnLayout {
        Layout.fillWidth: true
        spacing: Style.marginS

        NText {
            text: (pluginApi?.tr("settings.poll-interval") || "状态轮询间隔") + ": " + (root.editPollInterval / 1000) + "s"
            pointSize: Style.fontSizeM
        }

        NSlider {
            Layout.fillWidth: true
            from: 1000
            to: 10000
            stepSize: 500
            value: root.editPollInterval
            onMoved: {
                root.editPollInterval = Math.round(value);
            }
        }
    }
}
