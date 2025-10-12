import asyncio
from pyrogram import filters
from pyrogram.types import Message

from ShrutiMusic import app

# Ketika bot join sebagai anggota baru, cek admin
@app.on_message(filters.group & filters.new_chat_members)
async def check_admin_status(client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await asyncio.sleep(2)
            chat_member = await client.get_chat_member(message.chat.id, member.id)
            if chat_member.status != "administrator":
                await client.send_message(
                    message.chat.id,
                    "<blockquote><b>Saya harus dijadikan admin! Bot keluar otomatis</b></blockquote>"
                )
                await client.leave_chat(message.chat.id)
            break

# Jika status bot berubah (dicabut admin), bot keluar otomatis
@app.on_chat_member_updated(filters.group)
async def monitor_admin_rights(client, member_update):
    if member_update.new_chat_member.user.id == (await client.get_me()).id:
        if member_update.new_chat_member.status not in ("administrator", "owner"):
            await client.send_message(
                member_update.chat.id,
                "<blockquote><b>Saya bukan admin, bot keluar otomatis</b></blockquote>"
            )
            await client.leave_chat(member_update.chat.id)
