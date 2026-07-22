from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.filters.admin import AdminFilter
from bot.keyboards.user_key import user_menu_keyboard

menu_router = Router()


@menu_router.callback_query(
    F.data == "user_menu",
    ~AdminFilter()
)
async def open_user_menu(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "📋 Главное меню\n\n"
        "Выберите необходимый раздел.",
        reply_markup=user_menu_keyboard
    )
    
from bot.keyboards.admin_key import admin_keyboard


@menu_router.callback_query(
    F.data == "user_menu",
    AdminFilter()
)
async def open_admin_menu(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "🛠 Главное меню администратора",
        reply_markup=admin_keyboard
    )