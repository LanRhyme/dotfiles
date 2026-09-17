#!/bin/bash
# captive portal detection and notification
# monitors NetworkManager connectivity status

LAST_STATE=""
BROWSER="xdg-open"

check_connectivity() {
    local state
    state=$(nmcli -t -f CONNECTIVITY general 2>/dev/null)
    echo "$state"
}

send_notification() {
    local title="$1"
    local body="$2"
    notify-send -u critical -i network-wireless "$title" "$body"
}

open_portal() {
    # try to get the captive portal URL from NetworkManager
    local portal_url
    portal_url=$(nmcli -t -f DOMAIN connection show --active 2>/dev/null | head -1)
    
    if [ -z "$portal_url" ]; then
        # fallback: try common captive portal detection
        portal_url="http://connectivitycheck.gstatic.com/generate_204"
    fi
    
    $BROWSER "$portal_url" &
}

handle_state_change() {
    local new_state="$1"
    
    case "$new_state" in
        "PORTAL")
            send_notification "需要网络登录" "检测到需要认证的网络，正在打开登录页面..."
            open_portal
            ;;
        "LIMITED")
            send_notification "网络受限" "已连接但无法访问互联网，可能需要登录"
            ;;
        "NONE")
            send_notification "网络断开" "网络连接已断开"
            ;;
    esac
}

# main loop
while true; do
    CURRENT_STATE=$(check_connectivity)
    
    if [ "$CURRENT_STATE" != "$LAST_STATE" ]; then
        if [ -n "$LAST_STATE" ]; then
            handle_state_change "$CURRENT_STATE"
        fi
        LAST_STATE="$CURRENT_STATE"
    fi
    
    sleep 5
done
