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
        "Всем сап, это Twinstore!\n\n"
        "Команды Навигации по магазину \n"
        "/catalog — посмотреть категории\n"
        "/start — перезапустить"
    )