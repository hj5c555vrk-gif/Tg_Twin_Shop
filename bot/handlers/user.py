from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.base import async_session
from bot.services.catalog import get_categories
from bot.keyboards.catalog_key import catalog_keyboard

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

    if not categories:
        await message.answer(
            "Пока нет категорий.\nДобавьте их позже через админ-панель."
        )
        return

    await message.answer(
        "<b>📦 Каталог товаров</b>\n\nВыберите категорию:",
        reply_markup=catalog_keyboard(categories),
        parse_mode="HTML"
    )