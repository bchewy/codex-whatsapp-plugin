#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd "$script_dir/.." && pwd)"
bridge_dir="$plugin_root/vendor/whatsapp-mcp/whatsapp-bridge"

if ! command -v go >/dev/null 2>&1; then
  echo "Go is required to run the WhatsApp bridge. Install Go, then rerun this script." >&2
  exit 127
fi

if [ ! -f "$bridge_dir/main.go" ]; then
  echo "Missing vendored WhatsApp bridge at $bridge_dir." >&2
  exit 1
fi

# Stable bridge state directory, port, and local auth token shared with the Python MCP server.
source "$script_dir/bridge-env.sh"

cat >&2 <<EOF
Starting the WhatsApp bridge on http://127.0.0.1:${WHATSAPP_BRIDGE_PORT}/api.
State directory: ${WHATSAPP_MCP_STORE_DIR}

On first run, scan the QR code shown in this terminal from WhatsApp:
Settings > Linked Devices > Link a Device.

Keep this process running while Codex uses the WhatsApp MCP tools.
EOF

cd "$bridge_dir"
exec go run main.go
