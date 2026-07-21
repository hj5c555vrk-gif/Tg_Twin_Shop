from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def products_keyboard(products):

    keyboard = []

    for product in products:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=f"product_{product.id}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_catalog"
            )
        ]
    )


    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def product_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data="add_cart"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к товарам",
                    callback_data="back_products"
                )
            ]
        ]
    )