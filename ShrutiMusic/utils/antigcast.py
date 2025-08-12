import asyncio

from ShrutiMusic import app
from utils.antigcast import *
from utils.deleter import Deleter, VerifyAnkes
from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.database import db
from utils.query_group import ankes_group
from config import BANNED_USERS
from ShrutiMusic.misc import SUDOERS

from pyrogram import filters

async def blacklistword(chat_id, text):
    list_text = await db.get_var(chat_id, "delete_word") or []
    if text not in list_text:
        list_text.append(text)
        await db.set_var(chat_id, "delete_word", list_text)
    return text

async def removeword(chat_id, text):
    list_text = await db.get_var(chat_id, "delete_word") or []
    if text in list_text:
        list_text.remove(text)
        await db.set_var(chat_id, "delete_word", list_text)
        return text
    return None

async def ankestools(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply(">**Gunakan format `/protect [on/off]`**")
    jk = message.command[1]
    status = await db.get_var(chat_id, "PROTECT")
    if jk.lower() in ["On", "on"]:
        if status:
            return await message.reply(">**Protect sudah diaktifkan**")
        await db.set_var(chat_id, "PROTECT", jk)
        await Deleter.setup_antigcast(client, message)
        return await message.reply(f">**Berhasil mengatur protect menjadi {jk}.**\n\n**If admin messages are deleted by bots after enabling /antigcast on .\nJust type /reload to refresh admin list**")
    elif jk in ["Off", "off"]:
        if status is None:
            return await message.reply(">**Protect belum diaktifkan**")
        await db.remove_var(chat_id, "PROTECT")
        Deleter.SETUP_CHATS.remove(chat_id)
        return await message.reply(f">**Berhasil mengatur protect menjadi {jk}.**")
    else:
        return await message.reply(f">**{jk} Format salah, Gunakan `/protect [on/off]`.**")
    
async def clear_approved(_, message):
    chat_id = message.chat.id
    users = await db.get_list_from_var(chat_id, "APPROVED_USERS")
    for user in users:
        try:
            Deleter.WHITELIST_USER.remove(user)
        except Exception:
            pass
        await db.remove_from_var(chat_id, "APPROVED_USERS", user)
    return await message.reply(">**Berhasil menghapus semua pengguna approved.**")

async def clear_blackuser(_, message):
    chat_id = message.chat.id
    cekpre = await db.get_list_from_var(chat_id, "SILENT_USER")
    for pre in cekpre:
        try:
            Deleter.BLACKLIST_USER.remove(pre)
        except Exception:
            pass
        await db.remove_from_var(chat_id, "SILENT_USER", pre)
    return await message.reply(">**Berhasil menghapus list black pengguna.**")

@app.on_message(filters.command(["free", "approve", "addwhite"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def add_approve(client, message):
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
    freedom = await db.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids in freedom:
        return await message.reply_text(">**Pengguna sudah disetujui.**")
    await db.add_to_var(chat_id, "APPROVED_USERS", ids)
    Deleter.WHITELIST_USER[chat_id].append(ids)
    return await message.reply(f">**Pengguna: {user.mention} telah disetujui tidak akan terkena antigcast.")

async def un_approve(client, message):
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
    freedom = await db.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids not in freedom:
        return await message.reply_text(">**Pengguna memang belum disetujui.**")
    await db.remove_from_var(chat_id, "APPROVED_USERS", ids)
    Deleter.WHITELIST_USER[chat_id].remove(ids)
    return await message.reply(f">**Pengguna: {user.mention} telah dihapus dari daftar approved.**")

async def listapproved(_, message):
    chat_id = message.chat.id
    approved = await db.get_list_from_var(chat_id, "APPROVED_USERS")
    if len(approved) == 0:
        return await message.reply(">**Belum ada pengguna yang disetujui.**")
    msg = f"<blockquote expandable>**Pengguna Approved Di {message.chat.title}:**\n\n"
    for count, user in enumerate(approved, 1):
        msg += f"**•**{count} -> {user}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

async def listblack(_, message):
    chat_id = message.chat.id
    blacklist = await db.get_list_from_var(chat_id, "SILENT_USER")
    if len(blacklist) == 0:
        return await message.reply(">**Belum ada pengguna yang diblacklist.**")
    msg = f"<blockquote expandable>**Pengguna Blackist Di {message.chat.title}:**\n\n"
    for count, user in enumerate(blacklist, 1):
        msg += f"**•**{count} -> {user}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

async def _(client, message):
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
    dicekah = await db.get_list_from_var(chat_id, "SILENT_USER")
    if ids in dicekah:
        return await message.reply_text(">**Pengguna sudah diblacklist.**")
    await db.add_to_var(chat_id, "SILENT_USER", ids)
    Deleter.BLACKLIST_USER[chat_id].append(ids)
    msg = await message.reply(f">**Pengguna: {ids} ditambahkan ke blacklist.**")
    await asyncio.sleep(1)
    return await msg.delete()

async def _(client, message):
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
    dicekah = await db.get_list_from_var(chat_id, "SILENT_USER")
    if ids not in dicekah:
        return await message.reply_text("User not in blacklist.")
    await db.remove_from_var(chat_id, "SILENT_USER", ids)
    Deleter.BLACKLIST_USER[chat_id].remove(ids)
    msg = await message.reply(f">**Pengguna: {ids} dihapus ke blacklist.**")
    await asyncio.sleep(1)
    return await msg.delete()

async def addword_blacklist(_, message):
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

async def delword_blacklist(_, message):
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

async def listwordblacklist(_, message):
    chat_id = message.chat.id
    list_text = await db.get_var(chat_id, "delete_word")
    if list_text is None:
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

async def handle_deleter(client, message):
    if message.chat.id not in await db.get_list_from_var(client.me.id, "CHAT_ANTIGCAST"):
        return
    if message.sender_chat:
        return
    await Deleter.setup_antigcast(client, message)
    await Deleter.deleter(client, message)
