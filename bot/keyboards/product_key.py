from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



# ==================================================
# СПИСОК ТОВАРОВ В КАТАЛОГЕ
# ==================================================

def products_keyboard(products):

    keyboard = []


    if not products:

        keyboard.append(

            [

                InlineKeyboardButton(

                    text="Нет тут ничо",

                    callback_data="empty"

                )

            ]

        )


    else:


        for product in products:


            keyboard.append(

                [

                    InlineKeyboardButton(

                        text=(
                            f"{product.name} "
                            f"({product.price} Don$han)"
                        ),

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



# ==================================================
# МЕНЮ КОНКРЕТНОГО ТОВАРА
# ==================================================

def product_keyboard(
    product_id: int,
    category_id: int
):


    return InlineKeyboardMarkup(

        inline_keyboard=[


            [

                InlineKeyboardButton(

                    text="🥅 Добавить в Ворота",

                    callback_data=f"add_cart_{product_id}"

                )

            ],


            [

                InlineKeyboardButton(

                    text="⬅️ Назад к товарам",

                    callback_data=f"category_{category_id}"

                )

            ]

        ]

    )