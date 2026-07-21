from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
            "⛔ У вас нет доступа к панели администратора."
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
        parse_mode="HTML",
    )


@admin_router.callback_query(
    F.data.startswith("admin_") & (F.data != "admin_menu")
)
async def admin_sections(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )
        return

    await callback.answer()

    section_names = {
        "admin_products": "📦 Товары",
        "admin_categories": "📂 Категории",
        "admin_users": "👥 Пользователи",
        "admin_stats": "📊 Статистика",
        "admin_orders": "🛒 Заказы",
        "admin_settings": "⚙️ Настройки",
    }

    section = section_names.get(
        callback.data,
        "Неизвестный раздел"
    )

    await callback.message.edit_text(
        f"<b>{section}</b>\n\n"
        "🚧 Этот раздел находится в разработке.",
        reply_markup=back_to_admin_keyboard,
        parse_mode="HTML",
    )


@admin_router.callback_query(F.data == "admin_menu")
async def back_to_admin(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "<b>🔐 Панель администратора</b>\n\n"
        "Добро пожаловать.\n"
        "Выберите необходимый раздел.",
        reply_markup=admin_keyboard,
        parse_mode="HTML",
    )