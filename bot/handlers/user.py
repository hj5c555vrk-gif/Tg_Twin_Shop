from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.base import async_session
from bot.services.catalog import get_categories

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в магазин!\n\n"
        "Команды:\n"
        "/catalog — посмотреть категории\n"
        "/start — перезапустить"
    )
@user_router.message(Command("catalog"))
async def show_catalog(message: Message):
    async with async_session() as session:
        categories = await get_categories(session)

        print("КАТЕГОРИИ ИЗ БАЗЫ:", categories)

        if categories:
            text = "<b>Категории товаров:</b>\n\n"

            for cat in categories:
                text += f"• {cat.name}\n"

            await message.answer(text, parse_mode="HTML")
        else:
            await message.answer(
                "Пока нет категорий.\nДобавьте их позже через админ-панель."
            )