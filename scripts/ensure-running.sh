#!/usr/bin/env bash
# Ensure the ClaudeMic daemon is running. Called by SessionStart hook.

set -euo pipefail

if ! command -v claudemic &>/dev/null; then
    echo "[ClaudeMic] Not installed. Run: pip install -e <plugin-dir>" >&2
    exit 0
fi

if claudemic status 2>/dev/null | grep -q "running"; then
    exit 0
fi

claudemic start
