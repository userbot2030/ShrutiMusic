from pyrogram import filters
from functools import wraps

# Decorator: ONLY_ADMIN
def ONLY_ADMIN(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        # Pastikan hanya admin yang bisa memakai command
        user_id = message.from_user.id if message.from_user else None
        # Ambil data anggota grup
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if not (member.status in ["administrator", "creator"]):
                return await message.reply("Hanya admin yang boleh menggunakan perintah ini.")
        except Exception:
            return await message.reply("Tidak bisa memverifikasi admin.")
        return await func(client, message, *args, **kwargs)
    return wrapper
