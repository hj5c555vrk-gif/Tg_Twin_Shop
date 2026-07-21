from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.database.base import async_session

from bot.services.catalog import get_categories
from bot.services.product import get_products_by_category

from bot.keyboards.catalog_key import catalog_keyboard
from bot.keyboards.product_key import products_keyboard


catalog_router = Router()


@catalog_router.message(Command("catalog"))
async def show_catalog(message: Message):

    async with async_session() as session:
        categories = await get_categories(session)

    if not categories:
        await message.answer(
            "Пока нет категорий."
        )
        return

    await message.answer(
        "<b>📦 Каталог товаров</b>\n\n"
        "Выберите категорию:",
        reply_markup=catalog_keyboard(categories),
        parse_mode="HTML"
    )


@catalog_router.callback_query(F.data.startswith("category_"))
async def open_category(callback: CallbackQuery):

    category_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        products = await get_products_by_category(
            session,
            category_id
        )

    if not products:
        await callback.message.edit_text(
            "В этой категории пока нет товаров."
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📦 Выберите товар:",
        reply_markup=products_keyboard(products)
    )

    await callback.answer()
    @catalog_router.callback_query(
    F.data == "back_catalog"
    )

async def back_to_catalog(callback: CallbackQuery):

    async with async_session() as session:
        categories = await get_categories(session)

    await callback.message.edit_text(
        "<b>📦 Каталог товаров</b>\n\n"
        "Выберите категорию:",
        reply_markup=catalog_keyboard(categories),
        parse_mode="HTML"
    )

    await callback.answer()