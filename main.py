import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import routers
from bot.database.base import Base, engine, async_session
from bot.database.seed_categories import seed_categories
from bot.database.seed_products import seed_products


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


logging.basicConfig(
    level=logging.INFO
)


async def ensure_database_ready() -> None:
    project_root = Path(__file__).resolve().parent
    env = os.environ.copy()
    pythonpath = str(project_root)

    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = pythonpath

    logging.info("Проверяю состояние базы данных...")

    async with engine.connect() as connection:
        try:
            await connection.execute(text("SELECT 1 FROM alembic_version"))
        except Exception:
            await connection.rollback()
            await connection.run_sync(Base.metadata.create_all)
            await connection.commit()
            logging.info("Таблицы созданы напрямую, так как миграционная таблица отсутствует.")
            return

    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=project_root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        error_output = (exc.stderr or exc.stdout or str(exc)).strip()
        logging.warning(
            "Не удалось применить Alembic миграции, пробую создать таблицы напрямую: %s",
            error_output,
        )
        async with engine.connect() as connection:
            await connection.run_sync(Base.metadata.create_all)
            await connection.commit()
    else:
        logging.info("Миграции базы данных применены успешно.")


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


    await ensure_database_ready()

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