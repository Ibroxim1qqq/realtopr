import asyncio
import uvicorn
import logging
import os
from bot.loader import bot, dp
from web.app import app
from bot.handlers import start, realtor

# Register routers
dp.include_router(start.router)
dp.include_router(realtor.router)

async def start_bot():
    print("Bot starting...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted. Starting polling...")
        await dp.start_polling(bot)
        print("Bot polling finished (unexpectedly)!")
    except Exception as e:
        print(f"Bot Error: {e}")

async def start_web():
    print("Web starting...")
    try:
        port = int(os.getenv("PORT", 8002))
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        print("Web server finished (unexpectedly)!")
    except Exception as e:
        print(f"Web Error: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Main started")
    
    tasks = [
        asyncio.create_task(start_bot()),
        asyncio.create_task(start_web())
    ]
    
    print("Gathering tasks...")
    await asyncio.gather(*tasks)
    print("Main finished")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
