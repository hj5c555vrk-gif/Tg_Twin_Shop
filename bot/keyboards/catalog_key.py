from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def catalog_keyboard(categories):
    keyboard = []

    # Категории
    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"category_{category.id}"
                )
            ]
        )

    # Кнопка возврата в главное меню
    keyboard.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="user_menu"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )