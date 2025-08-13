import asyncio
from pyrogram import filters, errors
from pyrogram.types import Message
from ShrutiMusic import app, LOGGER
from ShrutiMusic.utils import pastebin
from ShrutiMusic.utils.deleter import Deleter, VerifyAnkes
from ShrutiMusic.utils.decorators import ONLY_GROUP, ONLY_ADMIN
from ShrutiMusic.utils.database import dB
from ShrutiMusic.utils.query_group import ankes_group
from config import BANNED_USERS
from ShrutiMusic.misc import SUDOERS

async def blacklistword(chat_id, text):
    list_text = await dB.get_var(chat_id, "delete_word") or []
    if text not in list_text:
        list_text.append(text)
        await dB.set_var(chat_id, "delete_word", list_text)
    return text

async def removeword(chat_id, text):
    list_text = await dB.get_var(chat_id, "delete_word") or []
    if text in list_text:
        list_text.remove(text)
        await dB.set_var(chat_id, "delete_word", list_text)
        return text
    return None

def ensure_chat_dict(d, chat_id):
    if chat_id not in d:
        d[chat_id] = []
    return d[chat_id]

@app.on_message(filters.command(["protect", "antigcast"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
@VerifyAnkes
async def ankestools(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply(">**Gunakan format `/protect [on/off]`**")
    jk = message.command[1]
    status = await dB.get_var(chat_id, "PROTECT")
    if jk.lower() == "on":
        if status:
            return await message.reply(">**Protect sudah diaktifkan**")
        await dB.set_var(chat_id, "PROTECT", jk)
        await Deleter.setup_antigcast(client, message)
        return await message.reply(
            f">**Berhasil mengatur protect menjadi {jk}.**\n\n"
            "**Jika pesan admin terhapus oleh bot setelah mengaktifkan /antigcast on, gunakan /reload untuk refresh daftar admin.**"
        )
    elif jk.lower() == "off":
        if status is None:
            return await message.reply(">**Protect belum diaktifkan**")
        await dB.remove_var(chat_id, "PROTECT")
        if hasattr(Deleter, "SETUP_CHATS") and chat_id in Deleter.SETUP_CHATS:
            Deleter.SETUP_CHATS.remove(chat_id)
        return await message.reply(f">**Berhasil mengatur protect menjadi {jk}.**")
    else:
        return await message.reply(f">**{jk} Format salah, gunakan `/protect [on/off]`.**")

@app.on_message(filters.command(["clearwhite","clearfree", "clearapproved"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def clear_approved(_, message: Message):
    chat_id = message.chat.id
    users = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    for user in users:
        try:
            ensure_chat_dict(Deleter.WHITELIST_USER, chat_id).remove(user)
        except Exception:
            pass
        await dB.remove_from_var(chat_id, "APPROVED_USERS", user)
    return await message.reply(">**Berhasil menghapus semua pengguna approved.**")

@app.on_message(filters.command(["clearblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def clear_blackuser(_, message: Message):
    chat_id = message.chat.id
    users = await dB.get_list_from_var(chat_id, "SILENT_USER")
    for user in users:
        try:
            ensure_chat_dict(Deleter.BLACKLIST_USER, chat_id).remove(user)
        except Exception:
            pass
        await dB.remove_from_var(chat_id, "SILENT_USER", user)
    return await message.reply(">**Berhasil menghapus list black pengguna.**")

@app.on_message(filters.command(["free", "approve", "addwhite"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def add_approve(client, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply and reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    if ids in SUDOERS:
        return await message.reply(">**Pengguna adalah SUDOERS bot!!**")
    freedom = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids in freedom:
        return await message.reply_text(">**Pengguna sudah disetujui.**")
    await dB.add_to_var(chat_id, "APPROVED_USERS", ids)
    ensure_chat_dict(Deleter.WHITELIST_USER, chat_id).append(ids)
    return await message.reply(f">**Pengguna: {user.mention} telah disetujui tidak akan terkena antigcast.**")

@app.on_message(filters.command(["unfree", "unapprove", "delwhite"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def un_approve(client, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply and reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(
            ">**Balas pesan pengguna atau berikan username pengguna.**"
        )
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    freedom = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids not in freedom:
        return await message.reply_text(">**Pengguna memang belum disetujui.**")
    await dB.remove_from_var(chat_id, "APPROVED_USERS", ids)
    ensure_chat_dict(Deleter.WHITELIST_USER, chat_id).remove(ids)
    return await message.reply(f">**Pengguna: {user.mention} telah dihapus dari daftar approved.**")

@app.on_message(filters.command(["listwhite", "approved"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def listapproved(_, message: Message):
    chat_id = message.chat.id
    approved = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if not approved:
        return await message.reply(">**Belum ada pengguna yang disetujui.**")
    msg = f"<blockquote expandable>**Pengguna Approved Di {message.chat.title}:**\n\n"
    for count, user in enumerate(approved, 1):
        msg += f"**•** {count} -> {user}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

@app.on_message(filters.command(["listblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def listblack(_, message: Message):
    chat_id = message.chat.id
    blacklist = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if not blacklist:
        return await message.reply(">**Belum ada pengguna yang diblacklist.**")
    msg = f"<blockquote expandable>**Pengguna Blacklist Di {message.chat.title}:**\n\n"
    for count, user in enumerate(blacklist, 1):
        msg += f"**•** {count} -> {user}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

@app.on_message(filters.command(["addblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def add_black(client, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply and reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    if ids in SUDOERS:
        return await message.reply(">**Pengguna adalah SUDOERS bot!!**")
    dicekah = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if ids in dicekah:
        return await message.reply_text(">**Pengguna sudah diblacklist.**")
    await dB.add_to_var(chat_id, "SILENT_USER", ids)
    ensure_chat_dict(Deleter.BLACKLIST_USER, chat_id).append(ids)
    msg = await message.reply(f">**Pengguna: {ids} ditambahkan ke blacklist.**")
    await asyncio.sleep(1)
    return await msg.delete()

@app.on_message(filters.command(["delblack", "unblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def del_black(client, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply and reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    dicekah = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if ids not in dicekah:
        return await message.reply_text(">**User tidak ada di blacklist.**")
    await dB.remove_from_var(chat_id, "SILENT_USER", ids)
    ensure_chat_dict(Deleter.BLACKLIST_USER, chat_id).remove(ids)
    msg = await message.reply(f">**Pengguna: {ids} dihapus dari blacklist.**")
    await asyncio.sleep(1)
    return await msg.delete()

@app.on_message(filters.command(["bl"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def addword_blacklist(_, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply:
        text = reply.text or reply.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply(">**Balas ke pesan atau berikan pesan untuk diblacklist.**")
    if text is None:
        return await message.reply(">**Pesan tidak memiliki teks untuk diblacklist.**")
    black = await blacklistword(chat_id, text)
    msg = await message.reply(f">**Kata dimasukkan ke blacklist:**\n{black}")
    await asyncio.sleep(1)
    return await msg.delete()

@app.on_message(filters.command(["unbl"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def delword_blacklist(_, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply:
        text = reply.text or reply.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply(">**Balas ke pesan atau berikan pesan untuk dihapus dari blacklist.**")
    if text is None:
        return await message.reply(">**Pesan tidak memiliki teks untuk dihapus dari blacklist.**")
    black = await removeword(chat_id, text)
    if black is not None:
        return await message.reply(f">**Kata dihapus dari blacklist:**\n{black}")
    else:
        return await message.reply(">**Kata tidak ditemukan di blacklist.**")

@app.on_message(filters.command(["listbl"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def listwordblacklist(_, message: Message):
    chat_id = message.chat.id
    list_text = await dB.get_var(chat_id, "delete_word")
    if not list_text:
        return await message.reply(">**Belum ada pesan yg diblacklist.**")
    msg = f"<blockquote expandable>**Daftar Blacklist Di {message.chat.title}:**\n"
    for num, text in enumerate(list_text, 1):
        msg += f"{num}. {text}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

@app.on_message(filters.incoming & filters.group & ~filters.bot & ~filters.via_bot, group=ankes_group)
async def handle_deleter(client, message: Message):
    if message.chat.id not in await dB.get_list_from_var(client.me.id, "CHAT_ANTIGCAST"):
        return
    if message.sender_chat:
        return
    await Deleter.setup_antigcast(client, message)
    await Deleter.deleter(client, message)

__MODULE__ = "Anti-Gcast"
__HELP__ = """
🚫 <b>Global Anti-Spam Protection</b>
• <b>/protect</b> or <b>/antigcast</b> [on/off] – Enable or disable Gcast protection.

👤 <b>User Blacklist</b>  
• <b>/addblack</b> – Reply to a user or provide username to blacklist.  
• <b>/delblack</b> – Remove a user from blacklist.  
• <b>/listblack</b> – Show all blacklisted users.  
• <b>/clearblack</b> – Clear all blacklisted users.

✅ <b>User Whitelist</b>  
• <b>/free</b> – Add a user to whitelist.  
• <b>/unfree</b> – Remove a user from whitelist.  
• <b>/listwhite</b> – Show all whitelisted users.  
• <b>/clearwhite</b> – Clear all whitelisted users.

📌 <b>Text Blacklist</b>  
• <b>/bl</b> – Add keyword/phrase to blacklist.  
• <b>/unbl</b> – Remove blacklisted text.  
• <b>/listbl</b> – Show all blacklisted texts.

<i>Note: If admin list is outdated (e.g. bot deletes admin messages), use <b>/reload</b> to refresh.</i>
"""
