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

        [
            InlineKeyboardButton(
                text="🖼 Фотографии",
                callback_data="admin_photos"
            )
        ],

    ]
)


# Меню управления фотографиями

photo_management_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🟢 Старт",
                callback_data="admin_photo_path_start"
            ),
            InlineKeyboardButton(
                text="👤 Профиль",
                callback_data="admin_photo_path_profile"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Главное меню",
                callback_data="admin_photo_path_menu"
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="admin_menu"
            )
        ]
    ]
)


def get_photo_path_keyboard(path: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Заменить фото",
                    callback_data=f"admin_replace_photo_{path}"
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить фото",
                    callback_data=f"admin_delete_photo_{path}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_photos"
                )
            ]
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