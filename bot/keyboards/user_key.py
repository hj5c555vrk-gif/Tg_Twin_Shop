from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗂️ Открыть меню",
                callback_data="user_menu"
            ),
            InlineKeyboardButton(
                text="🧟‍♂️ Профиль",
                callback_data="profile"
            )
        ]
    ]
)


user_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="📖 Каталог",
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
                text="🧟‍♂️ Профиль",
                callback_data="profile"
            )
        ],

    ]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔗 Реферальная ссылка",
                callback_data="profile_referral"
            ),
            InlineKeyboardButton(
                text="🏅 Уровень",
                callback_data="profile_level"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="user_menu"
            )
        ]
    ]
)