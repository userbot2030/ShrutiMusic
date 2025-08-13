class Deleter:
    WHITELIST_USER = {}
    BLACKLIST_USER = {}
    SETUP_CHATS = set()

    @staticmethod
    async def setup_antigcast(client, message):
        # Your setup code here
        pass

    @staticmethod
    async def deleter(client, message):
        # Your delete logic here
        pass

import asyncio

def VerifyAnkes(func):
    async def wrapper(*args, **kwargs):
        # logika verifikasi
        return await func(*args, **kwargs)
    return wrapper

@VerifyAnkes
async def tugas():
    print("Sedang menjalankan tugas")

# Memanggil fungsi async
asyncio.run(tugas())
