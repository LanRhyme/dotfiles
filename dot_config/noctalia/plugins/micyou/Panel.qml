import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import qs.Commons
import qs.Services.UI
import qs.Widgets

Item {
    id: root

    property var pluginApi: null
    property ShellScreen screen

    readonly property var geometryPlaceholder: panelContainer
    property real contentPreferredWidth: 480 * Style.uiScaleRatio
    property real contentPreferredHeight: 580 * Style.uiScaleRatio * (Settings.data?.ui?.fontDefaultScale ?? 1.0)
    readonly property bool allowAttach: true

    anchors.fill: parent

    readonly property var mainInstance: pluginApi?.mainInstance
    readonly property bool isRunning: mainInstance?.isRunning ?? false
    readonly property bool isStarting: mainInstance?.isStarting ?? false
    readonly property bool isStopping: mainInstance?.isStopping ?? false
    readonly property bool isAvailable: mainInstance?.isAvailable ?? false
    readonly property string mode: mainInstance?.connectionMode ?? "wifi"

    property int activeTab: 0 // 0: Service, 1: DSP, 2: ADB, 3: Logs

    Component.onCompleted: {
        if (mainInstance) {
            mainInstance.refreshAll();
        }
    }

    Rectangle {
        id: panelContainer
        anchors.fill: parent
        color: "transparent"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Style.marginL
            spacing: Style.marginM

            // --- HEADER ---
            RowLayout {
                Layout.fillWidth: true
                spacing: Style.marginM

                // Status Indicator Dot
                Rectangle {
                    width: 10 * Style.uiScaleRatio
                    height: 10 * Style.uiScaleRatio
                    radius: width / 2
                    color: root.isRunning ? Color.mSuccess ?? "#4caf50" : (root.isStarting || root.isStopping ? Color.mWarning ?? "#ff9800" : Color.mOutline ?? "#757575")
                }

                NText {
                    text: "MicYou"
                    pointSize: Style.fontSizeXL
                    font.weight: Style.fontWeightBold
                    color: Color.mOnSurface
                }

                // Mode Badge
                Rectangle {
                    visible: root.isRunning
                    radius: Style.radiusS
                    color: Qt.alpha(Color.mPrimary, 0.18)
                    implicitWidth: modeBadgeText.implicitWidth + Style.marginM * 2
                    implicitHeight: modeBadgeText.implicitHeight + Style.marginS

                    NText {
                        id: modeBadgeText
                        anchors.centerIn: parent
                        text: (mainInstance?.connectionMode || "wifi").toUpperCase()
                        pointSize: Style.fontSizeXS
                        font.weight: Style.fontWeightBold
                        color: Color.mPrimary
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                // Quick Reload / Refresh Button
                NIconButton {
                    icon: "reload"
                    tooltipText: pluginApi?.tr("panel.refresh") || "Refresh Status"
                    baseSize: Style.baseWidgetSize * 0.75
                    onClicked: {
                        if (mainInstance) mainInstance.refreshAll();
                    }
                }

                // Close Button
                NIconButton {
                    icon: "close"
                    tooltipText: I18n.tr("common.close")
                    baseSize: Style.baseWidgetSize * 0.75
                    onClicked: {
                        if (pluginApi) {
                            pluginApi.withCurrentScreen(function(s) { pluginApi.closePanel(s); });
                        }
                    }
                }
            }

            // --- TAB SWITCHER BAR ---
            RowLayout {
                Layout.fillWidth: true
                spacing: Style.marginS

                Repeater {
                    model: [
                        { "index": 0, "name": pluginApi?.tr("panel.tabs.service") || "服务", "icon": "server" },
                        { "index": 1, "name": pluginApi?.tr("panel.tabs.dsp") || "音频 DSP", "icon": "adjustments-horizontal" },
                        { "index": 2, "name": pluginApi?.tr("panel.tabs.adb") || "ADB 设备", "icon": "device-mobile" },
                        { "index": 3, "name": pluginApi?.tr("panel.tabs.logs") || "实时日志", "icon": "terminal-2" }
                    ]

                    delegate: Rectangle {
                        id: tabButton
                        Layout.fillWidth: true
                        height: 32 * Style.uiScaleRatio
                        radius: Style.radiusM
                        color: root.activeTab === modelData.index ? Color.mPrimary : (tabHover.hovered ? Qt.alpha(Color.mSurfaceVariant, 0.8) : Color.mSurfaceVariant)

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: Style.marginS

                            NIcon {
                                icon: modelData.icon
                                pointSize: Style.fontSizeS
                                color: root.activeTab === modelData.index ? Color.mOnPrimary : Color.mOnSurface
                            }

                            NText {
                                text: modelData.name
                                pointSize: Style.fontSizeS
                                font.weight: root.activeTab === modelData.index ? Style.fontWeightBold : Style.fontWeightNormal
                                color: root.activeTab === modelData.index ? Color.mOnPrimary : Color.mOnSurface
                            }
                        }

                        MouseArea {
                            id: tabHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                root.activeTab = modelData.index;
                            }
                        }
                    }
                }
            }

            NDivider {
                Layout.fillWidth: true
            }

            // --- TAB CONTENT CONTAINER ---
            StackLayout {
                id: tabStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: root.activeTab

                // ==========================================
                // TAB 0: 服务管理 (Service Management)
                // ==========================================
                ScrollView {
                    id: serviceTabScroll
                    clip: true
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                    ColumnLayout {
                        width: serviceTabScroll.width
                        spacing: Style.marginM

                        // Status Info Card
                        Rectangle {
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            border.color: Style.capsuleBorderColor
                            border.width: Style.capsuleBorderWidth
                            implicitHeight: statusCol.implicitHeight + Style.marginL * 2

                            ColumnLayout {
                                id: statusCol
                                anchors.fill: parent
                                anchors.margins: Style.marginL
                                spacing: Style.marginM

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.marginM

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        NText {
                                            text: root.isRunning
                                                ? (pluginApi?.tr("panel.status.running") || "MicYou 服务运行中")
                                                : (root.isStarting ? (pluginApi?.tr("messages.starting") || "正在启动...") : (pluginApi?.tr("panel.status.stopped") || "服务已停止"))
                                            pointSize: Style.fontSizeL
                                            font.weight: Style.fontWeightBold
                                            color: root.isRunning ? (Color.mSuccess ?? "#4caf50") : Color.mOnSurface
                                        }

                                        NText {
                                            text: root.isRunning
                                                ? ("PID: " + (mainInstance?.serverPid || "-") + " · 模式: " + (mainInstance?.serverMode || "CLI") + " · 已运行 " + (mainInstance?.startedAgo || 0) + "s")
                                                : (pluginApi?.tr("panel.status.stopped-hint") || "通过 CLI 启动以最小资源占用运行后台麦克风")
                                            pointSize: Style.fontSizeS
                                            color: Color.mOutline ?? Color.mOnSurfaceVariant
                                        }
                                    }

                                    // Big Start / Stop Button
                                    NButton {
                                        text: root.isRunning ? (pluginApi?.tr("panel.stop") || "停止服务") : (pluginApi?.tr("panel.start") || "启动 CLI")
                                        icon: root.isRunning ? "player-stop" : "player-play"
                                        colorBg: root.isRunning ? (Color.mError ?? "#d32f2f") : Color.mPrimary
                                        colorFg: root.isRunning ? (Color.mOnError ?? "#ffffff") : Color.mOnPrimary
                                        enabled: root.isAvailable && !root.isStarting && !root.isStopping
                                        onClicked: {
                                            if (!mainInstance) return;
                                            if (root.isRunning) {
                                                mainInstance.stopServer();
                                            } else {
                                                mainInstance.startServer(mainInstance.connectionMode, mainInstance.audioPort, mainInstance.selectedDevice, mainInstance.bindAddress);
                                            }
                                        }
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // PipeWire & Virtual Mic Status Row
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.marginM

                                    NIcon {
                                        icon: (mainInstance?.pipewireVirtualSink ?? false) ? "circle-check" : "alert-circle"
                                        color: (mainInstance?.pipewireVirtualSink ?? false) ? (Color.mSuccess ?? "#4caf50") : (Color.mWarning ?? "#ff9800")
                                        pointSize: Style.fontSizeM
                                    }

                                    NText {
                                        Layout.fillWidth: true
                                        text: (mainInstance?.pipewireVirtualSink ?? false)
                                            ? (pluginApi?.tr("panel.pipewire.ready") || "PipeWire 虚拟麦克风已就绪")
                                            : (pluginApi?.tr("panel.pipewire.auto") || "PipeWire 虚拟节点将在启动时自动创建")
                                        pointSize: Style.fontSizeS
                                        color: Color.mOnSurfaceVariant
                                    }
                                }
                            }
                        }

                        // Connection Mode Switcher
                        NText {
                            text: pluginApi?.tr("panel.mode-select") || "连接模式"
                            pointSize: Style.fontSizeM
                            font.weight: Style.fontWeightBold
                            color: Color.mOnSurface
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Style.marginM

                            // Wi-Fi Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 64 * Style.uiScaleRatio
                                radius: Style.radiusM
                                color: (mainInstance?.connectionMode === "wifi") ? Qt.alpha(Color.mPrimary, 0.2) : Color.mSurfaceVariant
                                border.color: (mainInstance?.connectionMode === "wifi") ? Color.mPrimary : Style.capsuleBorderColor
                                border.width: (mainInstance?.connectionMode === "wifi") ? 2 : 1

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 2

                                    NIcon {
                                        icon: "wifi"
                                        pointSize: Style.fontSizeL
                                        color: (mainInstance?.connectionMode === "wifi") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    NText {
                                        text: "Wi-Fi 模式"
                                        pointSize: Style.fontSizeS
                                        font.weight: (mainInstance?.connectionMode === "wifi") ? Style.fontWeightBold : Style.fontWeightNormal
                                        color: (mainInstance?.connectionMode === "wifi") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (mainInstance) mainInstance.setServerPref("mode", "wifi");
                                    }
                                }
                            }

                            // USB Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 64 * Style.uiScaleRatio
                                radius: Style.radiusM
                                color: (mainInstance?.connectionMode === "usb") ? Qt.alpha(Color.mPrimary, 0.2) : Color.mSurfaceVariant
                                border.color: (mainInstance?.connectionMode === "usb") ? Color.mPrimary : Style.capsuleBorderColor
                                border.width: (mainInstance?.connectionMode === "usb") ? 2 : 1

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 2

                                    NIcon {
                                        icon: "usb"
                                        pointSize: Style.fontSizeL
                                        color: (mainInstance?.connectionMode === "usb") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    NText {
                                        text: "USB (ADB)"
                                        pointSize: Style.fontSizeS
                                        font.weight: (mainInstance?.connectionMode === "usb") ? Style.fontWeightBold : Style.fontWeightNormal
                                        color: (mainInstance?.connectionMode === "usb") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (mainInstance) mainInstance.setServerPref("mode", "usb");
                                    }
                                }
                            }

                            // Web Card
                            Rectangle {
                                Layout.fillWidth: true
                                height: 64 * Style.uiScaleRatio
                                radius: Style.radiusM
                                color: (mainInstance?.connectionMode === "web") ? Qt.alpha(Color.mPrimary, 0.2) : Color.mSurfaceVariant
                                border.color: (mainInstance?.connectionMode === "web") ? Color.mPrimary : Style.capsuleBorderColor
                                border.width: (mainInstance?.connectionMode === "web") ? 2 : 1

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 2

                                    NIcon {
                                        icon: "world"
                                        pointSize: Style.fontSizeL
                                        color: (mainInstance?.connectionMode === "web") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                    NText {
                                        text: "Web 模式"
                                        pointSize: Style.fontSizeS
                                        font.weight: (mainInstance?.connectionMode === "web") ? Style.fontWeightBold : Style.fontWeightNormal
                                        color: (mainInstance?.connectionMode === "web") ? Color.mPrimary : Color.mOnSurface
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (mainInstance) mainInstance.setServerPref("mode", "web");
                                    }
                                }
                            }
                        }

                        // Server Parameters Card
                        Rectangle {
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            border.color: Style.capsuleBorderColor
                            border.width: Style.capsuleBorderWidth
                            implicitHeight: serverParamsCol.implicitHeight + Style.marginL * 2

                            ColumnLayout {
                                id: serverParamsCol
                                anchors.fill: parent
                                anchors.margins: Style.marginL
                                spacing: Style.marginM

                                // Port
                                RowLayout {
                                    Layout.fillWidth: true
                                    NText {
                                        text: (pluginApi?.tr("panel.port") || "音频端口") + ": " + (mainInstance?.audioPort || 8554)
                                        pointSize: Style.fontSizeM
                                        Layout.fillWidth: true
                                    }
                                    NText {
                                        text: "UDP: " + ((mainInstance?.audioPort || 8554) + 1)
                                        pointSize: Style.fontSizeS
                                        color: Color.mOutline ?? Color.mOnSurfaceVariant
                                    }
                                }

                                // Output Device Selector
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.marginS

                                    NText {
                                        text: pluginApi?.tr("panel.output-device") || "音频输出设备"
                                        pointSize: Style.fontSizeS
                                        color: Color.mOutline ?? Color.mOnSurfaceVariant
                                    }

                                    NComboBox {
                                        Layout.fillWidth: true
                                        model: (mainInstance?.devicesList && mainInstance.devicesList.length > 0)
                                            ? ["(Default / PipeWire Mic)"].concat(mainInstance.devicesList)
                                            : ["(Default / PipeWire Mic)"]
                                        currentText: (mainInstance?.selectedDevice && mainInstance.selectedDevice !== "") ? mainInstance.selectedDevice : "(Default / PipeWire Mic)"
                                        onActivated: function(index) {
                                            if (!mainInstance) return;
                                            var chosen = (index === 0) ? "" : mainInstance.devicesList[index - 1];
                                            mainInstance.setServerPref("outputDevice", chosen);
                                        }
                                    }
                                }
                            }
                        }

                        // Quick Actions & Launchers
                        NText {
                            text: pluginApi?.tr("panel.launchers") || "快速启动工具"
                            pointSize: Style.fontSizeM
                            font.weight: Style.fontWeightBold
                            color: Color.mOnSurface
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Style.marginM

                            NButton {
                                Layout.fillWidth: true
                                text: pluginApi?.tr("panel.launch-tui") || "打开 TUI 终端"
                                icon: "terminal-2"
                                onClicked: {
                                    if (mainInstance) mainInstance.launchTui();
                                }
                            }

                            NButton {
                                Layout.fillWidth: true
                                text: pluginApi?.tr("panel.launch-gui") || "启动桌面端 GUI"
                                icon: "layout-dashboard"
                                onClicked: {
                                    if (mainInstance) mainInstance.launchGui();
                                }
                            }
                        }
                    }
                }

                // ==========================================
                // TAB 1: 音频 DSP 处理 (Audio DSP)
                // ==========================================
                ScrollView {
                    id: dspTabScroll
                    clip: true
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                    ColumnLayout {
                        width: dspTabScroll.width
                        spacing: Style.marginM

                        // Gain Slider Card
                        Rectangle {
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            border.color: Style.capsuleBorderColor
                            border.width: Style.capsuleBorderWidth
                            implicitHeight: gainCol.implicitHeight + Style.marginL * 2

                            ColumnLayout {
                                id: gainCol
                                anchors.fill: parent
                                anchors.margins: Style.marginL
                                spacing: Style.marginS

                                RowLayout {
                                    Layout.fillWidth: true
                                    NText {
                                        text: pluginApi?.tr("panel.dsp.gain") || "输入增益 (Gain)"
                                        pointSize: Style.fontSizeM
                                        font.weight: Style.fontWeightBold
                                        Layout.fillWidth: true
                                    }
                                    NText {
                                        text: ((mainInstance?.dspGain ?? 0) > 0 ? "+" : "") + Math.round((mainInstance?.dspGain ?? 0) * 10) / 10 + " dB"
                                        pointSize: Style.fontSizeM
                                        font.weight: Style.fontWeightBold
                                        color: Color.mPrimary
                                    }
                                }

                                NSlider {
                                    Layout.fillWidth: true
                                    from: -20
                                    to: 20
                                    stepSize: 0.5
                                    value: mainInstance?.dspGain ?? 0.0
                                    onMoved: {
                                        if (mainInstance) {
                                            mainInstance.setDspSetting("gain", value);
                                        }
                                    }
                                }
                            }
                        }

                        // DSP Module Toggles
                        Rectangle {
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            border.color: Style.capsuleBorderColor
                            border.width: Style.capsuleBorderWidth
                            implicitHeight: dspTogglesCol.implicitHeight + Style.marginL * 2

                            ColumnLayout {
                                id: dspTogglesCol
                                anchors.fill: parent
                                anchors.margins: Style.marginL
                                spacing: Style.marginM

                                // AI Noise Suppression
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.ns") || "AI 智能降噪 (PureVox)"
                                    description: pluginApi?.tr("panel.dsp.ns-desc") || "轻量高效神经网络降噪滤除背景杂音"
                                    checked: mainInstance?.dspNsEnabled ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("nsEnabled", c);
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // AEC Echo Cancellation
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.aec") || "声学回声消除 (AEC)"
                                    description: pluginApi?.tr("panel.dsp.aec-desc") || "消除扬声器播放外放导致的回音"
                                    checked: mainInstance?.dspAecEnabled ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("aecEnabled", c);
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // Dereverb
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.dereverb") || "空间去混响 (Dereverb)"
                                    description: pluginApi?.tr("panel.dsp.dereverb-desc") || "削减房间回荡与空旷混响"
                                    checked: mainInstance?.dspDereverbEnabled ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("dereverbEnabled", c);
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // VAD Voice Activity Detection
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.vad") || "语音活动检测 (VAD)"
                                    description: pluginApi?.tr("panel.dsp.vad-desc") || "非说话状态自动降低静音底噪"
                                    checked: mainInstance?.dspVadEnabled ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("vadEnabled", c);
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // AGC Auto Gain
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.agc") || "自动增益控制 (AGC)"
                                    description: pluginApi?.tr("panel.dsp.agc-desc") || "自动平衡远近距离音量大小"
                                    checked: mainInstance?.dspAgcEnabled ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("agcEnabled", c);
                                    }
                                }

                                NDivider { Layout.fillWidth: true }

                                // Mute Toggle
                                NToggle {
                                    label: pluginApi?.tr("panel.dsp.mute") || "全局静音 (Mute)"
                                    description: pluginApi?.tr("panel.dsp.mute-desc") || "一键暂停麦克风音频传输输出"
                                    checked: mainInstance?.dspMute ?? false
                                    onToggled: function(c) {
                                        if (mainInstance) mainInstance.setDspSetting("mute", c);
                                    }
                                }
                            }
                        }

                        // Output Buffer Card
                        Rectangle {
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            border.color: Style.capsuleBorderColor
                            border.width: Style.capsuleBorderWidth
                            implicitHeight: bufferCol.implicitHeight + Style.marginL * 2

                            ColumnLayout {
                                id: bufferCol
                                anchors.fill: parent
                                anchors.margins: Style.marginL
                                spacing: Style.marginS

                                RowLayout {
                                    Layout.fillWidth: true
                                    NText {
                                        text: pluginApi?.tr("panel.dsp.buffer") || "音频输出缓冲"
                                        pointSize: Style.fontSizeM
                                        font.weight: Style.fontWeightBold
                                        Layout.fillWidth: true
                                    }
                                    NText {
                                        text: (mainInstance?.dspOutputBufferMs ?? 50) + " ms"
                                        pointSize: Style.fontSizeM
                                        font.weight: Style.fontWeightBold
                                        color: Color.mPrimary
                                    }
                                }

                                NSlider {
                                    Layout.fillWidth: true
                                    from: 10
                                    to: 200
                                    stepSize: 5
                                    value: mainInstance?.dspOutputBufferMs ?? 50
                                    onMoved: {
                                        if (mainInstance) {
                                            mainInstance.setDspSetting("outputBufferMs", Math.round(value));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // ==========================================
                // TAB 2: ADB 设备管理 (ADB Devices)
                // ==========================================
                ScrollView {
                    id: adbTabScroll
                    clip: true
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                    ColumnLayout {
                        width: adbTabScroll.width
                        spacing: Style.marginM

                        RowLayout {
                            Layout.fillWidth: true
                            NText {
                                text: pluginApi?.tr("panel.adb.title") || "已连接 Android 设备"
                                pointSize: Style.fontSizeM
                                font.weight: Style.fontWeightBold
                                Layout.fillWidth: true
                            }

                            NButton {
                                text: pluginApi?.tr("panel.refresh") || "刷新"
                                icon: "reload"
                                onClicked: {
                                    if (mainInstance) mainInstance.refreshAdb();
                                }
                            }
                        }

                        // Devices list
                        Repeater {
                            model: mainInstance?.adbDevices ?? []

                            delegate: Rectangle {
                                Layout.fillWidth: true
                                radius: Style.radiusM
                                color: Color.mSurfaceVariant
                                border.color: Style.capsuleBorderColor
                                border.width: Style.capsuleBorderWidth
                                implicitHeight: 56 * Style.uiScaleRatio

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: Style.marginM
                                    spacing: Style.marginM

                                    NIcon {
                                        icon: "device-mobile"
                                        pointSize: Style.fontSizeXL
                                        color: modelData.state === "device" ? (Color.mSuccess ?? "#4caf50") : (Color.mWarning ?? "#ff9800")
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        NText {
                                            text: modelData.description || modelData.serial
                                            pointSize: Style.fontSizeM
                                            font.weight: Style.fontWeightBold
                                        }

                                        NText {
                                            text: "SN: " + modelData.serial + " (" + modelData.state + ")"
                                            pointSize: Style.fontSizeS
                                            color: Color.mOutline ?? Color.mOnSurfaceVariant
                                        }
                                    }

                                    // Quick Switch to USB mode & run
                                    NButton {
                                        text: "启动 USB 服务"
                                        icon: "player-play"
                                        visible: modelData.state === "device" && !root.isRunning
                                        onClicked: {
                                            if (mainInstance) {
                                                mainInstance.setServerPref("mode", "usb");
                                                mainInstance.startServer("usb");
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Empty State
                        Rectangle {
                            visible: (mainInstance?.adbDevices?.length ?? 0) === 0
                            Layout.fillWidth: true
                            radius: Style.radiusM
                            color: Color.mSurfaceVariant
                            implicitHeight: 120 * Style.uiScaleRatio

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Style.marginM

                                NIcon {
                                    icon: "device-mobile-off"
                                    pointSize: 32 * Style.uiScaleRatio
                                    color: Color.mOutline ?? Color.mOnSurfaceVariant
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                NText {
                                    text: pluginApi?.tr("panel.adb.empty") || "未检测到已连接的 ADB 设备\n请通过 USB 连接手机并开启 USB 调试"
                                    pointSize: Style.fontSizeS
                                    horizontalAlignment: Text.AlignHCenter
                                    color: Color.mOutline ?? Color.mOnSurfaceVariant
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                }

                // ==========================================
                // TAB 3: 实时日志 (Live Logs)
                // ==========================================
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: Style.marginM

                    RowLayout {
                        Layout.fillWidth: true
                        NText {
                            text: pluginApi?.tr("panel.logs.title") || "CLI 实时输出日志"
                            pointSize: Style.fontSizeM
                            font.weight: Style.fontWeightBold
                            Layout.fillWidth: true
                        }

                        NButton {
                            text: pluginApi?.tr("panel.logs.config-dir") || "打开配置目录"
                            icon: "folder"
                            onClicked: {
                                if (mainInstance) mainInstance.openConfigDir();
                            }
                        }

                        NButton {
                            text: pluginApi?.tr("panel.logs.clear") || "清空"
                            icon: "trash"
                            onClicked: {
                                if (mainInstance) mainInstance.clearLogs();
                            }
                        }
                    }

                    // Terminal log display box
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: Style.radiusM
                        color: "#121412"
                        border.color: Style.capsuleBorderColor
                        border.width: Style.capsuleBorderWidth

                        ScrollView {
                            id: logScroll
                            anchors.fill: parent
                            anchors.margins: Style.marginM
                            clip: true

                            ListView {
                                id: logList
                                model: mainInstance?.logLines ?? []
                                width: logScroll.width
                                spacing: 2

                                delegate: Text {
                                    width: logList.width
                                    text: modelData
                                    font.family: Settings.data?.ui?.fontFixed ?? "monospace"
                                    font.pixelSize: 11 * Style.uiScaleRatio
                                    color: modelData.indexOf("error") !== -1 || modelData.indexOf("Error") !== -1
                                        ? "#ff6b6b"
                                        : (modelData.indexOf("Plugin") !== -1 ? "#4fc3f7" : "#a8d5ba")
                                    wrapMode: Text.WrapAnywhere
                                }

                                onCountChanged: {
                                    Qt.callLater(function() {
                                        logList.positionViewAtEnd();
                                    });
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
