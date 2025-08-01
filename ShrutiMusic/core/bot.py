# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# FINAL WORKING SOLUTION

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
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )
    
    async def start(self):
        await super().start()
        
        # Get bot info
        get_me = await self.get_me()
        self.id = get_me.id
        self.name = get_me.first_name + " " + (get_me.last_name or "")
        self.username = get_me.username
        self.mention = get_me.mention
        
        LOGGER(__name__).info(f"✅ Bot started: {self.name}")
        
        # FORCE PEER RESOLUTION - This is the key fix
        try:
            log_id = config.LOG_GROUP_ID
            
            # Method 1: Get dialogs first to populate peer cache
            LOGGER(__name__).info("📱 Loading dialogs to populate peer cache...")
            dialog_count = 0
            async for dialog in self.get_dialogs(limit=100):
                dialog_count += 1
                if dialog.chat.id == log_id:
                    LOGGER(__name__).info(f"✅ Found log group in dialogs: {dialog.chat.title}")
                    break
            
            LOGGER(__name__).info(f"📱 Loaded {dialog_count} dialogs")
            
            # Small delay for peer cache to settle
            await asyncio.sleep(3)
            
            # Method 2: Now try to access the group
            chat = await self.get_chat(log_id)
            LOGGER(__name__).info(f"✅ Successfully accessed: {chat.title}")
            
            # Send startup message
            await self.send_message(
                log_id,
                text=f"🎵 <b>{self.mention} Bot Started!</b> 🎵\n\n"
                     f"🆔 <b>ID:</b> <code>{self.id}</code>\n"
                     f"👤 <b>Name:</b> {self.name}\n"
                     f"🔗 <b>Username:</b> @{self.username}\n"
                     f"✅ <b>Status:</b> Online & Ready!\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            )
            
        except Exception as e:
            LOGGER(__name__).error(f"❌ Error with log group: {e}")
            
            # FALLBACK: Try alternative methods
            try:
                # Alternative 1: Try to resolve peer first
                LOGGER(__name__).info("🔄 Trying peer resolution...")
                peer = await self.resolve_peer(log_id)
                await asyncio.sleep(2)
                
                chat = await self.get_chat(log_id)
                await self.send_message(log_id, f"🎵 {self.mention} Bot Started! (Fallback method)")
                
            except Exception as e2:
                LOGGER(__name__).error(f"❌ Fallback failed: {e2}")
                
                # FINAL FALLBACK: Start without log group
                LOGGER(__name__).warning("⚠️ Starting without log group access")
                LOGGER(__name__).warning("Please check:")
                LOGGER(__name__).warning(f"1. LOG_GROUP_ID: {config.LOG_GROUP_ID}")
                LOGGER(__name__).warning("2. Bot is added to the group")
                LOGGER(__name__).warning("3. Bot has admin permissions")
                
                # Don't exit, just continue without log group
                LOGGER(__name__).info(f"🎵 Bot started as {self.name} (No log group)")
                return
        
        # Check admin permissions
        try:
            member = await self.get_chat_member(log_id, "me")
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("❌ Bot needs admin permissions")
                exit()
            LOGGER(__name__).info("✅ Admin permissions confirmed")
        except Exception as admin_ex:
            LOGGER(__name__).error(f"❌ Admin check failed: {admin_ex}")
        
        LOGGER(__name__).info(f"🎵 Music Bot Started Successfully as {self.name}")
    
    async def stop(self):
        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                f"🔴 <b>{self.mention} Bot Stopped!</b>"
            )
        except:
            pass
        await super().stop()
