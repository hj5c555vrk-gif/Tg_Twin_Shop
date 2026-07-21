from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.database.admin import ADMIN_ID
from bot.keyboards.admin_key import admin_keyboard


admin_router = Router()


print("ADMIN ROUTER LOADED")


@admin_router.message(Command("admin"))
async def admin_test(message: Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "⛔ У вас нет доступа к админ-панели"
        )
        return


    print(
        "ADMIN COMMAND RECEIVED:",
        message.from_user.id
    )


    await message.answer(
    "<b>🔐 Панель администратора</b>\n\n"
    "Добро пожаловать.\n"
    "Выберите необходимый раздел.",
    reply_markup=admin_keyboard,
    parse_mode="HTML"
    )
    
from aiogram.types import CallbackQuery
from aiogram import F


@admin_router.callback_query(F.data.startswith("admin_"))
async def admin_callbacks(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "🚧 Этот раздел находится в разработке."
    )