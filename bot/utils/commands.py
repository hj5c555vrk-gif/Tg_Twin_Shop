from aiogram.types import BotCommand


async def set_commands(bot):

    commands = [

        BotCommand(
            command="start",
            description="Запустить бота"
        ),

        BotCommand(
            command="catalog",
            description="Открыть каталог"
        ),

        BotCommand(
            command="cart",
            description="Моя корзина"
        ),

        BotCommand(
            command="menu",
            description="Главное меню"
        ),

        BotCommand(
            command="cancel",
            description="Отменить действие"
        ),

    ]

    await bot.set_my_commands(commands)