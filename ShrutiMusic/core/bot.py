# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# Core bot client for ShrutiMusic.
# NOTE: don't call uvloop.install() at import time; call enable_uvloop() from entrypoint if needed.

import logging as _stdlib_logging
from typing import Any

# Helper: install uvloop from your entrypoint if desired
def enable_uvloop() -> None:
    try:
        import uvloop
        uvloop.install()
    except Exception:
        # If uvloop not available or fails, continue with default loop
        pass

# Pyrogram imports
import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

# Robust resolver for the project's LOGGER export.
# - If ShrutiMusic/logging.py exports a logger instance -> use it.
# - If it exports a factory function LOGGER(name) -> call it to get logger.
# - Otherwise fallback to stdlib logger.
def _resolve_project_logger():
    try:
        from ..logging import LOGGER as _project_LOGGER  # type: ignore
    except Exception:
        return _stdlib_logging.getLogger(__name__)

    # If it's already a logger instance (has .info callable), use it
    if hasattr(_project_LOGGER, "info") and callable(getattr(_project_LOGGER, "info")):
        return _project_LOGGER

    # If it's callable (likely a factory), call it to obtain a logger instance
    if callable(_project_LOGGER):
        try:
            candidate = _project_LOGGER(__name__)
            if hasattr(candidate, "info") and callable(getattr(candidate, "info")):
                return candidate
        except Exception:
            # ignore and fallback
            pass

    # Final fallback
    return _stdlib_logging.getLogger(__name__)


# Module-level logger instance (safe to call LOGGER.info(...))
LOGGER = _resolve_project_logger()

# Small diagnostic (optional) — safe if logging not configured
try:
    LOGGER.debug("Resolved LOGGER: %s (has info=%s)", type(LOGGER), hasattr(LOGGER, "info"))
except Exception:
    pass


class Nand(Client):
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
                LOGGER.error("Bot cannot write to the log group: %s", e)
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
                except Exception as e:
                    LOGGER.error("Failed to send message in log group: %s", e)
            except Exception as e:
                LOGGER.error("Unexpected error while sending to log group: %s", e)
        else:
            LOGGER.warning("LOG_GROUP_ID is not set, skipping log group notifications.")

        # Check if bot is an admin in the logger group
        if config.LOG_GROUP_ID:
            try:
                chat_member_info = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER.error("Please promote Bot as Admin in Logger Group")
            except Exception as e:
                LOGGER.error("Error occurred while checking bot status: %s", e)

        LOGGER.info("Music Bot Started as %s", self.name)

    async def stop(self):
        await super().stop()
