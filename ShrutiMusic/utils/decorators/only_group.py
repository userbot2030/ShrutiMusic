from pyrogram import filters
from functools import wraps

# Decorator: ONLY_GROUP
def ONLY_GROUP(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        # Pastikan command hanya bisa dipakai di grup
        if not message.chat.type in ["group", "supergroup"]:
            return await message.reply("Command ini hanya bisa dipakai di grup.")
        return await func(client, message, *args, **kwargs)
    return wrapper
