#!/usr/bin/env bash
# Entry point for the MCP server.

set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"

export PYTHONPATH="$DIR/src"
exec python3 -m claudemic.server
