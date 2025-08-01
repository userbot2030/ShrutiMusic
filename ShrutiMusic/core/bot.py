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
import asyncio
import config
from ..logging import LOGGER

class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info(f"🚀 Starting Bot...")
        super().__init__(
            "ShrutiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            sleep_threshold=240,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )
    
    async def start(self):
        await super().start()
        
        get_me = await self.get_me()
        self.id = get_me.id
        self.name = get_me.first_name + " " + (get_me.last_name or "")
        self.username = get_me.username
        self.mention = get_me.mention
        
        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=f"🎵 <b>{self.mention} Bot Started Successfully!</b> 🎵\n\n"
                     f"🆔 <b>Bot ID:</b> <code>{self.id}</code>\n"
                     f"👤 <b>Name:</b> {self.name}\n"
                     f"🔗 <b>Username:</b> @{self.username}\n"
                     f"✅ <b>Status:</b> Online & Ready to serve!\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "❌ Bot failed to access the log group/channel. Make sure that you have added your bot to your log group/channel."
            )
            LOGGER(__name__).error("Error details:", exc_info=True)
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}: {ex}"
            )
            exit()
        
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, "me")
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "❌ Please promote your bot as an admin in your log group/channel."
                )
                exit()
        except Exception:
            pass
        
        LOGGER(__name__).info(f"🎵 Music Bot Started as {self.name}")
    
    async def stop(self):
        try:
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"🔴 <b>{self.mention} Bot Stopped!</b> 🔴\n\n"
                     f"❌ <b>Status:</b> Offline\n"
                     f"⏰ <b>Shutdown:</b> Successful"
            )
        except:
            pass
        await super().stop()
