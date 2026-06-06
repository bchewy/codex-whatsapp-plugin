import re
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_events as whatsapp_list_events,
    list_desktop_events as whatsapp_list_desktop_events,
    backfill_events as whatsapp_backfill_events,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    add_group_participants as whatsapp_add_group_participants,
    get_group_invite_link as whatsapp_get_group_invite_link,
    create_group as whatsapp_create_group,
    download_media as whatsapp_download_media
)

# Initialize FastMCP server
mcp = FastMCP("whatsapp")

RAW_PHONE_ADD_RISK_MESSAGE = (
    "Refusing direct group adds by raw phone number by default. WhatsApp has "
    "been observed to log out linked devices after participant-level 403 errors "
    "for this path. Use get_group_invite_link and share the invite manually, or "
    "set confirm_risky_phone_number_add=true after explicitly accepting that risk."
)

RAW_PHONE_ADD_SKIPPED_MESSAGE = (
    "Skipped direct group adds by raw phone number because WhatsApp has been "
    "observed to log out linked devices after participant-level 403 errors for "
    "this path. Use get_group_invite_link and share the invite manually, or set "
    "confirm_risky_phone_number_add=true after explicitly accepting that risk."
)

RAW_PHONE_INVITE_DM_RISK_MESSAGE = (
    "Direct add failed and the invite link was retrieved, but fallback DMs to "
    "raw phone numbers were not sent because that path can also force WhatsApp "
    "user-info lookups and has been observed to log out the linked device. Share "
    "the invite link manually, or set confirm_risky_phone_invite_dm=true after "
    "explicitly accepting that risk."
)

@mcp.tool()
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@mcp.tool()
def list_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        after: Optional ISO-8601 formatted string to only return messages after this date
        before: Optional ISO-8601 formatted string to only return messages before this date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    messages = whatsapp_list_messages(
        after=after,
        before=before,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    return messages

@mcp.tool()
def list_events(
    after: Optional[str] = None,
    before: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    include_canceled: bool = True,
    limit: int = 20,
    page: int = 0
) -> List[Dict[str, Any]]:
    """Get native WhatsApp events captured from chats.

    Args:
        after: Optional ISO-8601 formatted string to only return events after this date
        before: Optional ISO-8601 formatted string to only return events before this date
        chat_jid: Optional chat JID to filter events by chat
        query: Optional search term to filter event name, description, or location
        include_canceled: Whether to include canceled events (default True)
        limit: Maximum number of events to return (default 20)
        page: Page number for pagination (default 0)
    """
    events = whatsapp_list_events(
        after=after,
        before=before,
        chat_jid=chat_jid,
        query=query,
        include_canceled=include_canceled,
        limit=limit,
        page=page
    )
    return events

@mcp.tool()
def list_desktop_events(
    query: Optional[str] = None,
    limit: int = 100,
    page: int = 0,
    scroll_pages: int = 12
) -> str:
    """Read WhatsApp Desktop group event drawer rows via macOS accessibility.

    This is a fallback for events that appear in WhatsApp Desktop's Group Info
    event drawer but were not captured by the bridge event index. It requires
    WhatsApp Desktop to be running with the target group's event drawer open.

    Args:
        query: Optional search term to filter visible drawer rows
        limit: Maximum number of drawer rows to return
        page: Page number for pagination
        scroll_pages: Number of page-down passes to collect from the drawer
    """
    return whatsapp_list_desktop_events(
        query=query,
        limit=limit,
        page=page,
        scroll_pages=scroll_pages
    )

@mcp.tool()
def backfill_events(
    chat_jid: str,
    count: int = 50
) -> Dict[str, Any]:
    """Request on-demand history sync for a chat so older WhatsApp event cards can be indexed.

    This asks the linked primary device for messages before the oldest cached
    message in the chat. If WhatsApp returns EventMessage or EventInviteMessage
    payloads, the bridge stores them in the events table for list_events.

    Args:
        chat_jid: Chat JID to backfill, e.g. a group JID ending in @g.us
        count: Number of older messages to request before the oldest cached message
    """
    return whatsapp_backfill_events(chat_jid=chat_jid, count=count)

@mcp.tool()
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@mcp.tool()
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@mcp.tool()
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@mcp.tool()
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@mcp.tool()
def get_last_interaction(jid: str) -> str:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@mcp.tool()
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    return context

@mcp.tool()
def send_message(
    recipient: str,
    message: str,
    confirm_send: bool = False
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
        confirm_send: Must be true only after the user confirms the exact recipient and message
    
    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }

    if not confirm_send:
        return {
            "success": False,
            "message": "Refusing to send without confirm_send=true after explicit user confirmation"
        }
    
    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_file(recipient: str, media_path: str, confirm_send: bool = False) -> Dict[str, Any]:
    """Send a file such as a picture, raw audio, video or document via WhatsApp.

    For group messages use the JID.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the media file to send (image, video, document)
        confirm_send: Must be true only after the user confirms the exact recipient and file path
    
    Returns:
        A dictionary containing success status and a status message
    """
    if not confirm_send:
        return {
            "success": False,
            "message": "Refusing to send without confirm_send=true after explicit user confirmation"
        }

    # Call the whatsapp_send_file function
    success, status_message = whatsapp_send_file(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_audio_message(recipient: str, media_path: str, confirm_send: bool = False) -> Dict[str, Any]:
    """Send any audio file as a WhatsApp audio message to the specified recipient.

    For group messages use the JID. If conversion errors because ffmpeg is not
    installed, use send_file instead.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)
        confirm_send: Must be true only after the user confirms the exact recipient and audio file path
    
    Returns:
        A dictionary containing success status and a status message
    """
    if not confirm_send:
        return {
            "success": False,
            "message": "Refusing to send without confirm_send=true after explicit user confirmation"
        }

    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def add_group_participants(
    group_jid: str,
    participants: List[str],
    confirm_add: bool = False,
    confirm_risky_phone_number_add: bool = False
) -> Dict[str, Any]:
    """Add participants to a WhatsApp group.

    This is an externally visible group-admin action. Only use it after the user
    explicitly confirms the exact group JID and participant phone numbers/JIDs.

    Args:
        group_jid: The WhatsApp group JID, e.g. "123456789@g.us"
        participants: User JIDs, or phone numbers with country code and no + or symbols
        confirm_add: Must be true only after explicit confirmation of the exact group and participants
        confirm_risky_phone_number_add: Must be true only after explicitly accepting
            raw-phone direct-add logout risk from participant-level 403 errors

    Returns:
        A dictionary containing success status, a status message, and participant-level results when available
    """
    if not group_jid:
        return {
            "success": False,
            "message": "Group JID must be provided"
        }

    if not participants:
        return {
            "success": False,
            "message": "At least one participant must be provided"
        }

    if not confirm_add:
        return {
            "success": False,
            "message": "Refusing to add group participants without confirm_add=true after explicit user confirmation"
        }

    raw_phone_numbers = _raw_phone_number_participants(participants)
    if raw_phone_numbers and not confirm_risky_phone_number_add:
        return {
            "success": False,
            "message": RAW_PHONE_ADD_RISK_MESSAGE,
            "raw_phone_number_participants": raw_phone_numbers,
            "needs_risk_confirmation": True
        }

    success, status_message, participant_results = whatsapp_add_group_participants(group_jid, participants)
    return {
        "success": success,
        "message": status_message,
        "participants": participant_results
    }

def _is_raw_phone_number(ref: str) -> bool:
    if not ref or "@" in ref:
        return False
    cleaned = re.sub(r"[\s()+-]", "", ref.strip())
    return cleaned.isdigit()

def _raw_phone_number_participants(participants: List[str]) -> List[str]:
    return [participant for participant in participants if _is_raw_phone_number(participant)]

def _participant_recipient(participant: Dict[str, Any], fallback: str) -> str:
    return participant.get("phone_number") or participant.get("jid") or fallback

def _failed_participant_refs(
    requested_participants: List[str],
    participant_results: List[Dict[str, Any]]
) -> List[str]:
    if participant_results:
        failed = []
        for index, participant in enumerate(participant_results):
            if participant.get("error"):
                fallback = requested_participants[index] if index < len(requested_participants) else ""
                failed.append(_participant_recipient(participant, fallback))
        return failed
    return requested_participants

def _build_invite_message(template: Optional[str], invite_link: str) -> str:
    if template:
        if "{invite_link}" in template:
            return template.replace("{invite_link}", invite_link)
        return f"{template.rstrip()}\n\n{invite_link}"
    return f"I couldn't add you directly to the WhatsApp group, so here's the invite link: {invite_link}"

@mcp.tool()
def add_or_invite_group_participants(
    group_jid: str,
    participants: List[str],
    invite_message: Optional[str] = None,
    confirm_add: bool = False,
    confirm_invite_message: bool = False,
    confirm_risky_phone_number_add: bool = False,
    confirm_risky_phone_invite_dm: bool = False
) -> Dict[str, Any]:
    """Add participants to a WhatsApp group, then DM an invite link to failed adds.

    Direct group adds and fallback DMs are externally visible actions. Only set
    confirm_add=true after the user confirms the exact group and participant
    list. Only set confirm_invite_message=true after the user confirms fallback
    DMs should be sent if any direct adds fail.

    Args:
        group_jid: The WhatsApp group JID, e.g. "123456789@g.us"
        participants: Phone numbers with country code and no + or symbols, or user JIDs
        invite_message: Optional DM text. Use {invite_link} to control where the link appears.
        confirm_add: Must be true only after explicit confirmation of the exact group and participants
        confirm_invite_message: Must be true only after explicit confirmation to send fallback invite DMs
        confirm_risky_phone_number_add: Must be true only after explicitly accepting raw-phone direct-add logout risk
        confirm_risky_phone_invite_dm: Must be true only after explicitly accepting raw-phone invite-DM logout risk

    Returns:
        A dictionary containing direct-add status and invite fallback status
    """
    if not group_jid:
        return {
            "success": False,
            "message": "Group JID must be provided"
        }

    if not participants:
        return {
            "success": False,
            "message": "At least one participant must be provided"
        }

    if not confirm_add:
        return {
            "success": False,
            "message": "Refusing to add group participants without confirm_add=true after explicit user confirmation"
        }

    raw_phone_numbers = _raw_phone_number_participants(participants)
    if raw_phone_numbers and not confirm_risky_phone_number_add:
        return {
            "success": False,
            "message": RAW_PHONE_ADD_SKIPPED_MESSAGE,
            "add_success": False,
            "participants": [],
            "failed_recipients": raw_phone_numbers,
            "needs_risk_confirmation": True,
            "needs_manual_invite": True,
            "needs_invite_link": True
        }

    add_success, add_message, participant_results = whatsapp_add_group_participants(group_jid, participants)
    if add_success:
        return {
            "success": True,
            "message": add_message,
            "add_success": True,
            "participants": participant_results,
            "invites_sent": []
        }

    failed_recipients = _failed_participant_refs(participants, participant_results)
    if not confirm_invite_message:
        return {
            "success": False,
            "message": f"{add_message}; fallback invite DMs were not sent because confirm_invite_message is false",
            "add_success": False,
            "participants": participant_results,
            "failed_recipients": failed_recipients,
            "needs_invite_confirmation": True
        }

    invite_success, invite_status, invite_link = whatsapp_get_group_invite_link(group_jid)
    if not invite_success or not invite_link:
        return {
            "success": False,
            "message": f"{add_message}; failed to get group invite link: {invite_status}",
            "add_success": False,
            "participants": participant_results,
            "failed_recipients": failed_recipients,
            "invites_sent": []
        }

    raw_failed_recipients = _raw_phone_number_participants(failed_recipients)
    if raw_failed_recipients and not confirm_risky_phone_invite_dm:
        return {
            "success": False,
            "message": RAW_PHONE_INVITE_DM_RISK_MESSAGE,
            "add_success": False,
            "participants": participant_results,
            "failed_recipients": failed_recipients,
            "invite_link": invite_link,
            "invites_sent": [],
            "needs_risk_confirmation": True,
            "needs_manual_invite": True
        }

    message = _build_invite_message(invite_message, invite_link)
    invites_sent = []
    invite_failures = []
    for recipient in failed_recipients:
        send_success, send_status = whatsapp_send_message(recipient, message)
        item = {
            "recipient": recipient,
            "success": send_success,
            "message": send_status
        }
        invites_sent.append(item)
        if not send_success:
            invite_failures.append(item)

    return {
        "success": len(invite_failures) == 0,
        "message": "Direct add failed; fallback invite messages processed",
        "add_success": False,
        "participants": participant_results,
        "failed_recipients": failed_recipients,
        "invite_link": invite_link,
        "invites_sent": invites_sent
    }

@mcp.tool()
def get_group_invite_link(
    group_jid: str,
    reset: bool = False,
    confirm_get: bool = False,
    confirm_reset: bool = False
) -> Dict[str, Any]:
    """Get a WhatsApp group invite link.

    Invite links are sensitive because anyone with the link may be able to join.
    Only set confirm_get=true after confirming the exact group. Only set
    reset=true with confirm_reset=true after the user explicitly confirms link
    rotation, because resetting invalidates the previous invite link.

    Args:
        group_jid: The WhatsApp group JID, e.g. "123456789@g.us"
        reset: Whether to rotate the group's invite link
        confirm_get: Must be true only after explicit confirmation of the exact group
        confirm_reset: Must be true only after explicit confirmation to rotate the link

    Returns:
        A dictionary containing success status, a status message, and the invite link
    """
    if not group_jid:
        return {
            "success": False,
            "message": "Group JID must be provided"
        }

    if not confirm_get:
        return {
            "success": False,
            "message": "Refusing to get group invite link without confirm_get=true after explicit user confirmation"
        }

    if reset and not confirm_reset:
        return {
            "success": False,
            "message": "Refusing to reset group invite link without confirm_reset=true after explicit user confirmation"
        }

    success, status_message, invite_link = whatsapp_get_group_invite_link(group_jid, reset=reset)
    return {
        "success": success,
        "message": status_message,
        "invite_link": invite_link
    }

@mcp.tool()
def create_group(
    name: str,
    participants: List[str],
    confirm_create: bool = False
) -> Dict[str, Any]:
    """Create a WhatsApp group with the given participants.

    This is an externally visible action. Only use it after the user explicitly
    confirms the exact group name and participant phone numbers/JIDs.

    Args:
        name: WhatsApp group name. WhatsApp currently limits names to 25 characters.
        participants: Phone numbers with country code and no + or symbols, or user JIDs
        confirm_create: Must be true only after explicit confirmation of the exact group and participants

    Returns:
        A dictionary containing success status, status message, new group JID,
        and participant-level results when available
    """
    if not name:
        return {
            "success": False,
            "message": "Group name must be provided"
        }

    if not participants:
        return {
            "success": False,
            "message": "At least one participant must be provided"
        }

    if not confirm_create:
        return {
            "success": False,
            "message": "Refusing to create group without confirm_create=true after explicit user confirmation"
        }

    success, status_message, group_jid, participant_results = whatsapp_create_group(name, participants)
    return {
        "success": success,
        "message": status_message,
        "group_jid": group_jid,
        "participants": participant_results
    }

@mcp.tool()
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    """Download media from a WhatsApp message and get the local file path.
    
    Args:
        message_id: The ID of the message containing the media
        chat_jid: The JID of the chat containing the message
    
    Returns:
        A dictionary containing success status, a status message, and the file path if successful
    """
    file_path = whatsapp_download_media(message_id, chat_jid)
    
    if file_path:
        return {
            "success": True,
            "message": "Media downloaded successfully",
            "file_path": file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to download media"
        }

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
