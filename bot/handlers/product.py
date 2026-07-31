from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.base import async_session
from bot.database.models import Product
from bot.keyboards.product_key import product_keyboard
from bot.services.cart import add_product_to_cart


product_router = Router()


@product_router.callback_query(
    F.data.startswith("product_")
)
async def show_product(callback: CallbackQuery):

    product_id = int(
        callback.data.split("_")[1]
    )

    async with async_session() as session:

        product = await session.get(
            Product,
            product_id
        )

    if not product:
        await callback.answer(
            "Товар не найден",
            show_alert=True
        )
        return


    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f" 💸 Ценность: {product.price} Донжуанов"
    )


    await callback.message.edit_text(
    text,
    reply_markup=product_keyboard(product.id),
    parse_mode="HTML"
    )

    await callback.answer()


@product_router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        await add_product_to_cart(
            session,
            callback.from_user.id,
            product_id,
            quantity=1,
        )

    await callback.answer("Товар добавлен в корзину")