import asyncio
import logging
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import routers
from bot.database.seed_categories import seed_categories
from bot.database.seed_products import seed_products


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


logging.basicConfig(
    level=logging.INFO
)


async def main():

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )


    dp = Dispatcher(
        storage=MemoryStorage()
    )


    for router in routers:
        dp.include_router(router)


    # Временный seed данных
    # после подключения Alembic
    # перенесем отдельно

    async with async_session() as session:

        await seed_categories(session)

        await seed_products(session)


    print(
        "Бот запущен!"
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(main())