from pyrogram.errors import UserNotParticipant

async def check_force_join(client, message, channel_username):
    try:
        user = await client.get_chat_member(channel_username, message.from_user.id)
        if user.status in ["member", "administrator", "creator"]:
            return True
    except UserNotParticipant:
        return False
    except Exception:
        return False
    return False
