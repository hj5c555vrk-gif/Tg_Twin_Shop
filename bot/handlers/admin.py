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

from bot.database.admin import is_admin_user
from bot.database.base import async_session
from bot.database.models import Category
from bot.services.user import get_user_logs

from bot.keyboards.admin_key import (
    admin_keyboard,
    back_to_admin_keyboard,
    products_keyboard,
    photo_management_keyboard,
    get_photo_path_keyboard,
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

from bot.services.photos import (
    get_message_photo,
    set_message_photo,
    delete_message_photo,
)

from bot.states.admin_states import AddProductStates, AddCategoryStates, EditCategoryStates, EditPhotoStates

admin_router = Router()
is_admin = is_admin_user


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
# ПОЛЬЗОВАТЕЛИ
# ==========================================================

@admin_router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as session:
        users = await get_user_logs(session)

    if not users:
        text = "<b>👥 Пользователи</b>\n\nПока нет зарегистрированных пользователей."
    else:
        preview = users[:20]
        lines = ["<b>👥 Пользователи</b>", ""]

        for index, user in enumerate(preview, 1):
            lines.append(
                f"{index}. ID: {user['telegram_id']}\n"
                f"   @: {user['username']}\n"
                f"   Имя: {user['first_name']}\n"
                f"   Регистрация: {user['created_at']}"
            )

        if len(users) > len(preview):
            lines.append(f"\n... и еще {len(users) - len(preview)} пользователей")

        text = "\n\n".join(lines)

    await callback.answer()

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_to_admin_keyboard,
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

@admin_router.callback_query(F.data == "delete_product")
async def delete_product_menu(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as session:
        products = await get_all_products(session)

    await callback.answer()

    keyboard_rows = []

    if products:
        for product in products:
            keyboard_rows.append(
                [
                    InlineKeyboardButton(
                        text=f"🗑 {product.name}",
                        callback_data=f"delete_{product.id}",
                    )
                ]
            )

    keyboard_rows.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_products",
            )
        ]
    )

    await callback.message.edit_text(
        text="<b>🗑 Удаление товара</b>\n\n"
        "Выберите товар для удаления:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows),
    )


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_handler(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    if callback.data == "delete_product":
        await delete_product_menu(callback)
        return

    product_id = int(
        callback.data.split("_")[1]
    )

    async with async_session() as session:
        result = await delete_product(
            session,
            product_id,
        )

    if result:
        await callback.answer("Товар удалён")
    else:
        await callback.answer("Товар не найден", show_alert=True)

    await delete_product_menu(callback)


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

    if callback.data == "delete_product":
        await delete_product_menu(callback)
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

    await delete_product_menu(callback)



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


# ==========================================================
# УПРАВЛЕНИЕ КАТЕГОРИЯМИ
# ==========================================================

@admin_router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать категорию",
                    callback_data="admin_add_category"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать категории",
                    callback_data="admin_edit_categories"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить категории",
                    callback_data="admin_delete_categories"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "<b>📂 Управление категориями</b>\n\n"
        "Выберите необходимое действие.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@admin_router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_categories"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "📝 <b>Создание категории</b>\n\n"
        "Введите название новой категории:",
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await state.set_state(AddCategoryStates.name)


@admin_router.message(AddCategoryStates.name)
async def admin_save_category(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    name = message.text.strip()
    if not name:
        await message.answer("❌ Название категории не может быть пустым. Попробуйте еще раз:")
        return

    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.name == name))
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer("❌ Категория с таким названием уже существует. Введите другое название:")
            return

        new_cat = Category(name=name)
        session.add(new_cat)
        await session.commit()

    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_categories"
                )
            ]
        ]
    )
    await message.answer(
        f"✅ Категория <b>{name}</b> успешно создана!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == "admin_edit_categories")
async def admin_edit_categories(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.name))
        categories = result.scalars().all()

    if not categories:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="admin_categories"
                    )
                ]
            ]
        )
        await callback.message.edit_text(
            "<b>✏️ Редактирование категорий</b>\n\n"
            "❌ Список категорий пуст.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    keyboard_rows = []
    for cat in categories:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"✏️ {cat.name}",
                callback_data=f"admin_edit_cat_{cat.id}"
            )
        ])

    keyboard_rows.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_categories"
        )
    ])

    await callback.message.edit_text(
        "<b>✏️ Редактирование категорий</b>\n\n"
        "Выберите категорию для изменения названия:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    )


@admin_router.callback_query(F.data.startswith("admin_edit_cat_"))
async def admin_edit_cat_name(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)

    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()

    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_edit_categories"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"📝 <b>Редактирование категории</b>\n\n"
        f"Текущее название: <b>{category.name}</b>\n"
        f"Введите новое название для этой категории:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.set_state(EditCategoryStates.name)


@admin_router.message(EditCategoryStates.name)
async def admin_save_edited_category(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    new_name = message.text.strip()
    if not new_name:
        await message.answer("❌ Название категории не может быть пустым. Попробуйте еще раз:")
        return

    data = await state.get_data()
    category_id = data.get("category_id")

    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.name == new_name, Category.id != category_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer("❌ Категория с таким названием уже существует. Введите другое название:")
            return

        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            await message.answer("❌ Категория не найдена в базе данных.")
            await state.clear()
            return

        category.name = new_name
        await session.commit()

    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_categories"
                )
            ]
        ]
    )
    await message.answer(
        f"✅ Название категории успешно изменено на <b>{new_name}</b>!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == "admin_delete_categories")
async def admin_delete_categories(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.name))
        categories = result.scalars().all()

    if not categories:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="admin_categories"
                    )
                ]
            ]
        )
        await callback.message.edit_text(
            "<b>🗑 Удаление категорий</b>\n\n"
            "❌ Список категорий пуст.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    keyboard_rows = []
    for cat in categories:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"🗑 {cat.name}",
                callback_data=f"admin_delete_cat_{cat.id}"
            )
        ])

    keyboard_rows.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_categories"
        )
    ])

    await callback.message.edit_text(
        "<b>🗑 Удаление категорий</b>\n\n"
        "⚠️ <b>Внимание:</b> удаление категории повлечет за собой удаление всех связанных товаров!\n\n"
        "Выберите категорию для удаления:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    )


@admin_router.callback_query(F.data.startswith("admin_delete_cat_"))
async def admin_delete_cat_handler(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    category_id = int(callback.data.split("_")[3])

    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()

        if category:
            await session.delete(category)
            await session.commit()
            await callback.answer("Категория удалена")
        else:
            await callback.answer("Категория не найдена", show_alert=True)

    await admin_delete_categories(callback, state)


# ==========================================================
# УПРАВЛЕНИЕ ФОТОГРАФИЯМИ
# ==========================================================

@admin_router.callback_query(F.data == "admin_photos")
async def admin_photos_menu(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.answer()

    await callback.message.edit_text(
        "<b>🖼 Управление фотографиями сообщений</b>\n\n"
        "Вы можете привязать фотографии к основным разделам меню пользователя.\n"
        "Выберите интересующий путь для настройки:",
        parse_mode="HTML",
        reply_markup=photo_management_keyboard
    )


@admin_router.callback_query(F.data.startswith("admin_photo_path_"))
async def admin_photo_path(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    path = callback.data.split("_")[3]  # admin_photo_path_start -> start
    async with async_session() as session:
        photo = await get_message_photo(session, path)

    await callback.answer()

    await callback.message.edit_text(
        f"<b>🖼 Настройка фото для пути: {path}</b>\n\n"
        f"Текущее фото (file_id или URL):\n<code>{photo}</code>\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_photo_path_keyboard(path)
    )


@admin_router.callback_query(F.data.startswith("admin_delete_photo_"))
async def admin_delete_photo(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    path = callback.data.split("_")[3]
    async with async_session() as session:
        deleted = await delete_message_photo(session, path)

    if deleted:
        await callback.answer("Фотография сброшена до стандартной", show_alert=True)
    else:
        await callback.answer("Кастомная фотография не была установлена", show_alert=True)

    # Refresh view
    async with async_session() as session:
        photo = await get_message_photo(session, path)

    await callback.message.edit_text(
        f"<b>🖼 Настройка фото для пути: {path}</b>\n\n"
        f"Текущее фото (file_id или URL):\n<code>{photo}</code>\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_photo_path_keyboard(path)
    )


@admin_router.callback_query(F.data.startswith("admin_replace_photo_"))
async def admin_replace_photo(callback: CallbackQuery, state: FSMContext):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    path = callback.data.split("_")[3]
    await state.clear()
    await state.update_data(photo_path=path)
    await state.set_state(EditPhotoStates.wait_for_photo)

    await callback.answer()

    back_k = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_photo_path_{path}")
            ]
        ]
    )

    await callback.message.edit_text(
        f"📝 <b>Замена фото для пути: {path}</b>\n\n"
        f"Отправьте новое фото (как изображение) или пришлите прямую ссылку на картинку (текстовым сообщением):",
        parse_mode="HTML",
        reply_markup=back_k
    )


@admin_router.message(EditPhotoStates.wait_for_photo)
async def save_new_path_photo(message: Message, state: FSMContext):

    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    path = data.get("photo_path")
    if not path:
        await state.clear()
        await message.answer("❌ Произошла ошибка. Попробуйте заново.")
        return

    photo_id = None
    if message.photo:
        photo_id = message.photo[-1].file_id
    elif message.text:
        text = message.text.strip()
        if text.startswith("http://") or text.startswith("https://"):
            photo_id = text
        else:
            await message.answer(
                "❌ Пожалуйста, отправьте изображение как фото или пришлите корректную ссылку на изображение (начинающуюся с http:// или https://)."
            )
            return
    else:
        await message.answer(
            "❌ Пожалуйста, отправьте изображение как фото или пришлите корректную ссылку на изображение."
        )
        return

    async with async_session() as session:
        await set_message_photo(session, path, photo_id)

    await state.clear()

    back_k = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="admin_photos")
            ]
        ]
    )

    await message.answer(
        f"✅ Фотография для пути <b>{path}</b> успешно обновлена!",
        parse_mode="HTML",
        reply_markup=back_k
    )