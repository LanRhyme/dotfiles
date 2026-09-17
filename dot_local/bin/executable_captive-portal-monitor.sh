#!/bin/bash
# captive portal detection and notification
# uses D-Bus signals from NetworkManager — no polling

BROWSER="xdg-open"
LAST_STATE=""

send_notification() {
    notify-send -u critical -i network-wireless "$1" "$2"
}

open_portal() {
    local portal_url
    portal_url=$(nmcli -t -f DOMAIN connection show --active 2>/dev/null | head -1)
    [ -z "$portal_url" ] && portal_url="http://connectivitycheck.gstatic.com/generate_204"
    $BROWSER "$portal_url" &
}

handle_state() {
    local state="$1"
    [ "$state" = "$LAST_STATE" ] && return
    LAST_STATE="$state"

    case "$state" in
        PORTAL)
            send_notification "需要网络登录" "检测到需要认证的网络，正在打开登录页面..."
            open_portal
            ;;
        LIMITED)
            send_notification "网络受限" "已连接但无法访问互联网，可能需要登录"
            ;;
        NONE)
            send_notification "网络断开" "网络连接已断开"
            ;;
    esac
}

# 监听 D-Bus 信号，状态变化时才执行
dbus-monitor --system "type='signal',interface='org.freedesktop.NetworkManager',member='StateChanged'" 2>/dev/null |
while read -r line; do
    # 收到任意 NM 信号后检查连接状态
    if [[ "$line" == *"uint32"* ]]; then
        sleep 0.5  # 等待状态稳定
        state=$(nmcli -t -f CONNECTIVITY general 2>/dev/null)
        handle_state "$state"
    fi
done
