from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command


from bot.database.admin import ADMIN_ID


from bot.keyboards.admin_key import (
    admin_keyboard,
    back_to_admin_keyboard,
    products_keyboard,
)


from bot.database.base import async_session


from bot.services.analytics import get_analytics

from bot.services.products import get_all_products



admin_router = Router()


print("ADMIN ROUTER LOADED")



# ===== ГЛАВНАЯ АДМИН ПАНЕЛЬ =====


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



# ===== АНАЛИТИКА =====


@admin_router.callback_query(
    F.data == "admin_stats"
)
async def admin_analytics(callback: CallbackQuery):

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

        parse_mode="HTML",

    )



# ===== ТОВАРЫ =====


@admin_router.callback_query(
    F.data == "admin_products"
)
async def admin_products(callback: CallbackQuery):

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

        parse_mode="HTML",

    )



# ===== ДОБАВЛЕНИЕ ТОВАРА =====


@admin_router.callback_query(
    F.data == "add_product"
)
async def add_product(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return



    await callback.answer()



    await callback.message.edit_text(

        "<b>➕ Добавление товара</b>\n\n"
        "Функционал добавления подключается.",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML",

    )



# ===== СПИСОК ТОВАРОВ =====


@admin_router.callback_query(
    F.data == "products_list"
)
async def products_list(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return



    async with async_session() as session:

        products = await get_all_products(
            session
        )



    await callback.answer()



    if not products:


        text = (

            "<b>📋 Список товаров</b>\n\n"

            "❌ В базе нет товаров."

        )


    else:


        text = (

            "<b>📋 Список товаров</b>\n\n"

        )



        for product in products:


            category_name = (

                product.category.name

                if product.category

                else "Без категории"

            )



            text += (

                f"📦 <b>{product.name}</b>\n"

                f"📂 {category_name}\n"

                f"💰 {product.price} ₽\n"

                f"📊 Остаток: {product.stock}\n"

                f"🟢 Активен: "
                f"{'Да' if product.available else 'Нет'}\n\n"

            )




    await callback.message.edit_text(

        text,

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML",

    )



# ===== ОСТАТКИ =====


@admin_router.callback_query(
    F.data == "stock_manage"
)
async def stock_manage(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return



    await callback.answer()



    await callback.message.edit_text(

        "<b>📦 Управление остатками</b>\n\n"
        "Раздел подготовки склада.",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML",

    )



# ===== ВКУСЫ =====


@admin_router.callback_query(
    F.data == "flavors_manage"
)
async def flavors_manage(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа.",
            show_alert=True
        )

        return



    await callback.answer()



    await callback.message.edit_text(

        "<b>🌈 Управление вкусами</b>\n\n"
        "Раздел добавления вкусов.",

        reply_markup=back_to_admin_keyboard,

        parse_mode="HTML",

    )



# ===== ОСТАЛЬНЫЕ РАЗДЕЛЫ =====


@admin_router.callback_query(

    F.data.startswith("admin_")

    & (F.data != "admin_menu")

    & (F.data != "admin_products")

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


        "admin_categories": "📂 Категории",

        "admin_users": "👥 Пользователи",

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



# ===== НАЗАД =====


@admin_router.callback_query(
    F.data == "admin_menu"
)
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