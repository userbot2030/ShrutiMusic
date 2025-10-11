# antigcst plugin for ShrutiMusic
# Adds per-chat anti-gcast/anti-spam protections with global owner-only toggle and SUDOERS override.
# New feature: "delete_all" (strict) mode which deletes any non-exempt message immediately.
# New feature: notifications — bot sends a group notification message when protect or delete_all is toggled.
#
# - /protect or /antigcast [on|off]         -> toggle protection (respects global only-owner & sudo override)
# - /protectmode or /antigcstmode all on|off -> per-chat: enable/disable delete-all (strict) mode
# - /antigcstconfig                         -> OWNER only: manage global settings (onlyowner, sudooverride)
# - /free, /unfree, /listwhite, /clearwhite -> whitelist users (approved)
# - /addblack, /delblack, /listblack, /clearblack -> blacklist users (silent)
# - /bl, /unbl, /listbl                     -> text blacklist (delete messages containing listed phrases)
#
# Stored in MongoDB collections: antigcst (per-chat) and antigcst_config (global)
# Access: chat admin commands are protected by AdminActual; global config is OWNER-only.

from typing import List

from pyrogram import filters, errors, enums
from pyrogram.types import Message

from ShrutiMusic import app, mongodb, SUDOERS, LOGGER, config
from ShrutiMusic.utils.decorators import AdminActual

COL = mongodb.antigcst  # per-chat collection
CFG = mongodb.antigcst_config  # global config collection

def _chat_doc_key(chat_id: int):
    return {"chat_id": chat_id}

async def _get_doc(chat_id: int) -> dict:
    doc = await COL.find_one(_chat_doc_key(chat_id))
    if not doc:
        doc = {
            "chat_id": chat_id,
            "protect": False,
            "delete_all": False,  # strict mode: delete any message (except exempt)
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

# Global config helpers
async def _get_global_config() -> dict:
    cfg = await CFG.find_one({"_id": "settings"})
    if not cfg:
        cfg = {"_id": "settings", "only_owner_toggle": False, "sudo_override": True}
        await CFG.insert_one(cfg)
    return cfg

async def _set_global_config(field: str, value):
    await CFG.update_one({"_id": "settings"}, {"$set": {field: value}}, upsert=True)

async def _notify_chat_toggle(chat_id: int, text: str):
    """
    Send a persistent notification to the chat about toggles.
    This helps members know that strict mode / protect changed.
    """
    try:
        await app.send_message(chat_id, text)
    except Exception:
        LOGGER.warning("Failed to send antigcst toggle notification to %s", chat_id)


@app.on_message(filters.command(["protect", "antigcast"]) & filters.group)
@AdminActual
async def antigcst_toggle(client, message: Message):
    """
    /protect on|off
    /antigcast on|off

    Behavior:
    - If global only_owner_toggle is True then only OWNER_ID can toggle per-chat protect,
      unless sudo_override is True and the invoking user is in SUDOERS.
    - Sends a notification message to the chat when toggled.
    """
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply_text(">Gunakan format: /protect [on|off]")

    mode = message.command[1].lower()

    # load global config and enforce owner-only toggle if enabled
    try:
        cfg = await _get_global_config()
    except Exception:
        cfg = {"only_owner_toggle": False, "sudo_override": True}

    only_owner = cfg.get("only_owner_toggle", False)
    sudo_override = cfg.get("sudo_override", True)
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if only_owner:
        # owner always allowed
        owner_id = getattr(config, "OWNER_ID", None)
        if user_id != owner_id:
            # allow SUDOERS only if sudo_override enabled
            if not (sudo_override and user_id in SUDOERS):
                return await message.reply_text(">Hanya owner (atau SUDOERS jika sudo_override aktif) yang dapat mengubah pengaturan protect.")

    if mode in ("on", "true", "1"):
        doc = await _get_doc(chat_id)
        if doc.get("protect"):
            return await message.reply_text(">Protect sudah diaktifkan.")
        await _set_protect(chat_id, True)
        await _notify_chat_toggle(chat_id, f"🔒 Anti-Gcast PROTECT diaktifkan oleh {user_mention}.")
        return await message.reply_text(">Berhasil mengaktifkan protect.")
    elif mode in ("off", "false", "0"):
        doc = await _get_doc(chat_id)
        if not doc.get("protect"):
            return await message.reply_text(">Protect belum diaktifkan.")
        await _set_protect(chat_id, False)
        await _notify_chat_toggle(chat_id, f"🔓 Anti-Gcast PROTECT dinonaktifkan oleh {user_mention}.")
        return await message.reply_text(">Berhasil menonaktifkan protect.")
    else:
        return await message.reply_text(">Format salah. Gunakan: /protect [on|off]")


# Per-chat strict mode: delete any message (except exemptions)
@app.on_message(filters.command(["protectmode", "antigcstmode"]) & filters.group)
@AdminActual
async def antigcst_mode(client, message: Message):
    """
    /protectmode all on|off
    /antigcstmode all on|off

