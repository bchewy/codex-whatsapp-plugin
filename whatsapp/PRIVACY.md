# Privacy Policy

This plugin is an unofficial local bridge for a personal WhatsApp account. It
is not affiliated with, endorsed by, or operated by WhatsApp or Meta.

## Local Data

The plugin stores WhatsApp linked-device session data, message indexes,
downloaded media, and the local bridge token on your machine under:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/codex-whatsapp-plugin/store/
```

You can override this location with `WHATSAPP_MCP_STORE_DIR`.

## What Codex Can Access

When the plugin is enabled, Codex can use the local MCP tools to search chats,
read indexed messages and events, inspect contacts, download requested media,
and send messages or media after explicit confirmation.

The plugin does not upload your WhatsApp database or bridge token to a plugin
service. Data is read from the local bridge and local SQLite indexes on the
machine where the plugin runs. Codex conversation handling is governed by the
privacy terms of the Codex/OpenAI environment you use it in.

## Sensitive Data

Do not commit or share the store directory, SQLite databases, bridge token,
downloaded private media, invite links, or exported message history. The
repository `.gitignore` excludes common runtime databases and build artifacts,
but you remain responsible for reviewing changes before publishing.

## Control And Removal

To stop background sync, unload the macOS service with:

```bash
bash scripts/bridge-service.sh uninstall
```

To reset the linked WhatsApp session, run:

```bash
bash scripts/reset-session.sh
```

Resetting removes local auth state and requires linking the device again.
