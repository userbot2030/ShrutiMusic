import asyncio

class Deleter:
    WHITELIST_USER = {}
    BLACKLIST_USER = {}
    SETUP_CHATS = set()

    @staticmethod
    async def setup_antigcast(client, message):
        print("Setup antigcast dijalankan")
        # kode setup kamu di sini
        pass

    @staticmethod
    async def deleter(client, message):
        print("Deleter dijalankan")
        # kode delete kamu di sini
        pass

def VerifyAnkes(func):
    async def wrapper(*args, **kwargs):
        print("Verifikasi dulu ya...")
        # logika verifikasi di sini (misal cek sesuatu)
        return await func(*args, **kwargs)
    return wrapper

@VerifyAnkes
async def tugas():
    print("Sedang menjalankan tugas")

# Cara menjalankan fungsi async
if __name__ == "__main__":
    asyncio.run(tugas())
