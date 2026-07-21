from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.base import async_session
from bot.database.models import Product


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
        f"💰 Цена: {product.price} ₽"
    )


    await callback.message.edit_text(
        text,
        parse_mode="HTML"
    )

    await callback.answer()