# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# All rights reserved.
#
# This code is the intellectual property of Nand Yaduwanshi.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: badboy809075@gmail.com

# NOTE:
# - Don't install uvloop at import time in libraries; call enable_uvloop()
#   from your main script before creating/running the client if you want uvloop.

import typing

# Optional helper to install uvloop from your entrypoint:
def enable_uvloop() -> None:
    """
    Call this from your main startup script (if you want uvloop).
    Example:
        from ShrutiMusic.core.bot import enable_uvloop
        enable_uvloop()
        bot = Aviax()
        bot.run()
    """
    try:
        import uvloop

        uvloop.install()
    except Exception:
        # If uvloop is not available, continue with the default loop.
        pass

# Import pyrogram (keep here). If import fails, fix dependencies first (pyrogram/tgcrypto/pyaes).
import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

# Safe import of project LOGGER: try relative import, else fallback to stdlib logging
try:
    from ..logging import LOGGER  # keep existing project logging if present
except Exception:
    import logging

    LOGGER = logging.getLogger(__name__)


class Aviax(Client):
    def __init__(self):
        LOGGER.info("sᴛᴀʀᴛɪɴɢ ʙᴏᴛ...")
        super().__init__(
            name="ShrutiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        # Use the result returned by get_me for consistent values
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.mention = me.mention

        # Create the button
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                        url=f"https://t.me/{self.username}?startgroup=true",
                    )
                ]
            ]
        )

        # Try to send a message to the logger group
        if config.LOG_GROUP_ID:
            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=(
                        "╔════❰𝗪𝗘𝗟𝗖𝗢𝗠𝗘❱════❍⊱❁۪۪\n"
                        "║\n"
                        "║┣⪼🥀ʙᴏᴛ sᴛᴀʀᴛᴇᴅ🎉\n"
                        "║\n"
                        f"║┣⪼ {self.name}\n"
                        "║\n"
                        f"║┣⪼🎈ɪᴅ:- `{self.id}` \n"
                        "║\n"
                        f"║┣⪼🎄@{self.username} \n"
                        "║ \n"
                        "║┣⪼💖ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ😍\n"
                        "║\n"
                        "╚════════════════❍⊱❁"
                    ),
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden as e:
                LOGGER.error(f"Bot cannot write to the log group: {e}")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        (
                            "╔═══❰𝗪𝗘𝗟𝗖𝗢𝗠𝗘❱═══❍⊱❁۪۪\n"
                            "║\n"
                            "║┣⪼🥀ʙᴏᴛ sᴛᴀʀᴛᴇᴅ🎉\n"
                            "║\n"
                            f"║◈ {self.name}\n"
                            "║\n"
                            f"║┣⪼🎈ɪᴅ:- `{self.id}` \n"
                            "║\n"
                            f"║┣⪼🎄@{self.username} \n"
                            "║ \n"
                            "║┣⪼💖ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ😍\n"
                            "║\n"
                            "╚══════════════❍⊱❁"
                        ),
                        reply_markup=button,
                    )
                except Exception as e2:
                    LOGGER.error(f"Failed to send message in log group: {e2}")
            except Exception as e:
                LOGGER.error(f"Unexpected error while sending to log group: {e}")
        else:
            LOGGER.warning("LOG_GROUP_ID is not set, skipping log group notifications.")

        # Check if bot is an admin in the logger group
        if config.LOG_GROUP_ID:
            try:
                chat_member_info = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER.error("Please promote Bot as Admin in Logger Group")
            except Exception as e:
                LOGGER.error(f"Error occurred while checking bot status: {e}")

        LOGGER.info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()


# ©️ Copyright Reserved - @NoxxOP  Nand Yaduwanshi

# ===========================================
# ©️ 2025 Nand Yaduwanshi (aka @NoxxOP)
# 🔗 GitHub : https://github.com/NoxxOP/ShrutiMusic
# 📢 Telegram Channel : https://t.me/ShrutiBots
# ===========================================
