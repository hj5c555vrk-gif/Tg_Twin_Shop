from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.database.admin import ADMIN_ID
from bot.keyboards.admin_key import (
    admin_keyboard,
    back_to_admin_keyboard,
)

admin_router = Router()


print("ADMIN ROUTER LOADED")


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "⛔ У вас нет доступа."
        )
        return

    await message.answer(
        "<b>🔐 Панель администратора</b>\n\n"
        "Выберите необходимый раздел.",
        reply_markup=admin_keyboard,
        parse_mode="HTML",
    )
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
    
@admin_router.callback_query(
    F.data.startswith("admin_"),
    F.data != "admin_menu",
)
async def admin_stub(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Нет доступа",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "🚧 Этот раздел находится в разработке.",
        reply_markup=back_to_admin_keyboard,
    )
    
@admin_router.callback_query(F.data == "admin_menu")
async def back_to_admin(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Нет доступа",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "<b>🔐 Панель администратора</b>\n\n"
        "Выберите необходимый раздел.",
        reply_markup=admin_keyboard,
        parse_mode="HTML",
    )