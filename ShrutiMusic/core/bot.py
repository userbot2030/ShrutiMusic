# Alternative fix for Pyrogram 2.0.106 peer resolution issue

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
    
    async def resolve_peer_safe(self, peer_id):
        """Safely resolve peer with multiple attempts"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Try to get chat directly
                chat = await self.get_chat(peer_id)
                return chat
            except Exception as e:
                if attempt == max_attempts - 1:
                    LOGGER(__name__).error(f"Failed to resolve peer after {max_attempts} attempts")
                    raise e
                await asyncio.sleep(2)
        return None
    
    async def start(self):
        await super().start()
        
        # Wait for client initialization
        await asyncio.sleep(3)
        
        try:
            me = await self.get_me()
            self.id = me.id
            self.name = me.first_name + " " + (me.last_name or "")
            self.username = me.username
            self.mention = me.mention
            LOGGER(__name__).info(f"Bot info loaded: {self.name} (@{self.username})")
        except Exception as ex:
            LOGGER(__name__).error(f"Failed to get bot info: {ex}")
            exit()
        
        # Try to resolve log group peer
        try:
            LOGGER(__name__).info("Attempting to resolve log group...")
            
            # First, validate the LOG_GROUP_ID format
            log_id = config.LOG_GROUP_ID
            if not isinstance(log_id, int):
                try:
                    log_id = int(log_id)
                except ValueError:
                    LOGGER(__name__).error(f"Invalid LOG_GROUP_ID format: {config.LOG_GROUP_ID}")
                    exit()
            
            # For supergroups/channels, ensure proper format
            if str(log_id).startswith("-100"):
                LOGGER(__name__).info(f"Detected supergroup/channel ID: {log_id}")
            
            # Try multiple resolution methods
            chat = None
            methods = [
                lambda: self.get_chat(log_id),
                lambda: self.resolve_peer_safe(log_id),
            ]
            
            for i, method in enumerate(methods, 1):
                try:
                    LOGGER(__name__).info(f"Trying resolution method {i}...")
                    chat = await method()
                    if chat:
                        LOGGER(__name__).info(f"✅ Successfully resolved using method {i}")
                        break
                except Exception as e:
                    LOGGER(__name__).warning(f"Method {i} failed: {e}")
                    if i < len(methods):
                        await asyncio.sleep(2)
            
            if not chat:
                raise Exception("All resolution methods failed")
            
            # Send startup message
            await self.send_message(
                chat_id=log_id,
                text=f"🎵 <b>{self.mention} Bot Started Successfully!</b> 🎵\n\n"
                     f"🆔 <b>Bot ID:</b> <code>{self.id}</code>\n"
                     f"👤 <b>Name:</b> {self.name}\n"
                     f"🔗 <b>Username:</b> @{self.username}\n"
                     f"✅ <b>Status:</b> Online & Ready!\n\n"
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
            LOGGER(__name__).error(f"❌ ValueError: {ve}")
            LOGGER(__name__).error(f"Check LOG_GROUP_ID format: {config.LOG_GROUP_ID}")
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Failed to access log group. Reason: {type(ex).__name__}: {ex}"
            )
            exit()
        
        # Check admin status
        try:
            member = await self.get_chat_member(log_id, self.id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                LOGGER(__name__).error(
                    "❌ Please promote bot as admin in log group."
                )
                exit()
            LOGGER(__name__).info("✅ Bot has admin permissions")
        except Exception as ex:
            LOGGER(__name__).error(f"Failed to check admin status: {ex}")
            exit()
            
        LOGGER(__name__).info(f"🎵 Music Bot Started Successfully as {self.name} 🎵")
    
    async def stop(self):
        try:
            await self.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"🔴 <b>{self.mention} Bot Stopped!</b> 🔴"
            )
        except:
            pass
        await super().stop()
