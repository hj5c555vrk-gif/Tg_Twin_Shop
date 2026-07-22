from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.base import async_session

from bot.services.catalog import get_categories
from bot.services.products import get_products_by_category
from bot.services.category_views import increase_category_view

from bot.keyboards.catalog_key import catalog_keyboard
from bot.keyboards.product_key import products_keyboard


catalog_router = Router()


# ==================================================
# ОБЩАЯ ФУНКЦИЯ ОТКРЫТИЯ КАТАЛОГА
# ==================================================

async def open_catalog(target):

    async with async_session() as session:

        categories = await get_categories(session)


    if not categories:

        text = "📦 Каталог пока пуст."


        if isinstance(target, Message):

            await target.answer(text)

        else:

            await target.message.edit_text(text)


        return


    text = (
        "<b>📦 Каталог товаров</b>\n\n"
        "Выберите категорию:"
    )


    keyboard = catalog_keyboard(categories)


    # Если вызвана команда /catalog
    if isinstance(target, Message):

        await target.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


    # Если вызвана кнопка из меню
    elif isinstance(target, CallbackQuery):

        await target.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )



# ==================================================
# КОМАНДА /catalog
# ==================================================

@catalog_router.message(Command("catalog"))
async def show_catalog(message: Message):

    await open_catalog(message)



# ==================================================
# КНОПКА "📦 Каталог" ИЗ ПОЛЬЗОВАТЕЛЬСКОГО МЕНЮ
# ==================================================

@catalog_router.callback_query(
    F.data == "catalog"
)
async def show_catalog_callback(
    callback: CallbackQuery
):

    await callback.answer()

    await open_catalog(callback)



# ==================================================
# ОТКРЫТИЕ КАТЕГОРИИ
# ==================================================

@catalog_router.callback_query(
    F.data.startswith("category_")
)
async def open_category(
    callback: CallbackQuery
):

    print("CATEGORY CLICK:", callback.data)

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
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="back_catalog"
                )
            ]
    )

    await callback.message.edit_text(
        "📦 В этой категории пока нет доступных товаров.",
        reply_markup=keyboard
    )

    await callback.answer()

    return


    await callback.message.edit_text(

        "📦 Выберите товар:",

        reply_markup=products_keyboard(products)

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

    await callback.answer()

    await open_catalog(callback)