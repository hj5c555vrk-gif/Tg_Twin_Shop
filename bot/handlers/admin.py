print("ADMIN HANDLER LOADED")
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.database.base import async_session
from bot.services.admin import is_admin


admin_router = Router()


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    
    async with async_session() as session:
    
    message.from_user.id
)
        check = await is_admin(
            session,
            message.from_user.id
         

    if not check:
        await message.answer(
            "⛔ Доступ запрещён"
        )
        return


    await message.answer(
        "🔐 Админ-панель\n\n"
        "Команды:\n"
        "/stats — статистика\n"
        "/users — пользователи\n"
        "/products — товары"
    )