# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar

import uvloop
import asyncio
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
import config
from ..logging import LOGGER


class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info("🔄 Initializing ShrutiMusic with string session...")
        super().__init__(
            session_name=config.STRING_SESSION,  # string session
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            in_memory=False,  # ✅ stored on disk for longer uptime
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

        # Send startup message with retry (PeerIdInvalid safe)
        chat_id = int(config.LOG_GROUP_ID)
        for attempt in range(3):
            try:
                await self.send_message(
                    chat_id=chat_id,
                    text=(
                        f"<u><b>✅ {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                        f"🆔 ID : <code>{self.id}</code>\n"
                        f"👤 Name : {self.name}\n"
                        f"🔗 Username : @{self.username}"
                    ),
                )
                LOGGER(__name__).info("📩 Sent startup message to log group.")
                break
            except errors.PeerIdInvalid:
                LOGGER(__name__).warning("⚠️ PeerIdInvalid. Retrying...")
                await asyncio.sleep(1)
            except Exception as ex:
                LOGGER(__name__).error(f"❌ Error: {type(ex).__name__} - {ex}")
                exit()

        # Check admin in log group
        try:
            member = await self.get_chat_member(chat_id, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "🚫 Bot is not admin in log group. Promote the bot to ADMIN."
                )
                exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Failed to check bot admin status: {type(ex).__name__} - {ex}"
            )
            exit()

        LOGGER(__name__).info(f"🚀 Shruti Music Bot started successfully as {self.name}.")

        # Start session refresher
        asyncio.create_task(self.session_refresher())

    async def session_refresher(self):
        while True:
            await asyncio.sleep(1800)  # Refresh every 30 mins
            try:
                await self.get_me()
                LOGGER(__name__).info("🔁 Session refreshed.")
            except Exception:
                LOGGER(__name__).warning("⚠️ Session weak. Restarting bot...")
                await self.stop()
                await self.start()

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("🛑 Bot has stopped.")
