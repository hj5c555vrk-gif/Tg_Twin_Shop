from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def catalog_keyboard(categories):
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"category_{category.id}"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)