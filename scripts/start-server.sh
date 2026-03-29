#!/usr/bin/env bash
# MCP server entrypoint — ensures venv is ready before starting.
set -euo pipefail

# Build venv if needed (idempotent, fast if already up to date)
bash "${CLAUDE_PLUGIN_ROOT}/hooks/install-deps.sh"

# Replace this process with the Python MCP server
exec "${CLAUDE_PLUGIN_DATA}/venv/bin/python" -m drive.server
