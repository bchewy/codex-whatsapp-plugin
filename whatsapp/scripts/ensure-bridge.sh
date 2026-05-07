#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$script_dir/bridge-env.sh"

cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/codex-whatsapp-plugin"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/codex-whatsapp-plugin"
lock_dir="$cache_dir/bridge-start.lock"
pid_file="$state_dir/bridge.pid"
log_file="$state_dir/bridge.log"

is_bridge_ready() {
  python3 - "$WHATSAPP_BRIDGE_PORT" "$WHATSAPP_BRIDGE_TOKEN" <<'PY' >/dev/null 2>&1
import json
import sys
import urllib.request

port, token = sys.argv[1], sys.argv[2]
request = urllib.request.Request(
    f"http://127.0.0.1:{port}/api/health",
    headers={"X-WhatsApp-Bridge-Token": token},
    method="GET",
)
with urllib.request.urlopen(request, timeout=0.5) as response:
    body = json.loads(response.read().decode("utf-8"))
    if response.status != 200 or body.get("success") is not True:
        raise SystemExit(1)
PY
}

wait_for_bridge() {
  attempts="${1:-30}"
  while [ "$attempts" -gt 0 ]; do
    if is_bridge_ready; then
      return 0
    fi
    attempts=$((attempts - 1))
    sleep 0.5
  done
  return 1
}

if is_bridge_ready; then
  exit 0
fi

umask 077
mkdir -p -m 700 "$WHATSAPP_MCP_STORE_DIR" "$cache_dir" "$state_dir"
chmod 700 "$WHATSAPP_MCP_STORE_DIR" "$cache_dir" "$state_dir"

if ! mkdir "$lock_dir" 2>/dev/null; then
  # Another MCP server instance is starting the bridge. Wait briefly and then
  # return control to the stdio MCP server; read-only tools can still use SQLite.
  wait_for_bridge 20 || true
  exit 0
fi
trap 'rmdir "$lock_dir" 2>/dev/null || true' EXIT

if is_bridge_ready; then
  exit 0
fi

{
  printf '\n[%s] Auto-starting WhatsApp bridge on 127.0.0.1:%s\n' "$(date -Iseconds)" "$WHATSAPP_BRIDGE_PORT"
  printf '[%s] Store: %s\n' "$(date -Iseconds)" "$WHATSAPP_MCP_STORE_DIR"
} >>"$log_file"

WHATSAPP_BRIDGE_SUPPRESS_QR=1 nohup bash "$script_dir/start-bridge.sh" >>"$log_file" 2>&1 </dev/null &
printf '%s\n' "$!" >"$pid_file"

if ! wait_for_bridge 30; then
  printf 'warn: WhatsApp bridge auto-started but did not pass the authenticated health check on 127.0.0.1:%s yet. See %s\n' "$WHATSAPP_BRIDGE_PORT" "$log_file" >&2
fi
