import asyncio
import logging

from typing import List

from pyrogram import filters, errors, enums
from pyrogram.types import Message

from ShrutiMusic import app
import config
from ShrutiMusic.misc import SUDOERS
from ShrutiMusic.core.mongo import mongodb
from ShrutiMusic.utils.decorators import AdminActual

LOGGER = logging.getLogger(__name__)

COL = mongodb.antigcst
CFG = mongodb.antigcst_config

OWNER_ID = getattr(config, "OWNER_ID", 5779185981)

def _chat_doc_key(chat_id: int):
    return {"chat_id": chat_id}

async def _get_doc(chat_id: int) -> dict:
    doc = await COL.find_one(_chat_doc_key(chat_id))
    if not doc:
        doc = {
            "chat_id": chat_id,
            "protect": False,
            "delete_all": False,
            "approved_users": [],
            "silent_users": [],
            "delete_words": [],
        }
        await COL.insert_one(doc)
    return doc

async def _set_protect(chat_id: int, value: bool):
    await COL.update_one(_chat_doc_key(chat_id), {"$set": {"protect": value}}, upsert=True)

async def _set_delete_all(chat_id: int, value: bool):
    await COL.update_one(_chat_doc_key(chat_id), {"$set": {"delete_all": value}}, upsert=True)

async def _add_to_list(chat_id: int, field: str, value):
    await COL.update_one(_chat_doc_key(chat_id), {"$addToSet": {field: value}}, upsert=True)

async def _remove_from_list(chat_id: int, field: str, value):
    await COL.update_one(_chat_doc_key(chat_id), {"$pull": {field: value}}, upsert=True)

async def _get_list(chat_id: int, field: str) -> List:
    doc = await COL.find_one(_chat_doc_key(chat_id))
    if not doc:
        return []
    return doc.get(field, [])

async def _notify_chat_toggle(chat_id: int, text: str):
    try:
        await app.send_message(chat_id, text)
    except Exception:
        LOGGER.warning("Failed to send antigcst toggle notification to %s", chat_id)

# ================ All requests need OWNER approval ================

def need_owner(message, action, target=None, extra=None):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_mention = message.from_user.mention
    if user_id != OWNER_ID:
        req_msg = f"Permintaan dari {user_mention} untuk {action} di chat {message.chat.title} ({chat_id})"
        if target: req_msg += f" terhadap target: {target}"
        if extra: req_msg += f"\n{extra}"
        req_msg += f"\nOWNER: balas dengan /approve{action} {chat_id}"
        if target: req_msg += f" {target}"
        if extra: req_msg += f" {extra}"
        return req_msg
    return None

@app.on_message(filters.command(["protect", "antigcast"]) & filters.group)
@AdminActual
async def antigcst_toggle(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(">Gunakan format: /protect [on|off]")
    mode = message.command[1].lower()
    req_msg = need_owner(message, "protect", mode)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    bool_val = mode in ("on", "true", "1")
    await _set_protect(message.chat.id, bool_val)
    await _notify_chat_toggle(message.chat.id, f"🔒 Protect diubah OWNER.")
    return await message.reply_text(f">Protect diubah OWNER ke {mode.upper()}.")

@app.on_message(filters.command(["approveprotect"]) & filters.user(OWNER_ID))
async def approveprotect_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveprotect <chat_id> <on|off>")
    chat_id = int(message.command[1])
    mode = message.command[2].lower()
    bool_val = mode in ("on", "true", "1")
    await _set_protect(chat_id, bool_val)
    await _notify_chat_toggle(chat_id, f"🔒 Protect diubah OWNER via konfirmasi.")
    await client.send_message(chat_id, f"Protect telah diubah menjadi {'AKTIF' if bool_val else 'NONAKTIF'} oleh OWNER.")
    return await message.reply_text(f"Berhasil mengubah protect di chat {chat_id} ke {mode.upper()}.")

@app.on_message(filters.command(["protectmode", "antigcstmode"]) & filters.group)
@AdminActual
async def antigcst_mode(client, message: Message, _):
    if len(message.command) < 3:
        return await message.reply_text(">Gunakan: /protectmode all on|off")
    sub = message.command[1].lower()
    val = message.command[2].lower()
    req_msg = need_owner(message, "protectmode", val)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    bool_val = val in ("on", "true", "1")
    await _set_delete_all(message.chat.id, bool_val)
    await _notify_chat_toggle(message.chat.id, f"⛔️ delete_all (STRICT) mode diubah OWNER.")
    return await message.reply_text(f">delete_all (strict) diubah OWNER ke {val.upper()}.")

@app.on_message(filters.command(["approveprotectmode"]) & filters.user(OWNER_ID))
async def approveprotectmode_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveprotectmode <chat_id> <on|off>")
    chat_id = int(message.command[1])
    val = message.command[2].lower()
    bool_val = val in ("on", "true", "1")
    await _set_delete_all(chat_id, bool_val)
    await _notify_chat_toggle(chat_id, f"⛔️ delete_all (STRICT) mode diubah OWNER via konfirmasi.")
    await client.send_message(chat_id, f"delete_all (strict) mode telah diubah menjadi {'AKTIF' if bool_val else 'NONAKTIF'} oleh OWNER.")
    return await message.reply_text(f"Berhasil mengubah delete_all untuk chat {chat_id} ke {val.upper()}.")

# Whitelist
@app.on_message(filters.command(["free", "approve", "addwhite"]) & filters.group)
@AdminActual
async def add_approve(client, message: Message, _):
    reply = message.reply_to_message
    if reply:
        target = reply.from_user.id
    elif len(message.command) > 1:
        target = int(message.command[1])
    else:
        return await message.reply_text(">Balas pesan pengguna atau berikan id/username.")
    req_msg = need_owner(message, "white", target)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _add_to_list(message.chat.id, "approved_users", target)
    return await message.reply_text(f">Pengguna {target} telah ditambahkan ke whitelist oleh OWNER.")

@app.on_message(filters.command(["approvewhite"]) & filters.user(OWNER_ID))
async def approve_white_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approvewhite <chat_id> <user_id>")
    chat_id = int(message.command[1])
    uid = int(message.command[2])
    await _add_to_list(chat_id, "approved_users", uid)
    await client.send_message(chat_id, f"Whitelist: {uid} disetujui OWNER.")
    return await message.reply_text(f"Whitelist untuk {uid} berhasil ditambahkan di chat {chat_id}.")

@app.on_message(filters.command(["unfree", "unapprove", "delwhite"]) & filters.group)
@AdminActual
async def un_approve(client, message: Message, _):
    reply = message.reply_to_message
    if reply:
        target = reply.from_user.id
    elif len(message.command) > 1:
        target = int(message.command[1])
    else:
        return await message.reply_text(">Balas pesan pengguna atau berikan id/username.")
    req_msg = need_owner(message, "unwhite", target)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _remove_from_list(message.chat.id, "approved_users", target)
    return await message.reply_text(f">Pengguna {target} telah dihapus dari whitelist oleh OWNER.")

@app.on_message(filters.command(["approveunwhite"]) & filters.user(OWNER_ID))
async def approve_unwhite_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveunwhite <chat_id> <user_id>")
    chat_id = int(message.command[1])
    uid = int(message.command[2])
    await _remove_from_list(chat_id, "approved_users", uid)
    await client.send_message(chat_id, f"Whitelist: {uid} dihapus OWNER.")
    return await message.reply_text(f"Whitelist untuk {uid} berhasil dihapus di chat {chat_id}.")

@app.on_message(filters.command(["clearwhite", "clearfree", "clearapproved"]) & filters.group)
@AdminActual
async def clear_approved(client, message: Message, _):
    req_msg = need_owner(message, "clearwhite")
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await COL.update_one(_chat_doc_key(message.chat.id), {"$set": {"approved_users": []}}, upsert=True)
    return await message.reply_text(">Berhasil menghapus semua pengguna approved (whitelist) oleh OWNER.")

@app.on_message(filters.command(["approveclearwhite"]) & filters.user(OWNER_ID))
async def approve_clear_white_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Format: /approveclearwhite <chat_id>")
    chat_id = int(message.command[1])
    await COL.update_one(_chat_doc_key(chat_id), {"$set": {"approved_users": []}}, upsert=True)
    await client.send_message(chat_id, f"Whitelist dihapus OWNER.")
    return await message.reply_text(f"Whitelist berhasil dihapus di chat {chat_id}.")

# Blacklist
@app.on_message(filters.command(["addblack"]) & filters.group)
@AdminActual
async def add_black(client, message: Message, _):
    reply = message.reply_to_message
    if reply:
        target = reply.from_user.id
    elif len(message.command) > 1:
        target = int(message.command[1])
    else:
        return await message.reply_text(">Balas pesan pengguna atau berikan id/username.")
    req_msg = need_owner(message, "black", target)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _add_to_list(message.chat.id, "silent_users", target)
    return await message.reply_text(f">Pengguna {target} telah ditambahkan ke blacklist oleh OWNER.")

@app.on_message(filters.command(["approveblack"]) & filters.user(OWNER_ID))
async def approve_black_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveblack <chat_id> <user_id>")
    chat_id = int(message.command[1])
    uid = int(message.command[2])
    await _add_to_list(chat_id, "silent_users", uid)
    await client.send_message(chat_id, f"Blacklist: {uid} ditambahkan OWNER.")
    return await message.reply_text(f"Blacklist untuk {uid} berhasil ditambahkan di chat {chat_id}.")

@app.on_message(filters.command(["delblack", "unblack"]) & filters.group)
@AdminActual
async def del_black(client, message: Message, _):
    reply = message.reply_to_message
    if reply:
        target = reply.from_user.id
    elif len(message.command) > 1:
        target = int(message.command[1])
    else:
        return await message.reply_text(">Balas pesan pengguna atau berikan id/username.")
    req_msg = need_owner(message, "unblack", target)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _remove_from_list(message.chat.id, "silent_users", target)
    return await message.reply_text(f">Pengguna {target} telah dihapus dari blacklist oleh OWNER.")

@app.on_message(filters.command(["approveunblack"]) & filters.user(OWNER_ID))
async def approve_unblack_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveunblack <chat_id> <user_id>")
    chat_id = int(message.command[1])
    uid = int(message.command[2])
    await _remove_from_list(chat_id, "silent_users", uid)
    await client.send_message(chat_id, f"Blacklist: {uid} dihapus OWNER.")
    return await message.reply_text(f"Blacklist untuk {uid} berhasil dihapus di chat {chat_id}.")

@app.on_message(filters.command(["clearblack"]) & filters.group)
@AdminActual
async def clear_black(client, message: Message, _):
    req_msg = need_owner(message, "clearblack")
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await COL.update_one(_chat_doc_key(message.chat.id), {"$set": {"silent_users": []}}, upsert=True)
    return await message.reply_text(">Berhasil menghapus semua pengguna blacklist oleh OWNER.")

@app.on_message(filters.command(["approveclearblack"]) & filters.user(OWNER_ID))
async def approve_clear_black_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Format: /approveclearblack <chat_id>")
    chat_id = int(message.command[1])
    await COL.update_one(_chat_doc_key(chat_id), {"$set": {"silent_users": []}}, upsert=True)
    await client.send_message(chat_id, f"Blacklist dihapus OWNER.")
    return await message.reply_text(f"Blacklist berhasil dihapus di chat {chat_id}.")

# Text blacklist
@app.on_message(filters.command(["bl"]) & filters.group)
@AdminActual
async def add_word_blacklist(client, message: Message, _):
    reply = message.reply_to_message
    text = None
    if reply:
        text = reply.text or reply.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(">Balas ke pesan atau berikan pesan untuk diblacklist.")
    if not text:
        return await message.reply_text(">Pesan tidak memiliki teks untuk diblacklist.")
    req_msg = need_owner(message, "bl", text)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _add_to_list(message.chat.id, "delete_words", text)
    return await message.reply_text(f">Kata \"{text}\" telah ditambahkan ke blacklist oleh OWNER.")

@app.on_message(filters.command(["approvebl"]) & filters.user(OWNER_ID))
async def approve_bl_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approvebl <chat_id> <text>")
    chat_id = int(message.command[1])
    text = message.text.split(None, 2)[2]
    await _add_to_list(chat_id, "delete_words", text)
    await client.send_message(chat_id, f"Kata blacklist \"{text}\" disetujui OWNER.")
    return await message.reply_text(f"Blacklist kata \"{text}\" berhasil ditambahkan di chat {chat_id}.")

@app.on_message(filters.command(["unbl"]) & filters.group)
@AdminActual
async def del_word_blacklist(client, message: Message, _):
    reply = message.reply_to_message
    text = None
    if reply:
        text = reply.text or reply.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(">Balas ke pesan atau berikan pesan untuk dihapus dari blacklist.")
    if not text:
        return await message.reply_text(">Pesan tidak memiliki teks untuk dihapus dari blacklist.")
    req_msg = need_owner(message, "unbl", text)
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await _remove_from_list(message.chat.id, "delete_words", text)
    return await message.reply_text(f">Kata \"{text}\" telah dihapus dari blacklist oleh OWNER.")

@app.on_message(filters.command(["approveunbl"]) & filters.user(OWNER_ID))
async def approve_unbl_handler(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Format: /approveunbl <chat_id> <text>")
    chat_id = int(message.command[1])
    text = message.text.split(None, 2)[2]
    await _remove_from_list(chat_id, "delete_words", text)
    await client.send_message(chat_id, f"Kata blacklist \"{text}\" dihapus OWNER.")
    return await message.reply_text(f"Blacklist kata \"{text}\" berhasil dihapus di chat {chat_id}.")

@app.on_message(filters.command(["clearbl"]) & filters.group)
@AdminActual
async def clear_bl(client, message: Message, _):
    req_msg = need_owner(message, "clearbl")
    if req_msg:
        await client.send_message(OWNER_ID, req_msg)
        return await message.reply_text(">Permintaan anda dikirim ke OWNER. Tunggu persetujuan.")
    await COL.update_one(_chat_doc_key(message.chat.id), {"$set": {"delete_words": []}}, upsert=True)
    return await message.reply_text(">Berhasil menghapus semua text blacklist oleh OWNER.")

@app.on_message(filters.command(["approveclearbl"]) & filters.user(OWNER_ID))
async def approve_clear_bl_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Format: /approveclearbl <chat_id>")
    chat_id = int(message.command[1])
    await COL.update_one(_chat_doc_key(chat_id), {"$set": {"delete_words": []}}, upsert=True)
    await client.send_message(chat_id, f"Text blacklist dihapus OWNER.")
    return await message.reply_text(f"Text blacklist berhasil dihapus di chat {chat_id}.")

# Command list tetap bisa dijalankan siapa saja
@app.on_message(filters.command(["listwhite", "approved"]) & filters.group)
@AdminActual
async def list_approved(_, message: Message, __):
    approved = await _get_list(message.chat.id, "approved_users")
    if not approved:
        return await message.reply_text(">Belum ada pengguna yang disetujui.")
    msg = "<b>Pengguna Approved:</b>\n\n"
    for i, uid in enumerate(approved, 1):
        msg += f"{i}. <code>{uid}</code>\n"
    return await message.reply_text(msg)

@app.on_message(filters.command(["listblack"]) & filters.group)
@AdminActual
async def list_black(_, message: Message, __):
    black = await _get_list(message.chat.id, "silent_users")
    if not black:
        return await message.reply_text(">Belum ada pengguna yang diblacklist.")
    msg = "<b>Pengguna Blacklist:</b>\n\n"
    for i, uid in enumerate(black, 1):
        msg += f"{i}. <code>{uid}</code>\n"
    return await message.reply_text(msg)

@app.on_message(filters.command(["listbl"]) & filters.group)
@AdminActual
async def list_word_blacklist(_, message: Message, __):
    words = await _get_list(message.chat.id, "delete_words")
    if not words:
        return await message.reply_text(">Belum ada pesan yg diblacklist.")
    msg = "<b>Daftar Blacklist:</b>\n\n"
    for i, w in enumerate(words, 1):
        msg += f"{i}. {w}\n"
    return await message.reply_text(msg)

# Utility: check if user is chat admin (owner or admin)
async def is_chat_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
    except Exception:
        return False

# Core protection: delete messages from blacklisted users or containing blacklisted words,
# and if delete_all is enabled, delete any non-exempt message immediately.
@app.on_message(filters.group & ~filters.bot, group=2)
async def antigcst_handler(client, message: Message):
    try:
        doc = await COL.find_one(_chat_doc_key(message.chat.id))
        if not doc or not doc.get("protect"):
            return
        if message.sender_chat:
            return
        uid = message.from_user.id if message.from_user else None
        if not uid:
            return

        if uid in doc.get("approved_users", []):
            return
        if await is_chat_admin(client, message.chat.id, uid):
            return
        if uid in SUDOERS:
            return

        warn_text = f"⚠️ WARN , {message.from_user.mention} Pesan anda telah dihapus karena ANDA JELEK."

        async def send_and_delete_warning():
            sent = await client.send_message(
                message.chat.id,
                warn_text,
                reply_to_message_id=message.id
            )
            await asyncio.sleep(5)
            try:
                await client.delete_messages(message.chat.id, sent.id)
            except Exception:
                pass

        if doc.get("delete_all", False):
            try:
                await message.delete()
                await send_and_delete_warning()
            except Exception:
                LOGGER.warning("Failed to delete message in strict mode in chat %s", message.chat.id)
            return

        if uid in doc.get("silent_users", []):
            try:
                await message.delete()
                await send_and_delete_warning()
            except Exception:
                LOGGER.warning("Failed to delete message from blacklisted user in chat %s", message.chat.id)
            return

        text = message.text or message.caption or ""
        for word in doc.get("delete_words", []):
            if word and word.lower() in text.lower():
                try:
                    await message.delete()
                    await send_and_delete_warning()
                except Exception:
                    LOGGER.warning("Failed to delete message containing blacklisted word in chat %s", message.chat.id)
                return
    except Exception as e:
        LOGGER.error("Error in antigcst_handler: %s", e)
