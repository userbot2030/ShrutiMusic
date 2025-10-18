#!/usr/bin/env python3
"""
start.py
Ensures an asyncio event loop (and uvloop policy, if available) is set
before importing/running the ShrutiMusic package. Use this as the
entrypoint in Procfile for Heroku worker dynos.
"""
import asyncio
import runpy
import sys
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("start")

# Try to enable uvloop policy if available (fast, but optional)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    log.info("uvloop EventLoopPolicy set")
except Exception:
    log.info("uvloop not available or failed to set; continuing with default loop policy")

# Ensure there is a running event loop in the main thread before importing pyrogram.sync
try:
    asyncio.get_event_loop()
    log.info("Existing event loop found")
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    log.info("New event loop created and set as current loop")

# Run the package as module (equivalent to python -m ShrutiMusic)
# If your package's entrypoint is different, adjust the module name.
if __name__ == "__main__":
    try:
        runpy.run_module("ShrutiMusic", run_name="__main__")
    except Exception:
        log.exception("Failed to start ShrutiMusic")
        raise
else:
    # If imported, expose nothing special
    pass
