import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

from bot.handlers.user import user_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(user_router)

    # Создаём таблицы при запуске
    from bot.database.base import engine, async_session
    from bot.database.models import Base
    async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

async with async_session() as session:
    await seed_categories(session)

print("Бот запущен с базой данных!")
await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())