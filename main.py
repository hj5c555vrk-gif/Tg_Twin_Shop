import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from bot.handlers import routers
from bot.database.seed_categories import seed_categories


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    # Подключение всех обработчиков
    for router in routers:
        dp.include_router(router)

    # Создание таблиц базы данных
    from bot.database.base import engine, async_session
    from bot.database.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Добавление стартовых категорий
    async with async_session() as session:
        await seed_categories(session)

    print("Бот запущен с базой данных!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())