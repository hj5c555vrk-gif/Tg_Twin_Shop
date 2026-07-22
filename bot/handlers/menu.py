from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.admin import ADMIN_ID
from bot.keyboards.user_key import user_menu_keyboard
from bot.keyboards.admin_key import admin_keyboard

menu_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@menu_router.callback_query(F.data == "user_menu")
async def open_menu(callback: CallbackQuery):

    await callback.answer()

    if is_admin(callback.from_user.id):
        await callback.message.edit_text(
            "🛠 Главное меню администратора",
            reply_markup=admin_keyboard
        )
    else:
        await callback.message.edit_text(
            "📋 Главное меню\n\n"
            "Выберите необходимый раздел.",
            reply_markup=user_menu_keyboard
        )