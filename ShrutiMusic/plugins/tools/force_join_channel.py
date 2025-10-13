from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID  # Sudah otomatis ambil dari config.py

# Helper function untuk cek apakah user sudah join channel
async def is_joined(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Handler untuk /start (hanya private chat, dengan foto)
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined(client, user_id):
        join_link = "https://t.me/Disney_storeDan"  # Ganti dengan username channel kamu
        await message.reply(
            "<blockquote><b>Anda harus join channel terlebih dahulu untuk menggunakan bot!\n\nSilakan join dulu:</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=join_link)]
            ]),
            disable_web_page_preview=True
        )
        return
    # Jika sudah join channel, kirim foto + pesan
    foto_url = "https://files.catbox.moe/hgtn8x.jpg"  # Ganti dengan URL foto kamu
    await client.send_photo(
        chat_id=message.chat.id,
        photo=foto_url,
        caption="<blockquote><b>Selamat datang di bot! Anda sudah join channel.</b></blockquote>"
    )

# Handler untuk /play (private dan grup)
@Client.on_message(filters.command("play") & (filters.group))
async def play_handler(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined(client, user_id):
        join_link = "https://t.me/Disney_storeDan"  # Ganti dengan username channel kamu
        await message.reply(
            "<blockquote><b>Anda harus join channel terlebih dahulu untuk menggunakan fitur play!\n\nSilakan join dulu:</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=join_link)]
            ]),
            disable_web_page_preview=True
        )
        return
    await message.reply("<blockquote><b>Memulai pemutaran musik...</b></blockquote>")
