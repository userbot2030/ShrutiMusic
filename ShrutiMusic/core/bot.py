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

import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

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
        )
    
    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

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
                    caption=f"🎵 <b>{self.mention} Bot Started Successfully!</b> 🎵\n\n"
                            f"🆔 <b>Bot ID:</b> <code>{self.id}</code>\n"
                            f"👤 <b>Name:</b> {self.name}\n"
                            f"🔗 <b>Username:</b> @{self.username}\n"
                            f"✅ <b>Status:</b> Online & Ready to serve!\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden as e:
                LOGGER(__name__).error(f"Bot cannot write to the log group: {e}")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        f"🎵 <b>{self.mention} Bot Started Successfully!</b> 🎵\n\n"
                        f"🆔 <b>Bot ID:</b> <code>{self.id}</code>\n"
                        f"👤 <b>Name:</b> {self.name}\n"
                        f"🔗 <b>Username:</b> @{self.username}\n"
                        f"✅ <b>Status:</b> Online & Ready to serve!\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        reply_markup=button,
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to send message in log group: {e}")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Unexpected error while sending to log group: {e}"
                )
        else:
            LOGGER(__name__).warning(
                "LOG_GROUP_ID is not set, skipping log group notifications."
            )

        # Check if bot is an admin in the logger group
        if config.LOG_GROUP_ID:
            try:
                chat_member_info = await self.get_chat_member(
                    config.LOG_GROUP_ID, self.id
                )
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error(
                        "❌ Please promote Bot as Admin in Logger Group"
                    )
                    exit()
                else:
                    LOGGER(__name__).info("✅ Bot has admin permissions")
            except Exception as e:
                LOGGER(__name__).error(f"Error occurred while checking bot status: {e}")

        LOGGER(__name__).info(f"🎵 Music Bot Started as {self.name}")
    
    async def stop(self):
        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                f"🔴 <b>{self.mention} Bot Stopped!</b> 🔴\n\n"
                f"❌ <b>Status:</b> Offline\n"
                f"⏰ <b>Shutdown:</b> Successful"
            )
        except:
            pass
        await super().stop()
