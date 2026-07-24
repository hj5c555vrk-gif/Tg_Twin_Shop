from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.database.base import async_session
from bot.services.user import get_or_create_user
from bot.keyboards.user_key import start_keyboard

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message):

    async with async_session() as session:
        await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )

    await message.answer(
        " Сап 🖖 \n"
        "это гадкий и сладкий twinbot от канала @twinstore_gng!\n\n"
        "Нажми эту чертову кнопку ниже, чтобы открыть это чертово меню.",
        reply_markup=start_keyboard,
    )

