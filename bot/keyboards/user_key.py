from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Открыть меню",
                callback_data="user_menu"
            )
        ]
    ]
)


user_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="📦 Каталог",
                callback_data="catalog"
            )
        ],

        [
            InlineKeyboardButton(
                text="🛒 Корзина",
                callback_data="cart"
            )
        ],

        [
            InlineKeyboardButton(
                text="📦 Мои заказы",
                callback_data="orders"
            )
        ],

        [
            InlineKeyboardButton(
                text="ℹ️ Информация",
                callback_data="info"
            )
        ]

    ]
)