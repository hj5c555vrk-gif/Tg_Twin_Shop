from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


admin_router = Router()


@admin_router.message(Command("admin"))
async def admin_test(message: Message):

    print("ADMIN COMMAND RECEIVED")

    await message.answer(
        "ADMIN WORKS"
    )