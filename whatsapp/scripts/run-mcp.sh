#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd "$script_dir/.." && pwd)"
mcp_dir="$plugin_root/build/vendor/whatsapp-mcp/whatsapp-mcp-server"
uv_cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/codex-whatsapp-plugin"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to run the WhatsApp MCP server. Install it from https://docs.astral.sh/uv/." >&2
  exit 127
fi

if [ ! -f "$mcp_dir/main.py" ]; then
  echo "Missing vendored WhatsApp MCP server at $mcp_dir." >&2
  exit 1
fi

mkdir -p "$uv_cache_dir"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$uv_cache_dir/whatsapp-mcp-server-venv}"

# Stable bridge state directory, port, and local auth token shared with the Go bridge.
source "$script_dir/bridge-env.sh"

if [ "${WHATSAPP_BRIDGE_AUTO_START:-1}" != "0" ]; then
  bash "$script_dir/ensure-bridge.sh" || true
fi

exec uv --directory "$mcp_dir" run main.py
