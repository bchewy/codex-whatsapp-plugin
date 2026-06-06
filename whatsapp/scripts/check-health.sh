#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd "$script_dir/.." && pwd)"
bridge_dir="$plugin_root/build/vendor/whatsapp-mcp/whatsapp-bridge"
mcp_dir="$plugin_root/build/vendor/whatsapp-mcp/whatsapp-mcp-server"
uv_cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/codex-whatsapp-plugin"
WHATSAPP_MCP_STORE_DIR="${WHATSAPP_MCP_STORE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store}"
WHATSAPP_BRIDGE_PORT="${WHATSAPP_BRIDGE_PORT:-8080}"
status=0

ok() {
  printf 'ok: %s\n' "$1"
}

warn() {
  printf 'warn: %s\n' "$1" >&2
}

fail() {
  printf 'fail: %s\n' "$1" >&2
  status=1
}

need_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "$1 found at $(command -v "$1")"
  else
    fail "$1 is required"
  fi
}

printf 'Checking Codex WhatsApp plugin at %s\n' "$plugin_root"

need_cmd go
need_cmd uv

if command -v ffmpeg >/dev/null 2>&1; then
  ok "ffmpeg found at $(command -v ffmpeg)"
else
  warn "ffmpeg not found; send_audio_message can only send pre-converted .ogg Opus files"
fi

if [ -f "$bridge_dir/main.go" ] && [ -f "$bridge_dir/go.mod" ]; then
  ok "WhatsApp bridge source present"
else
  fail "WhatsApp bridge source missing at $bridge_dir"
fi

if [ -f "$mcp_dir/main.py" ] && [ -f "$mcp_dir/pyproject.toml" ]; then
  ok "WhatsApp MCP server source present"
else
  fail "WhatsApp MCP server source missing at $mcp_dir"
fi

if command -v uv >/dev/null 2>&1 && [ -d "$mcp_dir" ]; then
  mkdir -p "$uv_cache_dir"
  export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$uv_cache_dir/whatsapp-mcp-server-venv}"
  if uv --directory "$mcp_dir" run python -c 'import httpx, mcp, requests' >/dev/null 2>&1; then
    ok "Python MCP dependencies resolve with uv"
  else
    fail "Python MCP dependencies failed to resolve with uv"
  fi
fi

if command -v nc >/dev/null 2>&1; then
  if nc -z 127.0.0.1 "$WHATSAPP_BRIDGE_PORT" >/dev/null 2>&1; then
    ok "WhatsApp bridge is listening on 127.0.0.1:$WHATSAPP_BRIDGE_PORT"
  else
    warn "WhatsApp bridge is not listening on 127.0.0.1:$WHATSAPP_BRIDGE_PORT; run scripts/start-bridge.sh or scripts/bridge-service.sh install"
  fi
else
  warn "nc not found; skipping bridge port check"
fi

label="com.brianchew.codex-whatsapp-bridge"
if command -v launchctl >/dev/null 2>&1; then
  if launchctl print "gui/$(id -u)/$label" >/dev/null 2>&1; then
    ok "macOS LaunchAgent $label is loaded"
  else
    warn "macOS LaunchAgent $label is not loaded; optional: run scripts/bridge-service.sh install"
  fi
fi

if [ -d "$WHATSAPP_MCP_STORE_DIR" ]; then
  ok "Bridge store directory present at $WHATSAPP_MCP_STORE_DIR"
else
  warn "Bridge store directory not found at $WHATSAPP_MCP_STORE_DIR; will be created on first bridge start"
fi

exit "$status"
