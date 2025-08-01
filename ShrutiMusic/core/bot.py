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
        
        await asyncio.sleep(1)
        
        try:
            me = await self.get_me()
            self.id = me.id
            self.name = me.first_name + " " + (me.last_name or "")
            self.username = me.username
            self.mention = me.mention
        except Exception as ex:
            LOGGER(__name__).error(f"Failed to get bot info: {ex}")
            await asyncio.sleep(2)
            try:
                me = await self.get_me()
                self.id = me.id
                self.name = me.first_name + " " + (me.last_name or "")
                self.username = me.username
                self.mention = me.mention
            except Exception as retry_ex:
                LOGGER(__name__).error(f"Retry failed: {retry_ex}")
                exit()
        
        await asyncio.sleep(2)
        
        try:
            chat = await self.get_chat(config.LOG_GROUP_ID)
            LOGGER(__name__).info(f"✅ Successfully accessed log group: {chat.title}")
            
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"🎵 <b>{self.mention} Bot Started Successfully!</b> 🎵\n\n"
                     f"🆔 <b>Bot ID:</b> <code>{self.id}</code>\n"
                     f"👤 <b>Name:</b> {self.name}\n"
                     f"🔗 <b>Username:</b> @{self.username}\n"
                     f"✅ <b>Status:</b> Online & Ready to serve!\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "❌ Bot failed to access log group. Make sure bot is added to the log group."
            )
            exit()
        except errors.ChatWriteForbidden:
            LOGGER(__name__).error(
                "❌ Bot doesn't have permission to write in log group."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Failed to access log group. Reason: {type(ex).__name__}: {ex}"
            )
            exit()
        
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "❌ Please promote bot as admin in log group."
                )
                exit()
        except Exception as ex:
            LOGGER(__name__).error(f"Failed to check admin status: {ex}")
            exit()
        
        LOGGER(__name__).info(f"🎵 Music Bot Started Successfully as {self.name} 🎵")
    
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
