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
                callback_data="back_to_catalog"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )