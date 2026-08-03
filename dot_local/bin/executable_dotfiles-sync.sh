#!/bin/bash
set -e

SOURCE_DIR="$(chezmoi source-path)"
LOG="$HOME/.local/share/chezmoi/sync.log"

cd "$SOURCE_DIR"

chezmoi re-add 2>>"$LOG"

# 密钥检查：提交前拦截疑似密钥，避免推送到 GitHub
# 仅匹配密钥特征，不匹配 css 属性名(sk-border)、键盘布局(keyboard-sk-qwerty)等正常内容
# 如确认安全可用 DOTFILES_SYNC_ALLOW_KEYS=1 强制放行
if [ -z "${DOTFILES_SYNC_ALLOW_KEYS:-}" ]; then
    HITS=$(git diff --cached | grep -nE '"apiKey"[[:space:]]*:[[:space:]]*"[^$!{]|sk-[A-Za-z0-9]{12,}|gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-[A-Za-z0-9-]{12,}' || true)
    if [ -n "$HITS" ]; then
        echo "检测到疑似密钥，已中止同步" >&2
        echo "命中的内容（前20行）：" >&2
        echo "$HITS" | head -20 >&2
        echo "确认安全后可用 DOTFILES_SYNC_ALLOW_KEYS=1 强制同步" >&2
        echo "本次变更未提交、未推送" >&2
        exit 1
    fi
fi

if ! git diff --cached --quiet 2>/dev/null || ! git diff --quiet 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "auto: $(date +%F-%T)" >>"$LOG" 2>&1
    git push origin master >>"$LOG" 2>&1
fi
