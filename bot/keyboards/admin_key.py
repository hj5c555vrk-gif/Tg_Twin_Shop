from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📦 Товары",
                callback_data="admin_products"
            ),
            InlineKeyboardButton(
                text="📂 Категории",
                callback_data="admin_categories"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Пользователи",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙ Настройки",
                callback_data="admin_settings"
            )
        ]
    ]
)