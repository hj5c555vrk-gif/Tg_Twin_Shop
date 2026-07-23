from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from sqlalchemy import select

from bot.database.admin import ADMIN_ID
from bot.database.base import async_session
from bot.database.models import Category

from bot.keyboards.admin_key import (
    admin_keyboard,
    back_to_admin_keyboard,
    products_keyboard,
)

from bot.services.analytics import get_analytics
from bot.services.products import (
    create_product,
    get_all_products,
    delete_product,
    update_stock,
    update_product_price,
    update_product_name,
    update_product_description,
)

from bot.states.admin_states import AddProductStates

admin_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ==========================================================
# ГЛАВНОЕ МЕНЮ
# ==========================================================

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return

    await message.answer(
        "<b>🔐 Панель администратора</b>\n\n"
        "Выберите необходимый раздел.",
        parse_mode="HTML",
        reply_markup=admin_keyboard,
    )


@admin_router.callback_query(F.data == "admin_menu")
async def back_to_admin(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.answer()

    await callback.message.edit_text(
        "<b>🔐 Панель администратора</b>\n\n"
        "Выберите раздел.",
        parse_mode="HTML",
        reply_markup=admin_keyboard,
    )


# ==========================================================
# АНАЛИТИКА
# ==========================================================

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as session:
        analytics = await get_analytics(session)

    text = (
        "<b>📊 Аналитика</b>\n\n"
        f"👥 Всего пользователей: {analytics['total']}\n\n"
        f"🟢 Сегодня: {analytics['day']}\n"
        f"📅 Неделя: {analytics['week']}\n"
        f"🗓 Месяц: {analytics['month']}\n\n"
        f"🔥 Популярная категория:\n"
        f"{analytics['popular']}"
    )

    await callback.answer()

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_to_admin_keyboard,
    )


# ==========================================================
# МЕНЮ ТОВАРОВ
# ==========================================================

@admin_router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.answer()

    await callback.message.edit_text(
        "<b>📦 Управление товарами</b>\n\n"
        "Выберите действие.",
        parse_mode="HTML",
        reply_markup=products_keyboard,
    )


# ==========================================================
# ДОБАВЛЕНИЕ ТОВАРА
# ==========================================================

@admin_router.callback_query(F.data == "add_product")
async def add_product(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    await callback.message.answer("📦 Введите название товара:")
    await state.set_state(AddProductStates.name)


@admin_router.message(AddProductStates.name)
async def add_product_name(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    await state.update_data(name=message.text.strip())

    await message.answer("📝 Введите описание товара:")
    await state.set_state(AddProductStates.description)


@admin_router.message(AddProductStates.description)
async def add_product_description(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    await state.update_data(description=message.text)

    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()

    if not categories:
        await message.answer("❌ В базе нет категорий.")
        await state.clear()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"admin_category_{category.id}"
                )
            ]
            for category in categories
        ]
    )

    await message.answer(
        "📂 Выберите категорию:",
        reply_markup=keyboard,
    )

    await state.set_state(AddProductStates.category)


@admin_router.callback_query(
    AddProductStates.category,
    F.data.startswith("admin_category_"),
)
async def choose_category(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    category_id = int(callback.data.split("_")[2])

    await state.update_data(category_id=category_id)

    await callback.answer()

    await callback.message.answer("💰 Введите стоимость товара:")

    await state.set_state(AddProductStates.price)


@admin_router.message(AddProductStates.price)
async def add_product_price(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректную цену.")
        return

    await state.update_data(price=price)

    await message.answer("📦 Введите остаток:")

    await state.set_state(AddProductStates.stock)


@admin_router.message(AddProductStates.stock)
async def add_product_stock(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    try:
        stock = int(message.text)
    except ValueError:
        await message.answer("Введите целое число.")
        return

    data = await state.get_data()

    async with async_session() as session:
        product = await create_product(
            session=session,
            name=data["name"],
            description=data["description"],
            category_id=data["category_id"],
            price=data["price"],
            stock=stock,
        )

    await state.clear()

    await message.answer(
        "✅ Товар успешно добавлен.\n\n"
        f"📦 {product.name}\n"
        f"💰 {product.price} ₽\n"
        f"📊 Остаток: {product.stock}",
        reply_markup=products_keyboard,
    )