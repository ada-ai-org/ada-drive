#!/usr/bin/env bash
set -euo pipefail

# When run directly (e.g. from a skill), fall back to derived paths
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/ada-drive-ada-ai}"

VENV_DIR="${CLAUDE_PLUGIN_DATA}/venv"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
CHECKSUM_FILE="${CLAUDE_PLUGIN_DATA}/.pyproject-checksum"

# ── Check for uv ─────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "⚠ ada-drive: uv is required but not found." >&2
    echo "  Install it: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 0
fi

# ── Create venv if it doesn't exist ─────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "ada-drive: creating virtual environment..." >&2
    uv venv "$VENV_DIR"
fi

# ── Install/reinstall if pyproject.toml changed ─────────────────
CURRENT_CHECKSUM=$(shasum -a 256 "$PLUGIN_ROOT/pyproject.toml" | cut -d' ' -f1)
STORED_CHECKSUM=""
if [ -f "$CHECKSUM_FILE" ]; then
    STORED_CHECKSUM=$(cat "$CHECKSUM_FILE")
fi

if [ "$CURRENT_CHECKSUM" != "$STORED_CHECKSUM" ]; then
    echo "ada-drive: installing dependencies..." >&2
    uv pip install --python "$VENV_DIR" -e "$PLUGIN_ROOT"
    echo "$CURRENT_CHECKSUM" > "$CHECKSUM_FILE"
    echo "ada-drive: ready." >&2
fi

# ── Register in Claude Desktop (if installed) ────────────────────
VENV_PYTHON="$VENV_DIR/bin/python"

# Detect OS and resolve config path; skip silently if Desktop is not present
DESKTOP_CONFIG=""
case "$(uname -s)" in
    Darwin)
        CANDIDATE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
        # Only proceed if the Claude Desktop app or its config directory exists
        if [ -d "/Applications/Claude.app" ] || [ -d "$HOME/Library/Application Support/Claude" ]; then
            DESKTOP_CONFIG="$CANDIDATE"
        fi
        ;;
    Linux)
        CANDIDATE="$HOME/.config/Claude/claude_desktop_config.json"
        if [ -d "$HOME/.config/Claude" ]; then
            DESKTOP_CONFIG="$CANDIDATE"
        fi
        ;;
esac

if [ -n "$DESKTOP_CONFIG" ] && [ -f "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" - "$DESKTOP_CONFIG" "$VENV_PYTHON" "$PLUGIN_ROOT" << 'PYEOF'
import json, sys, pathlib

config_path = pathlib.Path(sys.argv[1])
venv_python, plugin_root = sys.argv[2], sys.argv[3]

config = {}
if config_path.exists():
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        pass  # treat corrupt file as empty

entry = {"command": venv_python, "args": ["-m", "drive.server"], "cwd": plugin_root}
if config.get("mcpServers", {}).get("ada-drive") == entry:
    sys.exit(0)  # already up to date

config.setdefault("mcpServers", {})["ada-drive"] = entry
config_path.parent.mkdir(parents=True, exist_ok=True)
config_path.write_text(json.dumps(config, indent=2))
print("ada-drive: registered in Claude Desktop.", file=sys.stderr)
PYEOF
fi
