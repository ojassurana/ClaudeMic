#!/usr/bin/env bash
# Check that ClaudeMic dependencies are available. Called by SessionStart hook.

set -euo pipefail

missing=()

if ! command -v python3 &>/dev/null; then
    missing+=("python3")
fi

for pkg in sounddevice mcp openai; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        missing+=("$pkg")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "[ClaudeMic] Missing dependencies: ${missing[*]}" >&2
    echo "[ClaudeMic] Run: pip install -e ${CLAUDE_PLUGIN_ROOT:-.}" >&2
fi
