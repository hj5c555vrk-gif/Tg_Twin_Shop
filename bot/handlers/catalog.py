from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.database.base import async_session

from bot.services.catalog import get_categories
from bot.services.products import get_products_by_category
from bot.services.category_views import increase_category_view

from bot.keyboards.catalog_key import catalog_keyboard
from bot.keyboards.product_key import products_keyboard


catalog_router = Router()


# ==================================================
# КАТАЛОГ
# ==================================================

@catalog_router.message(Command("catalog"))
async def show_catalog(
    message: Message
):

    async with async_session() as session:

        categories = await get_categories(
            session
        )


    if not categories:

        await message.answer(
            "📦 Каталог пока пуст."
        )

        return


    await message.answer(

        "<b>📦 Каталог товаров</b>\n\n"
        "Выберите категорию:",

        reply_markup=catalog_keyboard(
            categories
        ),

        parse_mode="HTML"

    )



# ==================================================
# ОТКРЫТИЕ КАТЕГОРИИ
# ==================================================

@catalog_router.callback_query(
    F.data.startswith("category_")
)
async def open_category(
    callback: CallbackQuery
):

    try:

        category_id = int(
            callback.data.split("_")[1]
        )

    except ValueError:

        await callback.answer(
            "Ошибка категории.",
            show_alert=True
        )

        return



    async with async_session() as session:


        await increase_category_view(

            session,

            category_id

        )


        products = await get_products_by_category(

            session,

            category_id

        )


    products = [

        product

        for product in products

        if product.available

    ]


    if not products:


        await callback.message.edit_text(

            "📦 В этой категории пока нет доступных товаров."

        )

        await callback.answer()

        return



    await callback.message.edit_text(

        "📦 Выберите товар:",

        reply_markup=products_keyboard(
            products
        )

    )


    await callback.answer()



# ==================================================
# НАЗАД В КАТАЛОГ
# ==================================================

@catalog_router.callback_query(
    F.data == "back_catalog"
)
async def back_to_catalog(
    callback: CallbackQuery
):


    async with async_session() as session:

        categories = await get_categories(
            session
        )


    if not categories:

        await callback.message.edit_text(

            "📦 Каталог пуст."

        )

        await callback.answer()

        return



    await callback.message.edit_text(

        "<b>📦 Каталог товаров</b>\n\n"
        "Выберите категорию:",

        reply_markup=catalog_keyboard(
            categories
        ),

        parse_mode="HTML"

    )


    await callback.answer()