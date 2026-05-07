# Notices

This plugin vendors `lharries/whatsapp-mcp`.

## whatsapp-mcp

- Source: https://github.com/lharries/whatsapp-mcp
- License: MIT
- Copyright: Copyright (c) 2025 Luke Harries

The upstream license is preserved at `vendor/whatsapp-mcp/LICENSE`.

## Trademarks

This project is an unofficial third-party integration and is not affiliated
with, endorsed by, or sponsored by WhatsApp, Meta, or their affiliates.
WhatsApp is a trademark of its respective owner. The plugin uses neutral
third-party artwork rather than WhatsApp brand assets.

## Runtime data

The vendored WhatsApp bridge stores private WhatsApp auth state, message
history, and downloaded media under
`${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store/` by default.
That directory also contains a local bridge token and is runtime-only; it must
not be committed, synced, or packaged with sample data. Legacy installs may still have data under
`vendor/whatsapp-mcp/whatsapp-bridge/store/`; treat both locations as private
runtime state.
