from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto

from bot.database.admin import ADMIN_ID, is_admin_user
from bot.database.base import async_session
from bot.keyboards.user_key import profile_keyboard, user_menu_keyboard
from bot.keyboards.admin_key import admin_keyboard
from bot.services.cart import clear_cart, get_cart_summary
from bot.services.user import get_user_profile
from bot.services.photos import get_message_photo

menu_router = Router()


def get_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    if is_admin_user(user_id):
        return admin_keyboard
    return user_menu_keyboard


@menu_router.message(Command("menu"))
async def cmd_menu(message: Message):
    async with async_session() as session:
        photo = await get_message_photo(session, "menu")
    await message.answer_photo(
        photo=photo,
        caption="Главнейшее меню\n\nВыбери нужный тебе раздел.",
        reply_markup=get_menu_markup(message.from_user.id),
    )


@menu_router.message(Command("cart"))
async def cmd_cart(message: Message):
    async with async_session() as session:
        summary = await get_cart_summary(session, message.from_user.id)

    if not summary["items"]:
        text = " 🥅 Ворота пустые ."
    else:
        lines = ["<b> 🥅 Ворота </b>", ""]
        for item in summary["items"]:
            lines.append(
                f"• {item['name']}\n"
                f"  Кол-во: {item['quantity']}\n"
                f"  Сумма: {item['line_total']:.2f} ₽"
            )
        lines.append("")
        lines.append(f"🧾 Итого: {summary['total_price']:.2f} ₽")
        lines.append(f"📦 Товаров: {summary['quantity_total']}")
        text = "\n".join(lines)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛍 Забить Гол", callback_data="checkout"),
            ],
            [
                InlineKeyboardButton(text="⛔️ Не забивать гол ", callback_data="clear_cart"),
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu"),
            ],
        ]
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@menu_router.callback_query(F.data == "user_menu")
async def open_menu(callback: CallbackQuery):

    await callback.answer()

    async with async_session() as session:
        photo = await get_message_photo(session, "menu")

    if is_admin_user(callback.from_user.id):
        caption = "🛠 Главное меню администратора"
    else:
        caption = "📋 Главное меню\n\nВыберите необходимый раздел."

    markup = get_menu_markup(callback.from_user.id)

    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
            reply_markup=markup,
        )
    else:
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=markup,
            parse_mode="HTML"
        )
        await callback.message.delete()


@menu_router.callback_query(F.data == "profile")
async def open_profile(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        profile = await get_user_profile(session, callback.from_user.id)
        photo = await get_message_photo(session, "profile")

    favorite_categories = ", ".join(profile["favorite_categories"])
    caption = (
        "<b>👤 Профиль</b>\n\n"
        f"📅 Дата регистрации: {profile['registered_at']}\n"
        f"🛍 Количество заказов: {profile['order_count']}\n"
        f"⭐ Любимые категории: {favorite_categories}"
    )

    if callback.message.photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
            reply_markup=profile_keyboard,
        )
    else:
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=profile_keyboard,
            parse_mode="HTML"
        )
        await callback.message.delete()


@menu_router.callback_query(F.data == "profile_referral")
async def profile_referral(callback: CallbackQuery):
    await callback.answer("А тут и ничего и нет", show_alert=True)


@menu_router.callback_query(F.data == "profile_level")
async def profile_level(callback: CallbackQuery):
    await callback.answer("А тут и ничего и нет", show_alert=True)


@menu_router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        summary = await get_cart_summary(session, callback.from_user.id)

    if not summary["items"]:
        text = "🛒 Корзина пуста."
    else:
        lines = ["<b> 🥅 Ворота </b>", ""]
        for item in summary["items"]:
            lines.append(
                f"• {item['name']}\n"
                f"  Кол-во: {item['quantity']}\n"
                f"  Сумма: {item['line_total']:.2f} ₽"
            )
        lines.append("")
        lines.append(f"🧾 Итого: {summary['total_price']:.2f} ₽")
        lines.append(f"📦 Товаров: {summary['quantity_total']}")
        text = "\n".join(lines)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛍 Забить гол", callback_data="checkout"),
            ],
            [
                InlineKeyboardButton(text="🧹Не забивать Гол ", callback_data="clear_cart"),
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu"),
            ],
        ]
    )

    if callback.message.photo:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.message.delete()
    else:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@menu_router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    async with async_session() as session:
        await clear_cart(session, callback.from_user.id)

    await callback.answer("Корзина очищена")
    await show_cart(callback)


