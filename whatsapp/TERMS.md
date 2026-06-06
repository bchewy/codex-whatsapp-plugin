# Terms of Service

This plugin is provided as a local, unofficial wrapper around
`lharries/whatsapp-mcp` for personal use with Codex. It is not affiliated with,
endorsed by, or operated by WhatsApp or Meta.

## User Responsibility

You are responsible for using the plugin in a way that complies with WhatsApp's
terms, local law, workplace policy, and the expectations of the people whose
messages you access or contact.

## Externally Visible Actions

Sending messages, sending media, creating groups, adding participants, sending
fallback invite messages, and rotating or retrieving invite links are externally
visible actions. The MCP tools require explicit confirmation flags for these
actions, and agents should verify exact recipients, groups, content, and media
paths before setting those flags.

## Unofficial Bridge Limitations

The plugin depends on a local linked-device bridge and WhatsApp behavior that
can change. Sync may be stale, event history may be incomplete, unread state is
not guaranteed, and some raw-phone group operations may disrupt the linked
session. Treat plugin output as local assistant context, not an authoritative
WhatsApp export.

## No Warranty

The plugin is provided as-is, without warranties or guarantees of availability,
accuracy, delivery, account safety, or fitness for a particular purpose.
