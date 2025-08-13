import asyncio

class Deleter:
    WHITELIST_USER = {}
    BLACKLIST_USER = {}
    SETUP_CHATS = set()

    @staticmethod
    async def setup_antigcast(client, message):
        print("Setup antigcast dijalankan")
        pass

    @staticmethod
    async def deleter(client, message):
        print("Deleter dijalankan")
        pass

def VerifyAnkes(func):
    async def wrapper(*args, **kwargs):
        print("Verifikasi dulu ya...")
        return await func(*args, **kwargs)
    return wrapper

@VerifyAnkes
async def tugas():
    print("Sedang menjalankan tugas")

if __name__ == "__main__":
    asyncio.run(tugas())
