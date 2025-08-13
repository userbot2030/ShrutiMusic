import asyncio

# Dictionary untuk menyimpan user whitelist dan blacklist per chat
WHITELIST_USER = {}  # {chat_id: [user_id, ...]}
BLACKLIST_USER = {}  # {chat_id: [user_id, ...]}
SETUP_CHATS = set()

async def setup_antigcast(client, message):
    chat_id = message.chat.id
    # Inisialisasi list jika belum ada
    WHITELIST_USER.setdefault(chat_id, [])
    BLACKLIST_USER.setdefault(chat_id, [])
    SETUP_CHATS.add(chat_id)
    # Bisa tambahkan logika refresh admin list, dsb jika perlu

async def deleter(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    # Jika user ada di blacklist, hapus pesan
    if chat_id in BLACKLIST_USER and user_id in BLACKLIST_USER[chat_id]:
        try:
            await message.delete()
        except Exception:
            pass
    # Jika user bukan admin/whitelist, bisa tambahkan logika hapus pesan yang dicurigai Gcast

# Dummy decorator untuk verifikasi (bisa disesuaikan sesuai kebutuhan)
def VerifyAnkes(func):
    async def wrapper(client, message, *args, **kwargs):
        # Bisa tambahkan logika: misal verifikasi apakah chat sudah setup antigcast
        return await func(client, message, *args, **kwargs)
    return wrapper

class Deleter:
    WHITELIST_USER = WHITELIST_USER
    BLACKLIST_USER = BLACKLIST_USER
    SETUP_CHATS = SETUP_CHATS
    setup_antigcast = staticmethod(setup_antigcast)
    deleter = staticmethod(deleter)
