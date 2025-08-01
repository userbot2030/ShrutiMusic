# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar

import uvloop
import config
from pyrogram import Client, errors
from pyrogram.enums import ParseMode, ChatMemberStatus
from ..logging import LOGGER

uvloop.install()


class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info("🚀 Starting ShrutiMusic bot initialization...")
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

        self.id = self.me.id
        self.name = self.me.first_name + (f" {self.me.last_name}" if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        LOGGER(__name__).info(
            f"✅ Bot identity fetched: ID={self.id}, Name={self.name}, Username=@{self.username}"
        )

        try:
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=(
                    f"<b>✨ ShrutiMusic Bot Started!</b>\n\n"
                    f"<b>🆔 ID:</b> <code>{self.id}</code>\n"
                    f"<b>👤 Name:</b> {self.name}\n"
                    f"<b>🔗 Username:</b> @{self.username}\n"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "❌ Log group access failed: Check if bot is added to the group/channel!"
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Unexpected error while accessing log group: {type(ex).__name__}"
            )
            exit()

        try:
            member = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("❌ Please promote your bot as an admin in the log group!")
                exit()
        except Exception as e:
            LOGGER(__name__).error(f"❌ Error occurred while checking bot status: {e}")
            exit()

        LOGGER(__name__).info(f"🎵 Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("🛑 Bot stopped successfully.")
