from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.base import async_session
from bot.services.catalog import get_categories
from bot.keyboards.catalog_key import catalog_keyboard
from bot.services.user import get_or_create_user

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message):

    async with async_session() as session:
        await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        await message.answer(
            "Сап 🖐️, это Twinstore!\n\n"
            "🗺️Команды Навигации \n\n"
            "/catalog — посмотреть категории\n"
            "/start — перезапустить"
    )