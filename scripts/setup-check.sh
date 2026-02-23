#!/usr/bin/env bash
# SessionStart hook: verify python3 is available for venv bootstrap.

set -euo pipefail

if ! command -v python3 &>/dev/null; then
    echo "[ClaudeMic] python3 not found. Install Python 3.10+ to use this plugin." >&2
fi
