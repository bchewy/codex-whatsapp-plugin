---
name: whatsapp
description: Use when the user wants Codex to search WhatsApp chats, read WhatsApp messages, inspect contacts, download WhatsApp media, send WhatsApp messages/media, create WhatsApp groups, or add participants to WhatsApp groups through this plugin.
version: 0.1.0
---

# WhatsApp MCP Workflow

This plugin wraps `lharries/whatsapp-mcp`, which has two moving parts:

1. A Go WhatsApp bridge in `vendor/whatsapp-mcp/whatsapp-bridge`.
2. A Python stdio MCP server in `vendor/whatsapp-mcp/whatsapp-mcp-server`.

The MCP server depends on the bridge listening at `http://127.0.0.1:8080/api`.

## Before Using Tools

1. Run `scripts/check-health.sh` from the plugin root when setup is uncertain.
2. The MCP startup script tries to auto-start the bridge in the background when
   `WHATSAPP_BRIDGE_AUTO_START` is not `0`. If setup is uncertain or the user
   needs to see the QR code, ask them to start it in a terminal with:

   ```bash
   bash scripts/start-bridge.sh
   ```

3. On first run, the user must scan the QR code from WhatsApp:
   `Settings > Linked Devices > Link a Device`.
4. For always-on background sync on macOS, use:

   ```bash
   bash scripts/bridge-service.sh install
   ```

   Then check it with:

   ```bash
   bash scripts/bridge-service.sh status
   ```

5. Keep one bridge process running while using WhatsApp MCP tools.

If this plugin is installed from a local marketplace, Codex may run the cached
installed copy under `~/.codex/plugins/cache/...`. Prefer helper scripts from
the same installed plugin copy so the Go bridge version matches the Python MCP
server version. Runtime auth, message indexes, and media live in the shared
external store under `${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store/`.

## Tool Use

Prefer read-only discovery before write actions:

- `search_contacts`: find a person or phone number.
- `list_chats`: inspect available chats.
- `get_chat`: inspect one chat by JID.
- `list_messages`: search or page through messages.
- `get_message_context`: inspect context around a message.
- `download_media`: download media for a message when the user asks for it.

For sends:

- Use `get_direct_chat_by_contact` or `search_contacts` first when the recipient is ambiguous.
- Confirm the exact recipient and message/media path before using `send_message`, `send_file`, or `send_audio_message`; set `confirm_send=true` only after that confirmation.
- For group sends, use the group JID ending in `@g.us`.
- For voice messages, prefer `.ogg` Opus. If the file is not `.ogg`, `ffmpeg` must be installed or the tool may fail.

For group participant changes:

- Use `list_chats`, `get_chat`, or prior context to verify the exact group JID ending in `@g.us`.
- Use `search_contacts` first when participant phone numbers/JIDs are ambiguous.
- Confirm the exact group name and participant list before using `create_group`; set `confirm_create=true` only after that confirmation.
- Confirm the exact group JID and participant list before using `add_group_participants`; set `confirm_add=true` only after that confirmation.
- To invite people when direct adds fail, use `add_or_invite_group_participants`. Set `confirm_add=true` only after confirming the exact group and participants. Set `confirm_invite_message=true` only after confirming fallback DMs should be sent.
- If WhatsApp rejects a direct add because of permissions or privacy settings, ask the user to use or share a group invite link instead.

## Privacy And Failure Modes

- WhatsApp auth, message indexes, downloaded media, and the local bridge token are stored locally under `${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store/` (override with `WHATSAPP_MCP_STORE_DIR`).
- Do not commit, upload, or summarize private message history beyond what the user asked for.
- If messages look stale, ask the user to leave the bridge running for sync to catch up.
- If auth is broken or the linked device expired, use `scripts/reset-session.sh` only after explicit user confirmation.
