import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Services.UI
import qs.Services.System

Item {
    id: root

    property var pluginApi: null

    // State
    property bool isAvailable: false
    property string resolvedBin: ""
    property bool isRunning: false
    property bool isManagedProcess: false
    property int serverPid: 0
    property string serverMode: "none" // "CLI", "GUI", "TUI", "none"
    property int startedAgo: 0
    property bool isStarting: false
    property bool isStopping: false

    // Server prefs & connection state
    property string connectionMode: "wifi" // "wifi" | "usb" | "web"
    property int audioPort: 8554
    property int webPort: 8556
    property string bindAddress: "0.0.0.0"
    property bool autoBind: true
    property string selectedDevice: ""

    // Devices & Virtual Mics
    property var devicesList: []
    property var adbDevices: []
    property bool pipewireAvailable: false
    property bool pipewireVirtualSink: false

    // DSP Audio Settings
    property real dspGain: 0.0
    property bool dspNsEnabled: false
    property string dspNsModel: "PureVox"
    property bool dspAecEnabled: false
    property bool dspDereverbEnabled: false
    property bool dspVadEnabled: false
    property bool dspAgcEnabled: false
    property int dspOutputBufferMs: 50
    property bool dspMute: false
    property var dspChain: []

    // Live Logs
    property var logLines: []
    readonly property int maxLogLines: 120

    // Settings helpers
    readonly property string customBinPath: pluginApi?.pluginSettings?.executablePath || ""
    readonly property string terminalCmd: pluginApi?.pluginSettings?.terminalCommand || "ghostty -e"
    readonly property int pollIntervalMs: pluginApi?.pluginSettings?.pollInterval || 3000
    readonly property bool autoStart: pluginApi?.pluginSettings?.autoStart ?? false
    readonly property string defaultMode: pluginApi?.pluginSettings?.defaultMode || "wifi"
    readonly property int defaultPort: pluginApi?.pluginSettings?.defaultPort || 8554
    readonly property string barClickAction: pluginApi?.pluginSettings?.barClickAction || "panel"
    readonly property bool hideInactive: pluginApi?.pluginSettings?.hideInactive ?? false
    readonly property string iconColorKey: pluginApi?.pluginSettings?.iconColor || "none"

    function addLogLine(line) {
        if (!line) return;
        var clean = String(line).trimEnd();
        if (clean.length === 0) return;
        
        var next = logLines.slice();
        next.push(clean);
        if (next.length > maxLogLines) {
            next.shift();
        }
        logLines = next;
    }

    function clearLogs() {
        logLines = [];
    }

    // Binary detector
    Process {
        id: binDetector
        command: ["sh", "-c", "which micyou 2>/dev/null || ([ -x /home/lanrhyme/Projects/MicYou/tauri-app/target/release/micyou ] && echo /home/lanrhyme/Projects/MicYou/tauri-app/target/release/micyou) || ([ -x /home/lanrhyme/Projects/MicYou/tauri-app/target/debug/micyou ] && echo /home/lanrhyme/Projects/MicYou/tauri-app/target/debug/micyou) || ([ -x /home/lanrhyme/.cargo/bin/micyou ] && echo /home/lanrhyme/.cargo/bin/micyou) || which micyou-cli 2>/dev/null || echo ''"]
        running: true
        stdout: StdioCollector {
            onStreamFinished: {
                var path = text.trim();
                if (root.customBinPath && root.customBinPath.trim() !== "") {
                    root.resolvedBin = root.customBinPath.trim();
                    root.isAvailable = true;
                } else if (path !== "") {
                    root.resolvedBin = path;
                    root.isAvailable = true;
                } else {
                    root.resolvedBin = "micyou";
                    root.isAvailable = false;
                }
                if (root.isAvailable) {
                    refreshAll();
                    if (root.autoStart && !root.isRunning) {
                        startServer(root.defaultMode, root.defaultPort);
                    }
                }
            }
        }
    }

    // Status checker process
    Process {
        id: statusChecker
        command: [root.resolvedBin || "micyou", "status"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                root.parseStatus(text);
            }
        }
        onExited: function(code) {
            if (code !== 0 && !root.isManagedProcess) {
                root.isRunning = false;
                root.serverMode = "none";
                root.serverPid = 0;
            }
        }
    }

    function parseStatus(out) {
        if (!out) return;
        var lines = out.split("\n");
        var foundMode = "none";
        var foundPid = 0;
        var foundAgo = 0;
        var running = false;

        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (line.startsWith("mode:")) {
                foundMode = line.substring(5).trim();
                running = true;
            } else if (line.startsWith("pid:")) {
                foundPid = parseInt(line.substring(4).trim()) || 0;
            } else if (line.startsWith("started") && line.indexOf("s ago") !== -1) {
                var match = line.match(/started\s+(\d+)s\s+ago/);
                if (match) {
                    foundAgo = parseInt(match[1]) || 0;
                }
            } else if (line.indexOf("no server running") !== -1) {
                running = false;
                foundMode = "none";
                foundPid = 0;
            }
        }

        root.isRunning = running || root.isManagedProcess;
        if (running) {
            root.serverMode = foundMode;
            root.serverPid = foundPid;
            root.startedAgo = foundAgo;
        } else if (!root.isManagedProcess) {
            root.serverMode = "none";
            root.serverPid = 0;
            root.startedAgo = 0;
        }
    }

    // Server Prefs Process (micyou server get)
    Process {
        id: serverPrefsGetter
        command: [root.resolvedBin || "micyou", "server", "get"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                var lines = text.split("\n");
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i].trim();
                    if (line.startsWith("mode:")) {
                        root.connectionMode = line.substring(5).trim();
                    } else if (line.startsWith("port:")) {
                        root.audioPort = parseInt(line.substring(5).trim()) || 8554;
                    } else if (line.startsWith("webPort:")) {
                        root.webPort = parseInt(line.substring(8).trim()) || 8556;
                    } else if (line.startsWith("bindAddress:")) {
                        root.bindAddress = line.substring(12).trim();
                    } else if (line.startsWith("autoBind:")) {
                        root.autoBind = line.substring(9).trim() === "true";
                    } else if (line.startsWith("outputDevice:")) {
                        root.selectedDevice = line.substring(13).trim();
                    }
                }
            }
        }
    }

    // Settings DSP Getter (micyou settings get)
    Process {
        id: dspSettingsGetter
        command: [root.resolvedBin || "micyou", "settings", "get"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var parsed = JSON.parse(text.trim());
                    if (parsed) {
                        if (parsed.gain !== undefined) root.dspGain = parsed.gain;
                        if (parsed.nsEnabled !== undefined) root.dspNsEnabled = parsed.nsEnabled;
                        if (parsed.nsModel !== undefined) root.dspNsModel = parsed.nsModel;
                        if (parsed.aecEnabled !== undefined) root.dspAecEnabled = parsed.aecEnabled;
                        if (parsed.dereverbEnabled !== undefined) root.dspDereverbEnabled = parsed.dereverbEnabled;
                        if (parsed.vadEnabled !== undefined) root.dspVadEnabled = parsed.vadEnabled;
                        if (parsed.agcEnabled !== undefined) root.dspAgcEnabled = parsed.agcEnabled;
                        if (parsed.outputBufferMs !== undefined) root.dspOutputBufferMs = parsed.outputBufferMs;
                        if (parsed.mute !== undefined) root.dspMute = parsed.mute;
                        if (parsed.processingChain !== undefined) root.dspChain = parsed.processingChain;
                    }
                } catch (e) {
                    // Not json or error
                }
            }
        }
    }

    // Audio Devices Getter (micyou devices)
    Process {
        id: devicesGetter
        command: [root.resolvedBin || "micyou", "devices"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                var lines = text.split("\n");
                var devs = [];
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i].trim();
                    var match = line.match(/^\d+\.\s+(.*)$/);
                    if (match && match[1]) {
                        devs.push(match[1]);
                    }
                }
                root.devicesList = devs;
            }
        }
    }

    // PipeWire Mics Status (micyou mics)
    Process {
        id: micsGetter
        command: [root.resolvedBin || "micyou", "mics"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                root.pipewireAvailable = text.indexOf("available: true") !== -1;
                root.pipewireVirtualSink = text.indexOf("virtual sink: true") !== -1;
            }
        }
    }

    // ADB Devices Getter (micyou adb-devices)
    Process {
        id: adbGetter
        command: [root.resolvedBin || "micyou", "adb-devices"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                var lines = text.split("\n");
                var devs = [];
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i].trim();
                    // e.g. "  ed3fdd92 (device) - mondrian"
                    var match = line.match(/^([a-zA-Z0-9_-]+)\s+\(([^)]+)\)\s+-\s+(.*)$/);
                    if (match) {
                        devs.push({
                            serial: match[1],
                            state: match[2],
                            description: match[3]
                        });
                    }
                }
                root.adbDevices = devs;
            }
        }
    }

    // Background Process for CLI Serve
    Process {
        id: serveProcess
        command: []
        running: false

        stdout: SplitParser {
            onRead: data => {
                root.addLogLine(data);
            }
        }

        stderr: SplitParser {
            onRead: data => {
                root.addLogLine(data);
            }
        }

        onExited: function(exitCode, exitStatus) {
            root.isManagedProcess = false;
            root.isStarting = false;
            root.isStopping = false;
            root.addLogLine("[MicYou Plugin] Service exited with code: " + exitCode);
            
            if (exitCode !== 0 && exitCode !== 130 && exitCode !== 143) {
                ToastService.showError(
                    root.pluginApi?.tr("messages.service-error") || "MicYou Error",
                    (root.pluginApi?.tr("messages.service-crashed") || "MicYou CLI exited with error code: ") + exitCode
                );
            } else {
                ToastService.showNotice(
                    root.pluginApi?.tr("messages.service-stopped") || "MicYou Service Stopped",
                    "",
                    "microphone-off"
                );
            }
            root.refreshStatus();
        }
    }

    // Poller timer
    Timer {
        id: pollerTimer
        interval: root.pollIntervalMs
        repeat: true
        running: true
        onTriggered: {
            if (root.isAvailable) {
                root.refreshStatus();
            }
        }
    }

    function refreshAll() {
        if (!isAvailable) return;
        statusChecker.running = true;
        serverPrefsGetter.running = true;
        dspSettingsGetter.running = true;
        devicesGetter.running = true;
        micsGetter.running = true;
        adbGetter.running = true;
    }

    function refreshStatus() {
        if (isAvailable) {
            statusChecker.running = true;
        }
    }

    function refreshAdb() {
        if (isAvailable) {
            adbGetter.running = true;
        }
    }

    function refreshDevices() {
        if (isAvailable) {
            devicesGetter.running = true;
        }
    }

    function startServer(mode, port, device, bind) {
        if (!isAvailable) {
            ToastService.showError(
                pluginApi?.tr("messages.not-installed") || "MicYou Not Found",
                pluginApi?.tr("messages.not-installed-desc") || "Please install or configure the MicYou CLI binary."
            );
            return;
        }

        if (isRunning || isManagedProcess) {
            return;
        }

        var m = mode || connectionMode || "wifi";
        var p = port || audioPort || 8554;
        var args = [resolvedBin, "serve", "--mode", m, "--port", String(p)];

        if (device && device.trim() !== "") {
            args.push("--device", device.trim());
        }
        if (bind && bind.trim() !== "") {
            args.push("--bind", bind.trim());
        }

        isStarting = true;
        addLogLine("[MicYou Plugin] Starting: " + args.join(" "));
        serveProcess.command = args;
        serveProcess.running = true;
        isManagedProcess = true;
        isRunning = true;
        serverMode = "CLI";

        ToastService.showNotice(
            pluginApi?.tr("messages.service-started") || "MicYou Service Started",
            (pluginApi?.tr("panel.mode") || "Mode") + ": " + m.toUpperCase() + " (" + p + ")",
            "microphone"
        );

        // Delayed check
        delayedCheckTimer.restart();
    }

    Timer {
        id: delayedCheckTimer
        interval: 1000
        repeat: false
        onTriggered: {
            root.isStarting = false;
            root.refreshAll();
        }
    }

    function stopServer() {
        if (!isRunning && !isManagedProcess) return;

        isStopping = true;
        addLogLine("[MicYou Plugin] Stopping service...");

        if (serveProcess.running) {
            serveProcess.running = false;
        } else if (serverPid > 0) {
            // Send SIGINT / SIGTERM to existing external CLI process
            Quickshell.execDetached(["kill", "-SIGINT", String(serverPid)]);
        } else {
            Quickshell.execDetached(["pkill", "-SIGINT", "-f", "micyou serve"]);
        }

        stopCheckTimer.restart();
    }

    Timer {
        id: stopCheckTimer
        interval: 800
        repeat: false
        onTriggered: {
            root.isStopping = false;
            root.isManagedProcess = false;
            root.refreshStatus();
        }
    }

    function restartServer() {
        stopServer();
        restartTimer.restart();
    }

    Timer {
        id: restartTimer
        interval: 1200
        repeat: false
        onTriggered: {
            root.startServer(root.connectionMode, root.audioPort, root.selectedDevice, root.bindAddress);
        }
    }

    function launchTui() {
        var term = terminalCmd || "ghostty -e";
        var parts = term.split(" ").filter(function(s) { return s.length > 0; });
        parts.push(resolvedBin);
        addLogLine("[MicYou Plugin] Launching TUI in terminal: " + parts.join(" "));
        Quickshell.execDetached(parts);
    }

    function launchGui() {
        addLogLine("[MicYou Plugin] Launching MicYou GUI...");
        Quickshell.execDetached(["sh", "-c", "micyou-app || (command -v flatpak >/dev/null && flatpak run com.lanrhyme.micyou) || /home/lanrhyme/Projects/MicYou/tauri-app/target/release/micyou-app"]);
    }

    function setServerPref(key, value) {
        if (!isAvailable) return;
        Quickshell.execDetached([resolvedBin, "server", "set", key, String(value)]);
        var updateTimer = Qt.createQmlObject('import QtQuick; Timer { interval: 300; repeat: false; onTriggered: { root.serverPrefsGetter.running = true; destroy(); } }', root);
        updateTimer.start();
    }

    function setDspSetting(key, value) {
        if (!isAvailable) return;
        Quickshell.execDetached([resolvedBin, "settings", "set", key, String(value)]);
        var updateTimer = Qt.createQmlObject('import QtQuick; Timer { interval: 300; repeat: false; onTriggered: { root.dspSettingsGetter.running = true; destroy(); } }', root);
        updateTimer.start();
    }

    function openConfigDir() {
        Quickshell.execDetached(["xdg-open", Quickshell.env("HOME") + "/.config/micyou"]);
    }

    function buildTooltip() {
        if (!isAvailable) {
            return pluginApi?.tr("messages.not-installed") || "MicYou CLI not found";
        }
        if (isStarting) {
            return pluginApi?.tr("messages.starting") || "Starting MicYou...";
        }
        if (isStopping) {
            return pluginApi?.tr("messages.stopping") || "Stopping MicYou...";
        }
        if (isRunning) {
            var info = "MicYou (" + serverMode + ")\n";
            info += (pluginApi?.tr("panel.mode") || "Mode") + ": " + connectionMode.toUpperCase() + " :" + audioPort + "\n";
            if (serverPid > 0) info += "PID: " + serverPid + " (" + startedAgo + "s)\n";
            if (dspNsEnabled) info += "• " + (pluginApi?.tr("panel.dsp.ns") || "Noise Suppression") + "\n";
            if (dspAecEnabled) info += "• " + (pluginApi?.tr("panel.dsp.aec") || "AEC") + "\n";
            if (dspGain !== 0) info += "• Gain: " + (dspGain > 0 ? "+" : "") + dspGain + "dB\n";
            return info.trim();
        }
        return (pluginApi?.tr("messages.stopped-tooltip") || "MicYou: Stopped\nClick to manage");
    }

    // IPC support for Noctalia keybinds / scripts
    IpcHandler {
        target: "plugin:micyou"

        function toggle() {
            if (root.isRunning) {
                root.stopServer();
            } else {
                root.startServer(root.connectionMode, root.audioPort);
            }
        }

        function start() {
            root.startServer(root.connectionMode, root.audioPort);
        }

        function stop() {
            root.stopServer();
        }

        function restart() {
            root.restartServer();
        }

        function openPanel() {
            pluginApi?.withCurrentScreen(function(s) { pluginApi.openPanel(s); });
        }
    }
}
