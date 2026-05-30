# Notices

This plugin vendors `lharries/whatsapp-mcp`.

## whatsapp-mcp

- Source: https://github.com/lharries/whatsapp-mcp
- License: MIT
- Copyright: Copyright (c) 2025 Luke Harries

The upstream license is preserved at `whatsapp/vendor/whatsapp-mcp/LICENSE`.

## Trademarks

This project is an unofficial third-party integration and is not affiliated
with, endorsed by, or sponsored by WhatsApp, Meta, or their affiliates.
WhatsApp and the WhatsApp logo are trademarks of their respective owner. The
plugin displays the WhatsApp logo only to identify the compatible service.

## Runtime data

The vendored WhatsApp bridge stores private WhatsApp auth state, message
history, and downloaded media under
`${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store/` by default.
That directory also contains a local bridge token and is runtime-only; it must
not be committed, synced, or packaged with sample data. Legacy installs may still have data under
`whatsapp/vendor/whatsapp-mcp/whatsapp-bridge/store/`; treat both locations as
private runtime state.
