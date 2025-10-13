from pyrogram import filters
from pyrogram.types import Message
from ShrutiMusic import app

# Ganti ini dengan username channel kamu (tanpa @)
REQUIRED_CHANNEL = "Disney_storeDan"

async def is_joined_channel(user_id: int) -> bool:
    try:
        member = await app.get_chat_member(f"@{REQUIRED_CHANNEL}", user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

@app.on_message(filters.command("start"))
async def start_with_channel_check(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined_channel(user_id):
        return await message.reply(
            f"<blockquote><b>Untuk menggunakan bot ini, silakan join channel terlebih dahulu:\n\n</b></blockquote>"
            f"<blockquote><b>👉 <a href='https://t.me/{REQUIRED_CHANNEL}'>Join Channel</a></b></blockquote>",
            disable_web_page_preview=True
        )
    # lanjut fitur /start seperti biasa
    await message.reply("<blockquote><b>Selamat datang di bot!</b></blockquote>")

@app.on_message(filters.command("play"))
async def play_with_channel_check(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined_channel(user_id):
        return await message.reply(
            f"<blockquote><b>Untuk menggunakan fitur play, silakan join channel terlebih dahulu:\n\n</b></blockquote>"
            f"<blockquote><b>👉 <a href='https://t.me/{REQUIRED_CHANNEL}'>Join Channel</a></b></blockquote>",
            disable_web_page_preview=True
        )
    # lanjut fitur /play seperti biasa
    await message.reply("<blockquote><b>Silakan ketik lagu yang ingin diputar.</b></blockquote>")
