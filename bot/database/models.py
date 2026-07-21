from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext

from sqlalchemy import select


from bot.database.admin import ADMIN_ID

from bot.keyboards.admin_key import (
    admin_keyboard,
    back_to_admin_keyboard,
    products_keyboard,
)

from bot.database.base import async_session

from bot.services.products import create_product

from bot.states.admin_states import AddProductStates



admin_router = Router()


print("ADMIN ROUTER LOADED")



# ==================================================
# ГЛАВНАЯ АДМИН ПАНЕЛЬ
# ==================================================


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "⛔ У вас нет доступа к панели администратора."
        )

        return


    await message.answer(

        "<b>🔐 Панель администратора</b>\n\n"
        "Добро пожаловать.\n"
        "Выберите необходимый раздел.",

        reply_markup=admin_keyboard,

        parse_mode="HTML"
    )



# ==================================================
# АНАЛИТИКА
# ==================================================


@admin_router.callback_query(
    F.data == "admin_stats"
)
async def admin_analytics(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return


    async with async_session() as session:

        data = await get_analytics(session)


    text = (

        "<b>📊 Аналитика</b>\n\n"

        f"👥 Всего пользователей: {data['total']}\n\n"

        f"🟢 За сегодня: {data['day']}\n"

        f"📅 За неделю: {data['week']}\n"

        f"🗓 За месяц: {data['month']}\n\n"

        f"🔥 Популярная категория:\n"
        f"{data['popular']}"

    )


    await callback.answer()


    await callback.message.edit_text(

        text,

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# ТОВАРЫ
# ==================================================


@admin_router.callback_query(
    F.data == "admin_products"
)
async def admin_products(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return


    await callback.answer()


    await callback.message.edit_text(

        "<b>📦 Управление товарами</b>\n\n"
        "Выберите действие:",

        reply_markup=products_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# ДОБАВЛЕНИЕ ТОВАРА
# ==================================================


@admin_router.callback_query(
    F.data == "add_product"
)
async def add_product(
    callback: CallbackQuery,
    state: FSMContext
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return


    await callback.answer()


    await callback.message.answer(

        "➕ Добавление товара\n\n"
        "Введите название товара:"

    )


    await state.set_state(
        AddProductStates.name
    )



@admin_router.message(
    AddProductStates.name
)
async def product_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        name=message.text
    )


    await message.answer(
        "Введите описание товара:"
    )


    await state.set_state(
        AddProductStates.description
    )



@admin_router.message(
    AddProductStates.description
)
async def product_description(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        description=message.text
    )


    async with async_session() as session:

        result = await session.execute(
            select(Category)
        )

        categories = result.scalars().all()


    if not categories:

        await message.answer(
            "❌ Категории отсутствуют."
        )

        await state.clear()

        return



    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[]
    )


    for category in categories:

        keyboard.inline_keyboard.append(

            [

                InlineKeyboardButton(

                    text=category.name,

                    callback_data=f"category_{category.id}"

                )

            ]

        )


    await message.answer(

        "📂 Выберите категорию:",

        reply_markup=keyboard

    )


    await state.set_state(
        AddProductStates.category
    )



@admin_router.callback_query(
    F.data.startswith("category_")
)
async def select_category(
    callback: CallbackQuery,
    state: FSMContext
):

    category_id = int(
        callback.data.split("_")[1]
    )


    await state.update_data(
        category_id=category_id
    )


    await callback.answer()


    await callback.message.answer(
        "Введите цену товара:"
    )


    await state.set_state(
        AddProductStates.price
    )



@admin_router.message(
    AddProductStates.price
)
async def product_price(
    message: Message,
    state: FSMContext
):

    try:

        price = float(
            message.text
        )

    except ValueError:

        await message.answer(
            "Введите число."
        )

        return



    await state.update_data(
        price=price
    )


    await message.answer(
        "Введите количество товара:"
    )


    await state.set_state(
        AddProductStates.stock
    )



@admin_router.message(
    AddProductStates.stock
)
async def product_stock(
    message: Message,
    state: FSMContext
):

    try:

        stock = int(
            message.text
        )

    except ValueError:

        await message.answer(
            "Введите целое число."
        )

        return



    data = await state.get_data()



    async with async_session() as session:

        product = await create_product(

            session=session,

            name=data["name"],

            description=data["description"],

            category_id=data["category_id"],

            price=data["price"],

            stock=stock

        )



    await state.clear()



    await message.answer(

        "✅ Товар успешно добавлен!\n\n"

        f"📦 {product.name}\n"

        f"💰 Цена: {product.price}\n"

        f"📊 Остаток: {product.stock}"

    )



# ==================================================
# СПИСОК ТОВАРОВ
# ==================================================


@admin_router.callback_query(
    F.data == "products_list"
)
async def products_list(
    callback: CallbackQuery
):

    await callback.answer()


    await callback.message.edit_text(

        "<b>📋 Список товаров</b>\n\n"
        "Раздел подключается к базе товаров.",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# ОСТАТКИ
# ==================================================


@admin_router.callback_query(
    F.data == "stock_manage"
)
async def stock_manage(
    callback: CallbackQuery
):

    await callback.answer()


    await callback.message.edit_text(

        "<b>📦 Управление остатками</b>",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# ВКУСЫ
# ==================================================


@admin_router.callback_query(
    F.data == "flavors_manage"
)
async def flavors_manage(
    callback: CallbackQuery
):

    await callback.answer()


    await callback.message.edit_text(

        "<b>🌈 Управление вкусами</b>",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# ОСТАЛЬНЫЕ РАЗДЕЛЫ
# ==================================================


@admin_router.callback_query(
    F.data.startswith("admin_")
    & (F.data != "admin_menu")
    & (F.data != "admin_products")
)
async def admin_sections(
    callback: CallbackQuery
):

    await callback.answer()


    sections = {

        "admin_categories": "📂 Категории",

        "admin_users": "👥 Пользователи",

        "admin_orders": "🛒 Заказы",

        "admin_settings": "⚙️ Настройки",

    }


    name = sections.get(
        callback.data,
        "Неизвестный раздел"
    )


    await callback.message.edit_text(

        f"<b>{name}</b>\n\n"
        "🚧 Раздел в разработке.",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML"

    )



# ==================================================
# НАЗАД
# ==================================================


@admin_router.callback_query(
    F.data == "admin_menu"
)
async def back_to_admin(
    callback: CallbackQuery
):

    await callback.answer()


    await callback.message.edit_text(

        "<b>🔐 Панель администратора</b>\n\n"
        "Добро пожаловать.\n"
        "Выберите необходимый раздел.",

        reply_markup=admin_keyboard,

        parse_mode="HTML"

    )