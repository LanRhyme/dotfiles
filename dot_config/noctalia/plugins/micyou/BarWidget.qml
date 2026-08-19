import QtQuick
import QtQuick.Layouts
import Quickshell
import qs.Commons
import qs.Services.UI
import qs.Services.System
import qs.Widgets

NIconButton {
    id: root

    property var pluginApi: null
    property ShellScreen screen
    property string widgetId: ""
    property string section: ""
    property int sectionWidgetIndex: -1
    property int sectionWidgetsCount: 0

    readonly property var mainInstance: pluginApi?.mainInstance
    readonly property bool isRunning: mainInstance?.isRunning ?? false
    readonly property bool isStarting: mainInstance?.isStarting ?? false
    readonly property bool isStopping: mainInstance?.isStopping ?? false
    readonly property bool isAvailable: mainInstance?.isAvailable ?? false
    readonly property string mode: mainInstance?.connectionMode ?? "wifi"

    readonly property string iconColorKey: pluginApi?.pluginSettings?.iconColor ?? "none"
    readonly property color iconColor: Color.resolveColorKeyOptional(iconColorKey) ?? Color.mOnSurface

    readonly property bool hideInactive: pluginApi?.pluginSettings?.hideInactive ?? false
    readonly property bool shouldShow: !hideInactive || isRunning || isStarting

    visible: true
    opacity: shouldShow ? (isStarting || isStopping ? 0.6 : 1.0) : 0.0
    implicitWidth: shouldShow ? baseSize : 0
    implicitHeight: shouldShow ? baseSize : 0

    Behavior on opacity {
        NumberAnimation { duration: Style.animationNormal }
    }
    Behavior on implicitWidth {
        NumberAnimation { duration: Style.animationNormal }
    }
    Behavior on implicitHeight {
        NumberAnimation { duration: Style.animationNormal }
    }

    enabled: isAvailable
    icon: isRunning ? (mode === "usb" ? "usb" : (mode === "web" ? "world" : "microphone")) : "microphone"
    tooltipText: mainInstance?.buildTooltip() || "MicYou"
    tooltipDirection: BarService.getTooltipDirection(screen?.name)
    baseSize: Style.getCapsuleHeightForScreen(screen?.name)
    applyUiScale: false
    customRadius: Style.radiusL

    colorBg: isRunning ? Color.mPrimary : (isStarting || isStopping ? Qt.alpha(Color.mSecondary, 0.3) : Style.capsuleColor)
    colorFg: isRunning ? Color.mOnPrimary : (isStarting || isStopping ? Color.mSecondary : root.iconColor)
    colorBorder: "transparent"
    colorBorderHover: "transparent"
    border.color: Style.capsuleBorderColor
    border.width: Style.capsuleBorderWidth

    onClicked: {
        if (!enabled) {
            ToastService.showError(
                pluginApi?.tr("messages.not-installed") || "MicYou Not Found",
                pluginApi?.tr("messages.not-installed-desc") || "Please install MicYou CLI"
            );
            return;
        }

        var action = pluginApi?.pluginSettings?.barClickAction || "panel";
        if (action === "toggle") {
            if (mainInstance) {
                if (isRunning) {
                    mainInstance.stopServer();
                } else {
                    mainInstance.startServer();
                }
            }
        } else {
            if (pluginApi) {
                pluginApi.openPanel(root.screen, this);
            }
        }
    }

    onRightClicked: {
        PanelService.showContextMenu(contextMenu, root, screen);
    }

    NPopupContextMenu {
        id: contextMenu

        model: {
            var items = [];

            if (root.isRunning) {
                items.push({
                    "label": pluginApi?.tr("panel.stop") || "Stop MicYou",
                    "action": "stop",
                    "icon": "player-stop"
                });
                items.push({
                    "label": pluginApi?.tr("panel.restart") || "Restart MicYou",
                    "action": "restart",
                    "icon": "reload"
                });
            } else {
                items.push({
                    "label": pluginApi?.tr("panel.start") || "Start MicYou (CLI)",
                    "action": "start",
                    "icon": "player-play"
                });
            }

            items.push({
                "label": (pluginApi?.tr("panel.mode") || "Mode") + ": Wi-Fi",
                "action": "set-wifi",
                "icon": "wifi"
            });
            items.push({
                "label": (pluginApi?.tr("panel.mode") || "Mode") + ": USB (ADB)",
                "action": "set-usb",
                "icon": "usb"
            });
            items.push({
                "label": (pluginApi?.tr("panel.mode") || "Mode") + ": Web",
                "action": "set-web",
                "icon": "world"
            });

            items.push({
                "label": pluginApi?.tr("panel.launch-tui") || "Open TUI (Terminal)",
                "action": "launch-tui",
                "icon": "terminal-2"
            });

            items.push({
                "label": pluginApi?.tr("panel.launch-gui") || "Open MicYou GUI",
                "action": "launch-gui",
                "icon": "layout-dashboard"
            });

            items.push({
                "label": I18n.tr("actions.widget-settings"),
                "action": "widget-settings",
                "icon": "settings"
            });

            return items;
        }

        onTriggered: function(action) {
            contextMenu.close();
            PanelService.closeContextMenu(screen);

            if (!mainInstance) return;

            if (action === "start") {
                mainInstance.startServer();
            } else if (action === "stop") {
                mainInstance.stopServer();
            } else if (action === "restart") {
                mainInstance.restartServer();
            } else if (action === "set-wifi") {
                mainInstance.setServerPref("mode", "wifi");
                if (root.isRunning) mainInstance.restartServer();
            } else if (action === "set-usb") {
                mainInstance.setServerPref("mode", "usb");
                if (root.isRunning) mainInstance.restartServer();
            } else if (action === "set-web") {
                mainInstance.setServerPref("mode", "web");
                if (root.isRunning) mainInstance.restartServer();
            } else if (action === "launch-tui") {
                mainInstance.launchTui();
            } else if (action === "launch-gui") {
                mainInstance.launchGui();
            } else if (action === "widget-settings") {
                BarService.openPluginSettings(screen, pluginApi.manifest);
            }
        }
    }
}
