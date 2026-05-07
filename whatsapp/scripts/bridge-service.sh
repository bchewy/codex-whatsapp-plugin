#!/usr/bin/env bash
set -euo pipefail

label="com.brianchew.codex-whatsapp-bridge"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd "$script_dir/.." && pwd)"
plist="$HOME/Library/LaunchAgents/$label.plist"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/codex-whatsapp-plugin"
store_dir="${WHATSAPP_MCP_STORE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store}"
port="${WHATSAPP_BRIDGE_PORT:-8080}"
uid="$(id -u)"
service="gui/$uid/$label"

path_value="/opt/homebrew/bin:/usr/local/bin:/usr/local/go/bin:/usr/bin:/bin:/usr/sbin:/sbin"

usage() {
  cat <<EOF
Usage: bash scripts/bridge-service.sh <command>

Commands:
  install    Install and start the macOS LaunchAgent
  uninstall  Stop and remove the LaunchAgent
  start      Start the LaunchAgent
  stop       Stop the LaunchAgent
  restart    Restart the LaunchAgent
  status     Show LaunchAgent and bridge-port status
  logs       Tail recent bridge logs

The service runs scripts/start-bridge.sh in the background and writes logs under:
  $state_dir
EOF
}

write_plist() {
  mkdir -p "$HOME/Library/LaunchAgents" "$state_dir" "$store_dir"
  chmod 700 "$state_dir" "$store_dir"

  python3 - "$plist" "$label" "$script_dir/start-bridge.sh" "$plugin_root" "$state_dir" "$store_dir" "$port" "$path_value" <<'PY'
import plistlib
import sys
from pathlib import Path

plist_path, label, start_script, cwd, state_dir, store_dir, port, path_value = sys.argv[1:]
data = {
    "Label": label,
    "ProgramArguments": ["/bin/bash", start_script],
    "WorkingDirectory": cwd,
    "RunAtLoad": True,
    "KeepAlive": True,
    "EnvironmentVariables": {
        "PATH": path_value,
        "WHATSAPP_MCP_STORE_DIR": store_dir,
        "WHATSAPP_BRIDGE_PORT": port,
        "WHATSAPP_BRIDGE_SUPPRESS_QR": "1",
    },
    "StandardOutPath": str(Path(state_dir) / "bridge.launchd.out.log"),
    "StandardErrorPath": str(Path(state_dir) / "bridge.launchd.err.log"),
}

Path(plist_path).write_bytes(plistlib.dumps(data, sort_keys=False))
PY
}

is_loaded() {
  launchctl print "$service" >/dev/null 2>&1
}

install_service() {
  write_plist
  if is_loaded; then
    launchctl bootout "gui/$uid" "$plist" >/dev/null 2>&1 || true
  fi
  launchctl bootstrap "gui/$uid" "$plist"
  launchctl enable "$service" >/dev/null 2>&1 || true
  launchctl kickstart -k "$service"
}

stop_service() {
  if is_loaded; then
    launchctl bootout "gui/$uid" "$plist"
  fi
}

show_status() {
  if is_loaded; then
    echo "LaunchAgent: loaded ($service)"
    launchctl print "$service" | sed -n '1,80p'
  else
    echo "LaunchAgent: not loaded ($service)"
  fi

  if command -v nc >/dev/null 2>&1 && nc -z 127.0.0.1 "$port" >/dev/null 2>&1; then
    echo "Bridge: listening on 127.0.0.1:$port"
  else
    echo "Bridge: not listening on 127.0.0.1:$port"
  fi

  echo "Plist: $plist"
  echo "Logs:  $state_dir"
  echo "Store: $store_dir"
}

show_logs() {
  for file in "$state_dir/bridge.launchd.err.log" "$state_dir/bridge.launchd.out.log" "$state_dir/bridge.log"; do
    if [ -f "$file" ]; then
      echo "==> $file"
      tail -n 80 "$file"
    fi
  done
}

cmd="${1:-}"
case "$cmd" in
  install)
    install_service
    show_status
    ;;
  uninstall)
    stop_service || true
    rm -f "$plist"
    echo "Removed $plist"
    ;;
  start)
    if [ ! -f "$plist" ]; then
      write_plist
      launchctl bootstrap "gui/$uid" "$plist"
    else
      if ! is_loaded; then
        launchctl bootstrap "gui/$uid" "$plist"
      fi
    fi
    launchctl enable "$service" >/dev/null 2>&1 || true
    launchctl kickstart -k "$service"
    show_status
    ;;
  stop)
    stop_service
    show_status
    ;;
  restart)
    stop_service || true
    install_service
    show_status
    ;;
  status)
    show_status
    ;;
  logs)
    show_logs
    ;;
  *)
    usage
    exit 2
    ;;
esac
