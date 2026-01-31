import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()

@router.message()
async def get_id_handler(message: Message):
    if message.forward_from_chat:
        print(f"\n--- FOUND CHANNEL ID ---\nTitle: {message.forward_from_chat.title}\nID: {message.forward_from_chat.id}\n------------------------\n")
        await message.answer(f"Channel Name: {message.forward_from_chat.title}\nChannel ID: `{message.forward_from_chat.id}`", parse_mode="Markdown")
    else:
         print(f"Chat ID: {message.chat.id}")
         await message.answer(f"Your ID: `{message.chat.id}`\n\nForward a message from your channel to get its ID.", parse_mode="Markdown")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("Send any message or forward a channel post to me...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
