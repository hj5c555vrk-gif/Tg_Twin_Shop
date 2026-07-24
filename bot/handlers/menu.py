from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.admin import ADMIN_ID
from bot.database.base import async_session
from bot.keyboards.user_key import profile_keyboard, user_menu_keyboard
from bot.keyboards.admin_key import admin_keyboard
from bot.services.user import get_user_profile

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


@menu_router.callback_query(F.data == "profile")
async def open_profile(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        profile = await get_user_profile(session, callback.from_user.id)

    favorite_categories = ", ".join(profile["favorite_categories"])

    await callback.message.edit_text(
        "<b>👤 Профиль</b>\n\n"
        f"📅 Дата регистрации: {profile['registered_at']}\n"
        f"🛍 Количество заказов: {profile['order_count']}\n"
        f"⭐ Любимые категории: {favorite_categories}",
        reply_markup=profile_keyboard,
        parse_mode="HTML",
    )


@menu_router.callback_query(F.data == "profile_referral")
async def profile_referral(callback: CallbackQuery):
    await callback.answer("А тут и ничего и нет", show_alert=True)


@menu_router.callback_query(F.data == "profile_level")
async def profile_level(callback: CallbackQuery):
    await callback.answer("А тут и ничего и нет", show_alert=True)