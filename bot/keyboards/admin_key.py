from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



# Главное меню администратора

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
            ),
        ],

        [
            InlineKeyboardButton(
                text="👥 Пользователи",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            ),
        ],

        [
            InlineKeyboardButton(
                text="🛒 Заказы",
                callback_data="admin_orders"
            ),
            InlineKeyboardButton(
                text="⚙️ Настройки",
                callback_data="admin_settings"
            ),
        ],

    ]
)



# Меню управления товарами

products_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="➕ Добавить товар",
                callback_data="add_product"
            )
        ],

        [
            InlineKeyboardButton(
                text="📋 Список товаров",
                callback_data="products_list"
            )
        ],

        [
            InlineKeyboardButton(
                text="📦 Управление остатками",
                callback_data="stock_manage"
            )
        ],

        [
            InlineKeyboardButton(
                text="🌈 Управление вкусами",
                callback_data="flavors_manage"
            )
        ],

        [
            InlineKeyboardButton(
                text="✏️ Редактировать товары",
                callback_data="edit_products"
            )
        ],

        [
            InlineKeyboardButton(
                text="🗑 Удалить товар",
                callback_data="delete_product"
            )
        ],

        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_menu"
            )
        ],

    ]
)



# Универсальная кнопка возврата

back_to_admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_menu"
            )
        ]

    ]
)