#!/usr/bin/env bash
# Entry point for the MCP server. Auto-bootstraps a venv on first run.

set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$DIR/.venv"

# Auto-bootstrap venv if it doesn't exist
if [ ! -f "$VENV/bin/python3" ]; then
    echo "[ClaudeMic] Creating virtual environment..." >&2
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet -e "$DIR"
    echo "[ClaudeMic] Setup complete." >&2
fi

export PYTHONPATH="$DIR/src"
exec "$VENV/bin/python3" -m claudemic.server
