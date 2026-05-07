#!/usr/bin/env bash
set -euo pipefail

store_dir="${WHATSAPP_MCP_STORE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store}"

cat >&2 <<EOF
This removes local WhatsApp auth and message index databases from:
$store_dir

You will need to scan the WhatsApp QR code again on the next bridge start.
Type RESET to continue:
EOF

read -r confirmation

if [ "$confirmation" != "RESET" ]; then
  echo "Reset cancelled." >&2
  exit 1
fi

rm -f \
  "$store_dir/messages.db" \
  "$store_dir/messages.db-shm" \
  "$store_dir/messages.db-wal" \
  "$store_dir/whatsapp.db" \
  "$store_dir/whatsapp.db-shm" \
  "$store_dir/whatsapp.db-wal"

echo "WhatsApp session databases removed from $store_dir." >&2
