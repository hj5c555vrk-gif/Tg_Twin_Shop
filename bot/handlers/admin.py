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
    
# ==========================================================
# СПИСОК ТОВАРОВ
# ==========================================================

@admin_router.callback_query(F.data == "products_list")
async def products_list(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as session:
        products = await get_all_products(session)

    await callback.answer()

    if not products:

        await callback.message.edit_text(
            "<b>📋 Список товаров</b>\n\n"
            "❌ Товаров пока нет.",
            parse_mode="HTML",
            reply_markup=products_keyboard,
        )

        return


    keyboard = []

    text = "<b>📋 Все товары</b>\n\n"


    for product in products:

        text += (
            f"📦 <b>{product.name}</b>\n"
            f"💰 {product.price} ₽\n"
            f"📊 Остаток: {product.stock}\n\n"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"✏️ {product.name}",
                    callback_data=f"edit_{product.id}",
                )
            ]
        )


    keyboard.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_products",
            )
        ]
    )


    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )



# ==========================================================
# РЕДАКТИРОВАНИЕ ТОВАРА
# ==========================================================

@admin_router.callback_query(F.data.startswith("edit_"))
async def edit_product(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return


    product_id = int(
        callback.data.split("_")[1]
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Цена",
                    callback_data=f"price_{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Остаток",
                    callback_data=f"stock_{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Название",
                    callback_data=f"rename_{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Описание",
                    callback_data=f"description_{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="products_list",
                )
            ],
        ]
    )


    await callback.answer()


    await callback.message.edit_text(
        "<b>✏️ Редактирование товара</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=keyboard,
    )



# ==========================================================
# УДАЛЕНИЕ
# ==========================================================

@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_handler(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return


    product_id = int(
        callback.data.split("_")[1]
    )


    async with async_session() as session:

        await delete_product(
            session,
            product_id,
        )


    await callback.answer(
        "Удалено."
    )


    await products_list(callback)



# ==========================================================
# ИЗМЕНЕНИЕ ОСТАТКА
# ==========================================================

@admin_router.callback_query(F.data.startswith("stock_"))
async def edit_stock(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        return


    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()

    await callback.message.answer(
        "Введите новый остаток:"
    )


    await state.set_state(
        AddProductStates.edit_stock
    )



@admin_router.message(AddProductStates.edit_stock)
async def save_stock(
    message: Message,
    state: FSMContext,
):

    try:
        stock = int(message.text)

    except ValueError:

        await message.answer(
            "Введите число."
        )

        return


    data = await state.get_data()


    async with async_session() as session:

        await update_stock(
            session,
            data["product_id"],
            stock,
        )


    await state.clear()

    await message.answer(
        "✅ Остаток обновлён."
    )



# ==========================================================
# ИЗМЕНЕНИЕ ЦЕНЫ
# ==========================================================

@admin_router.callback_query(F.data.startswith("price_"))
async def edit_price(
    callback: CallbackQuery,
    state: FSMContext,
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()

    await callback.message.answer(
        "Введите новую цену:"
    )


    await state.set_state(
        AddProductStates.edit_price
    )



@admin_router.message(AddProductStates.edit_price)
async def save_price(
    message: Message,
    state: FSMContext,
):

    try:

        price = float(
            message.text.replace(",", ".")
        )

    except ValueError:

        await message.answer(
            "Введите корректную цену."
        )

        return


    data = await state.get_data()


    async with async_session() as session:

        await update_product_price(
            session,
            data["product_id"],
            price,
        )


    await state.clear()


    await message.answer(
        "✅ Цена обновлена."
    )



# ==========================================================
# ИЗМЕНЕНИЕ НАЗВАНИЯ
# ==========================================================

@admin_router.callback_query(F.data.startswith("rename_"))
async def rename_product(
    callback: CallbackQuery,
    state: FSMContext,
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новое название:"
    )


    await state.set_state(
        AddProductStates.edit_name
    )



@admin_router.message(AddProductStates.edit_name)
async def save_name(
    message: Message,
    state: FSMContext,
):

    data = await state.get_data()


    async with async_session() as session:

        await update_product_name(
            session,
            data["product_id"],
            message.text,
        )


    await state.clear()


    await message.answer(
        "✅ Название изменено."
    )



# ==========================================================
# ИЗМЕНЕНИЕ ОПИСАНИЯ
# ==========================================================

@admin_router.callback_query(F.data.startswith("description_"))
async def edit_description(
    callback: CallbackQuery,
    state: FSMContext,
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новое описание:"
    )


    await state.set_state(
        AddProductStates.edit_description
    )



@admin_router.message(AddProductStates.edit_description)
async def save_description(
    message: Message,
    state: FSMContext,
):

    data = await state.get_data()


    async with async_session() as session:

        await update_product_description(
            session,
            data["product_id"],
            message.text,
        )


    await state.clear()


    await message.answer(
        "✅ Описание обновлено."
    )
    
# ==========================================================
# ПРОВЕРКА ДОСТУПА ДЛЯ РЕДАКТИРОВАНИЯ
# ==========================================================

def admin_only(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)



# ==========================================================
# ДОБАВЛЕНИЕ КНОПОК РЕДАКТИРОВАНИЯ ТОВАРА
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("edit_")
)
async def edit_product(
    callback: CallbackQuery
):

    if not admin_only(callback):
        await callback.answer(
            "Нет доступа",
            show_alert=True
        )
        return


    product_id = int(
        callback.data.split("_")[1]
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="💰 Изменить цену",
                    callback_data=f"price_{product_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📦 Изменить остаток",
                    callback_data=f"stock_{product_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="✏️ Название",
                    callback_data=f"rename_{product_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📝 Описание",
                    callback_data=f"description_{product_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_{product_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="products_list"
                )
            ]
        ]
    )


    await callback.answer()

    await callback.message.edit_text(
        "<b>✏️ Редактирование товара</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=keyboard
    )



# ==========================================================
# УДАЛЕНИЕ ТОВАРА
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("delete_")
)
async def delete_product_handler(
    callback: CallbackQuery
):

    if not admin_only(callback):
        return


    product_id = int(
        callback.data.split("_")[1]
    )


    async with async_session() as session:

        result = await delete_product(
            session,
            product_id
        )


    if result:

        await callback.answer(
            "Товар удалён"
        )

    else:

        await callback.answer(
            "Товар не найден",
            show_alert=True
        )


    await products_list(callback)



# ==========================================================
# ИЗМЕНЕНИЕ ОСТАТКА
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("stock_")
)
async def edit_stock(
    callback: CallbackQuery,
    state: FSMContext
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новый остаток:"
    )


    await state.set_state(
        AddProductStates.edit_stock
    )



@admin_router.message(
    AddProductStates.edit_stock
)
async def save_stock(
    message: Message,
    state: FSMContext
):

    try:

        stock = int(message.text)

    except ValueError:

        await message.answer(
            "Введите число."
        )

        return


    data = await state.get_data()


    async with async_session() as session:

        await update_stock(
            session,
            data["product_id"],
            stock
        )


    await state.clear()


    await message.answer(
        "✅ Остаток изменён"
    )



# ==========================================================
# ИЗМЕНЕНИЕ ЦЕНЫ
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("price_")
)
async def edit_price(
    callback: CallbackQuery,
    state: FSMContext
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новую цену:"
    )


    await state.set_state(
        AddProductStates.edit_price
    )



@admin_router.message(
    AddProductStates.edit_price
)
async def save_price(
    message: Message,
    state: FSMContext
):

    try:

        price = float(
            message.text.replace(",", ".")
        )

    except ValueError:

        await message.answer(
            "Некорректная цена."
        )

        return


    data = await state.get_data()


    async with async_session() as session:

        await update_product_price(
            session,
            data["product_id"],
            price
        )


    await state.clear()


    await message.answer(
        "✅ Цена обновлена"
    )



# ==========================================================
# ИЗМЕНЕНИЕ НАЗВАНИЯ
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("rename_")
)
async def rename_product(
    callback: CallbackQuery,
    state: FSMContext
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новое название:"
    )


    await state.set_state(
        AddProductStates.edit_name
    )



@admin_router.message(
    AddProductStates.edit_name
)
async def save_name(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()


    async with async_session() as session:

        await update_product_name(
            session,
            data["product_id"],
            message.text
        )


    await state.clear()


    await message.answer(
        "✅ Название изменено"
    )



# ==========================================================
# ИЗМЕНЕНИЕ ОПИСАНИЯ
# ==========================================================

@admin_router.callback_query(
    F.data.startswith("description_")
)
async def edit_description(
    callback: CallbackQuery,
    state: FSMContext
):

    product_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        product_id=product_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите новое описание:"
    )


    await state.set_state(
        AddProductStates.edit_description
    )



@admin_router.message(
    AddProductStates.edit_description
)
async def save_description(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()


    async with async_session() as session:

        await update_product_description(
            session,
            data["product_id"],
            message.text
        )


    await state.clear()


    await message.answer(
        "✅ Описание обновлено"
    )