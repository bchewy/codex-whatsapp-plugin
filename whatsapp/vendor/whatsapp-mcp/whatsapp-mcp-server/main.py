from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
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
    """Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.
    
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
    """Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.
    
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
    confirm_add: bool = False
) -> Dict[str, Any]:
    """Add participants to a WhatsApp group.

    This is an externally visible group-admin action. Only use it after the user
    explicitly confirms the exact group JID and participant phone numbers/JIDs.

    Args:
        group_jid: The WhatsApp group JID, e.g. "123456789@g.us"
        participants: Phone numbers with country code and no + or symbols, or user JIDs
        confirm_add: Must be true only after explicit confirmation of the exact group and participants

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

    success, status_message, participant_results = whatsapp_add_group_participants(group_jid, participants)
    return {
        "success": success,
        "message": status_message,
        "participants": participant_results
    }

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
    confirm_invite_message: bool = False
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
        A dictionary containing success status, a status message, the new group JID, and participant-level results when available
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
