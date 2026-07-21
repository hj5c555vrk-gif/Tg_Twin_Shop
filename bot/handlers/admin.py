from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


admin_router = Router()


print("ADMIN ROUTER LOADED")


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):

    print(
        "ADMIN COMMAND RECEIVED:",
        message.from_user.id
    )

    await message.answer(
        "🔐 Админ-панель\n\n"
        "/stats — статистика\n"
        "/users — пользователи\n"
        "/products — товары"
    )