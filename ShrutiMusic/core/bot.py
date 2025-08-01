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

import uvloop
uvloop.install()

from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
import config
from ..logging import LOGGER


class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info("🔄 Initializing bot client...")
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
        self.me = await self.get_me()

        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        LOGGER(__name__).info(
            f"✅ Bot identity fetched: ID={self.id}, Name={self.name}, Username=@{self.username}"
        )

        try:
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=(
                    f"<u><b>✅ {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"🆔 ID : <code>{self.id}</code>\n"
                    f"👤 Name : {self.name}\n"
                    f"🔗 Username : @{self.username}"
                ),
            )
            LOGGER(__name__).info("📩 Successfully sent startup message to log group.")
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "❌ Bot failed to access the log group/channel. "
                "Make sure your bot is added to the group/channel!"
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Unexpected error while accessing log group: {type(ex).__name__}"
            )
            exit()

        try:
            member_status = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if member_status.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "🚫 Bot is not admin in the log group/channel. "
                    "Please promote the bot to ADMIN."
                )
                exit()
        except Exception as e:
            LOGGER(__name__).error(
                f"⚠️ Could not verify bot's admin status in log group: {e}"
            )
            exit()

        LOGGER(__name__).info(f"🚀 Shruti Music Bot started successfully as {self.name}.")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("🛑 Bot stopped. See you next time!")
