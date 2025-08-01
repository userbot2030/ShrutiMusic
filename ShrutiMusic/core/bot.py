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
import asyncio

class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot...")
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
        
        # Wait for client initialization
        await asyncio.sleep(2)
        
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
        
        # Force peer resolution for new pyrogram versions
        try:
            # First try to resolve the peer using invoke
            from pyrogram.raw.functions.messages import GetChats
            from pyrogram.raw.types import InputChannel
            
            # Extract channel ID and access hash if needed
            chat_id = config.LOG_GROUP_ID
            if str(chat_id).startswith("-100"):
                # It's a supergroup/channel
                channel_id = int(str(chat_id)[4:])  # Remove -100 prefix
                
                try:
                    # Try direct access first
                    chat = await self.get_chat(chat_id)
                    LOGGER(__name__).info(f"✅ Successfully accessed log group: {chat.title}")
                except Exception:
                    # If direct access fails, try to resolve peer
                    try:
                        # Send a dummy request to force peer resolution
                        await self.send_message("me", "test")
                        await asyncio.sleep(1)
                        chat = await self.get_chat(chat_id)
                        LOGGER(__name__).info(f"✅ Successfully accessed log group after resolution: {chat.title}")
                    except Exception as resolve_ex:
                        LOGGER(__name__).error(f"Failed to resolve peer: {resolve_ex}")
                        raise
            else:
                chat = await self.get_chat(chat_id)
                LOGGER(__name__).info(f"✅ Successfully accessed log group: {chat.title}")
            
            # Send startup message
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
        except ValueError as ve:
            if "Peer id invalid" in str(ve):
                LOGGER(__name__).error(
                    f"❌ Invalid LOG_GROUP_ID: {config.LOG_GROUP_ID}. Please check the group ID format."
                )
            else:
                LOGGER(__name__).error(f"❌ ValueError: {ve}")
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Failed to access log group. Reason: {type(ex).__name__}: {ex}"
            )
            exit()
        
        try:
            member = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                LOGGER(__name__).error(
                    "❌ Please promote bot as admin in log group."
                )
                exit()
        except Exception as ex:
            LOGGER(__name__).error(f"Failed to check admin status: {ex}")
            exit()
            
        LOGGER(__name__).info(f"🎵 Music Bot Started Successfully as {self.name} 🎵")

    async def stop(self):
        await super().stop()
