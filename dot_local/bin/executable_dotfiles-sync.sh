#!/bin/bash
set -e

SOURCE_DIR="$(chezmoi source-path)"
LOG="$HOME/.local/share/chezmoi/sync.log"

cd "$SOURCE_DIR"

chezmoi re-add 2>>"$LOG"

if ! git diff --cached --quiet 2>/dev/null || ! git diff --quiet 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "auto: $(date +%F-%T)" >>"$LOG" 2>&1
    git push origin master >>"$LOG" 2>&1
fi
