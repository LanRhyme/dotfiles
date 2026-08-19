import QtQuick
import Quickshell
import qs.Widgets
import qs.Commons

NIconButton {
    property ShellScreen screen
    property var pluginApi: null
    readonly property var mainInstance: pluginApi?.mainInstance

    enabled: mainInstance?.isAvailable ?? false
    icon: (mainInstance?.isRunning) ? "microphone" : "microphone-off"
    tooltipText: mainInstance?.buildTooltip() || "MicYou"
    colorFg: (mainInstance?.isRunning) ? Color.mOnPrimary : Color.mPrimary
    colorBg: (mainInstance?.isRunning) ? Color.mPrimary : Style.capsuleColor

    onClicked: {
        if (!mainInstance) return;
        if (mainInstance.isRunning) {
            mainInstance.stopServer();
        } else {
            mainInstance.startServer();
        }
    }
}
