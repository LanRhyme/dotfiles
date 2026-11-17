#!/usr/bin/env bash
# Tailscale 自愈看门狗
#
# 背景：tailscaled 通过 systemd drop-in 强制走本地代理 (127.0.0.1:7890)，
# 而 Tailscale 的受限 DNS 解析器会拒绝以 IP 字面量表示的代理地址，
# 导致 DialPlan 拨号路径永远失败、只剩回退路径。代理层一旦抖动
# （FlClash 换节点/重载订阅/短暂断连），tailscaled 会卡在无法自愈的状态，
# 表现为本机在控台显示 offline、controlhttp 持续拨号失败。
#
# 本脚本只做兜底：连续多次确认失联才动手，代理不通时不动手，
# 且限定冷却时间，避免在传输文件时反复打断会话。
#
# 调试：TS_WATCHDOG_ONCE=1 只诊断不动作

set -uo pipefail

PROXY_HOST="127.0.0.1"
PROXY_PORT="7890"
CHECK_INTERVAL="${TS_WATCHDOG_INTERVAL:-60}"
STREAK_NEED="${TS_WATCHDOG_STREAK:-2}"
COOLDOWN="${TS_WATCHDOG_COOLDOWN:-600}"
STAMP="${XDG_RUNTIME_DIR:-/tmp}/tailscale-watchdog.last"
ONCE="${TS_WATCHDOG_ONCE:-0}"

log() { printf '%s [watchdog] %s\n' "$(date '+%F %T')" "$*"; }

proxy_alive() { nc -z -w 2 "$PROXY_HOST" "$PROXY_PORT" >/dev/null 2>&1; }

control_reachable() {
    local code
    code=$(curl -x "http://${PROXY_HOST}:${PROXY_PORT}" -s -o /dev/null --max-time 8 \
        -w '%{http_code}' https://controlplane.tailscale.com/ 2>/dev/null)
    [[ "$code" =~ ^[1-5][0-9][0-9]$ ]]
}

# 0 = 判定失联，1 = 正常或不该干预
wedged() {
    local json state online text fails

    json=$(timeout 10 tailscale status --json 2>/dev/null) || {
        log "读不到 tailscale 状态，本轮跳过"
        return 1
    }
    state=$(jq -r '.BackendState // ""' <<<"$json")
    # 用户主动 down、未登录、停止等情况一律不干预
    [[ "$state" == "Running" ]] || return 1

    # 注意：不能用 jq 的 `// true`，该运算符会把 false 当空值吞掉
    online=$(jq -r '.Self.Online' <<<"$json")
    [[ "$online" == "false" ]] && return 0

    text=$(timeout 10 tailscale status 2>/dev/null)
    grep -q "Unable to connect to the Tailscale coordination server" <<<"$text" && return 0

    fails=$(journalctl -u tailscaled --since "-3min" --no-pager 2>/dev/null \
        | grep -c "controlhttp: failed dialing" || true)
    [[ "${fails:-0}" -ge 6 ]] && return 0

    return 1
}

heal() {
    local now last=0 out

    now=$(date +%s)
    if [[ -r "$STAMP" ]]; then
        last=$(<"$STAMP")
    fi
    [[ "$last" =~ ^[0-9]+$ ]] || last=0

    if ((now - last < COOLDOWN)); then
        log "冷却中（$(((COOLDOWN - (now - last)) / 60)) 分钟后可再次自愈），本轮不动手"
        return 1
    fi

    if ! proxy_alive; then
        log "本地代理 ${PROXY_HOST}:${PROXY_PORT} 不通，自愈无意义，跳过"
        return 1
    fi

    if ! control_reachable; then
        log "代理在但控台不可达，问题可能出在机场侧，先不动手"
        return 1
    fi

    log "确认控台失联，执行 tailscale down/up 自愈"
    timeout 20 tailscale down >/dev/null 2>&1
    sleep 3
    out=$(timeout 45 tailscale up 2>&1)
    log "tailscale up 返回: ${out:-<空>}"
    printf '%s' "$now" >"$STAMP"

    sleep 5
    if wedged; then
        log "自愈后仍失联，交给下一轮"
    else
        log "自愈成功，已重新入网"
    fi
}

main() {
    command -v tailscale >/dev/null 2>&1 || {
        log "找不到 tailscale 命令"
        exit 1
    }

    if [[ "$ONCE" == "1" ]]; then
        if wedged; then
            log "诊断结果: 判定失联（dry-run，不动作）"
        else
            log "诊断结果: 正常"
        fi
        exit 0
    fi

    log "启动 间隔=${CHECK_INTERVAL}s 连续阈值=${STREAK_NEED} 冷却=${COOLDOWN}s"
    local streak=0
    while true; do
        if wedged; then
            streak=$((streak + 1))
            log "检测到异常（连续 ${streak}/${STREAK_NEED}）"
            if ((streak >= STREAK_NEED)); then
                heal
                streak=0
            fi
        else
            if ((streak > 0)); then
                log "恢复正常，计数清零"
            fi
            streak=0
        fi
        sleep "$CHECK_INTERVAL"
    done
}

main "$@"
