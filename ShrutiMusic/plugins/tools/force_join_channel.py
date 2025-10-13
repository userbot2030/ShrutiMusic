from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_CHANNEL

def extract_channel_username(channel_url):
    if channel_url.endswith("/"):
        channel_url = channel_url[:-1]
    username = "@" + channel_url.split("/")[-1]
    return username

CHANNEL_USERNAME = extract_channel_username(SUPPORT_CHANNEL)

async def is_joined(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined(client, user_id):
        await message.reply(
            "<blockquote><b>Anda harus join channel terlebih dahulu untuk menggunakan bot!\n\nSilakan join dulu:</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=SUPPORT_CHANNEL)]
            ]),
            disable_web_page_preview=True
        )
        return
    foto_url = "https://files.catbox.moe/hgtn8x.jpg"
    await client.send_photo(
        chat_id=message.chat.id,
        photo=foto_url,
        caption="</b></blockquote>Selamat datang di bot! Anda sudah join channel.</b></blockquote>"
    )

@Client.on_message(filters.command("play") & (filters.private | filters.group))
async def play_handler(client, message: Message):
    user_id = message.from_user.id
    if not await is_joined(client, user_id):
        await message.reply(
            "<blockquote><b>Anda harus join channel terlebih dahulu untuk menggunakan fitur play!\n\nSilakan join dulu:</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=SUPPORT_CHANNEL)]
            ]),
            disable_web_page_preview=True
        )
        return
    await message.reply("<blockquote><b>Memulai pemutaran musik...</b></blockquote>")
