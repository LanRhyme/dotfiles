#!/usr/bin/env bash
# game-mode.sh — 游戏时冻结后台 CPU/RAM 黑洞, 退出一键恢复
# 只发 SIGSTOP/SIGCONT, 不杀进程不丢状态, 冻结期间后台进程零 CPU 占用
# 用法: game-mode.sh on | off | status
set -uo pipefail

STATE="${XDG_RUNTIME_DIR:-/tmp}/game-mode.frozen"

# "名称|pgrep 正则" —— 只收会持续抢 CPU 的后台常驻
# 故意不含 Zen 浏览器与 Steam: 前者是当前对话界面, 后者是游戏父进程, 冻了会一起出事
TARGETS=(
	"Antigravity 语言服务器|/opt/Antigravity/resources/bin/language_server"
	"桌宠 slugcatpet|slugcatpet"
	"Bettbox|Bettbox"
)

is_stopped() { [ "$(ps -o stat= -p "$1" 2>/dev/null | cut -c1)" = "T" ]; }

case "${1:-status}" in
on)
	: >"$STATE"
	for t in "${TARGETS[@]}"; do
		name="${t%%|*}"
		pat="${t#*|}"
		for pid in $(pgrep -f -- "$pat" 2>/dev/null); do
			[ "$pid" = "$$" ] && continue
			if is_stopped "$pid" || kill -STOP "$pid" 2>/dev/null; then
				printf '%s|%s\n' "$pid" "$name" >>"$STATE"
				echo "冻结 [${name}] PID ${pid}"
			fi
		done
	done
	if [ -s "$STATE" ]; then
		echo "--- 退出游戏后执行: $(basename "$0") off"
	else
		echo "没有需要冻结的进程"
	fi
	;;
off)
	if [ ! -s "$STATE" ]; then
		echo "没有记录在案的冻结进程"
		exit 0
	fi
	while IFS='|' read -r pid name; do
		[ -d "/proc/${pid}" ] || continue
		kill -CONT "$pid" 2>/dev/null && echo "恢复 [${name}] PID ${pid}"
	done <"$STATE"
	: >"$STATE"
	;;
status)
	if [ -s "$STATE" ]; then
		while IFS='|' read -r pid name; do
			st=$(ps -o stat= -p "$pid" 2>/dev/null | cut -c1)
			echo "PID ${pid}  ${name}  ->  ${st:-(已退出)}"
		done <"$STATE"
	else
		echo "当前未冻结任何进程"
	fi
	;;
*)
	echo "用法: $(basename "$0") on|off|status" >&2
	exit 2
	;;
esac
