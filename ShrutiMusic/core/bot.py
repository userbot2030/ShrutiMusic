# ShrutiMusic/core/bot.py
import logging as _stdlib_logging

def enable_uvloop() -> None:
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass

# Import pyrogram and types
import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

# Resolve the project's LOGGER export in a robust way.
# It handles:
# - LOGGER being a logger instance (has .info)
# - LOGGER being a factory function (callable) that returns a logger when called with a name
# - fall back to stdlib logging.getLogger(__name__)
def _resolve_project_logger():
    try:
        from ..logging import LOGGER as _project_LOGGER  # type: ignore
    except Exception:
        return _stdlib_logging.getLogger(__name__)

    # If it already looks like a logger instance, use it
    if hasattr(_project_LOGGER, "info"):
        return _project_LOGGER

    # If it's callable, try calling it to obtain a logger
    if callable(_project_LOGGER):
        try:
            candidate = _project_LOGGER(__name__)
            if hasattr(candidate, "info"):
                return candidate
        except Exception:
            # If calling fails, fall back below
            pass

    # Unknown shape or everything failed -> fallback to stdlib
    return _stdlib_logging.getLogger(__name__)


LOGGER = _resolve_project_logger()

# Optional: small diagnostic print (will appear in logs once imported)
try:
    LOGGER.debug("Resolved LOGGER: %s (has info=%s)", type(LOGGER), hasattr(LOGGER, "info"))
except Exception:
    # If logging isn't configured yet, ignore
    pass


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
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.mention = me.mention

        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏", url=f"https://t.me/{self.username}?startgroup=true")]]
        )

        if config.LOG_GROUP_ID:
            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=f"╔════❰𝗪𝗘𝗟𝗖𝗢𝗠𝗘❱════\n║\n║┣⪼ {self.name}\n║┣⪼🎈ɪᴅ:- `{self.id}` \n║┣⪼🎄@{self.username}\n╚════════",
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden as e:
                LOGGER.error("Bot cannot write to the log group: %s", e)
                try:
                    await self.send_message(config.LOG_GROUP_ID, f"Bot started: {self.name}", reply_markup=button)
                except Exception as e2:
                    LOGGER.error("Failed to send message in log group: %s", e2)
            except Exception as e:
                LOGGER.error("Unexpected error while sending to log group: %s", e)
        else:
            LOGGER.warning("LOG_GROUP_ID is not set, skipping log group notifications.")

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
